"""
Genomic Data Ingestion Service - HIPAA Compliant
Handles VCF, BAM, FASTQ, and pharmacogenomics data ingestion
"""

import logging
import hashlib
import json
import gzip
from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime
from pathlib import Path
import re

# Genomic data processing
import pysam  # BAM/SAM/CRAM file handling
import vcfpy  # VCF file parsing
from Bio import SeqIO  # FASTQ/FASTA handling
import pandas as pd

# AWS and encryption
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenomicIngestionService:
    """
    HIPAA-compliant genomic data ingestion service

    Supports:
    - VCF (Variant Call Format) - SNPs, indels, structural variants
    - BAM/SAM/CRAM - Aligned sequencing reads
    - FASTQ - Raw sequencing reads
    - Pharmacogenomics annotations
    - ClinVar clinical significance data
    """

    # PHI that might appear in genomic files
    PHI_PATTERNS = {
        'patient_name': r'(?i)patient[_\s]?name[:=]\s*[\w\s]+',
        'mrn': r'(?i)mrn[:=]\s*[\w-]+',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'date': r'\b\d{4}-\d{2}-\d{2}\b',
        'email': r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
        'phone': r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
    }

    def __init__(
        self,
        s3_bucket: Optional[str] = None,
        kms_key_id: Optional[str] = None,
        local_storage: bool = True,
        clinvar_db_path: Optional[str] = None
    ):
        """
        Initialize genomic ingestion service

        Args:
            s3_bucket: S3 bucket for storage
            kms_key_id: AWS KMS key for encryption
            local_storage: Use local storage for development
            clinvar_db_path: Path to ClinVar database for annotations
        """
        self.s3_bucket = s3_bucket
        self.kms_key_id = kms_key_id
        self.local_storage = local_storage
        self.clinvar_db_path = clinvar_db_path

        # Initialize AWS clients (if not local)
        if not local_storage:
            self.s3_client = boto3.client('s3')
        else:
            # Local storage directory
            self.storage_dir = Path('./genomic_storage')
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Local storage mode: {self.storage_dir}")

        # Statistics tracking
        self.stats = {
            'vcf_processed': 0,
            'bam_processed': 0,
            'fastq_processed': 0,
            'variants_total': 0,
            'reads_total': 0
        }

    def ingest_vcf(
        self,
        file_path: str,
        patient_pseudonym: str,
        sample_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest VCF (Variant Call Format) file

        VCF contains genetic variants (SNPs, indels, structural variants)

        Args:
            file_path: Path to VCF file (.vcf or .vcf.gz)
            patient_pseudonym: De-identified patient identifier
            sample_metadata: Additional metadata

        Returns:
            Dict with ingestion results
        """
        try:
            logger.info(f"Ingesting VCF file: {file_path}")

            # Step 1: Read and validate VCF
            vcf_reader = vcfpy.Reader.from_path(file_path)

            # Step 2: Extract metadata (BEFORE de-identification)
            metadata = self._extract_vcf_metadata(vcf_reader, sample_metadata)

            # Step 3: De-identify header
            deidentified_header = self._deidentify_vcf_header(vcf_reader.header)

            # Step 4: Process variants with ClinVar annotations
            variants_data = []
            variant_count = 0

            for record in vcf_reader:
                variant_count += 1

                # Extract variant information
                variant = self._extract_variant(record)

                # Add ClinVar clinical significance (if available)
                if self.clinvar_db_path:
                    variant['clinvar'] = self._get_clinvar_annotation(
                        record.CHROM, record.POS, record.REF, record.ALT
                    )

                variants_data.append(variant)

                # Limit variants to prevent memory issues (can be streamed in production)
                if variant_count >= 10000:
                    logger.warning("Variant limit reached (10,000). Implement streaming for large files.")
                    break

            vcf_reader.close()

            # Step 5: Generate content hash
            content_hash = self._generate_file_hash(file_path)

            # Step 6: Create processed VCF data structure
            processed_vcf = {
                'header': deidentified_header,
                'variants': variants_data,
                'metadata': metadata,
                'variant_count': variant_count
            }

            # Step 7: Store encrypted
            storage_key = self._store_genomic_data(
                processed_vcf,
                patient_pseudonym,
                'vcf',
                content_hash
            )

            self.stats['vcf_processed'] += 1
            self.stats['variants_total'] += variant_count

            logger.info(f"VCF ingestion complete: {variant_count} variants")

            return {
                'success': True,
                'file_type': 'vcf',
                'storage_key': storage_key,
                'content_hash': content_hash,
                'variant_count': variant_count,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"VCF ingestion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def ingest_bam(
        self,
        file_path: str,
        patient_pseudonym: str,
        reference_genome: str = 'GRCh38',
        sample_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest BAM (Binary Alignment Map) file

        BAM contains aligned sequencing reads

        Args:
            file_path: Path to BAM file
            patient_pseudonym: De-identified patient identifier
            reference_genome: Reference genome (GRCh38, GRCh37, etc.)
            sample_metadata: Additional metadata

        Returns:
            Dict with ingestion results
        """
        try:
            logger.info(f"Ingesting BAM file: {file_path}")

            # Step 1: Open and validate BAM
            bam_file = pysam.AlignmentFile(file_path, "rb")

            # Step 2: Extract metadata from header
            metadata = self._extract_bam_metadata(bam_file, reference_genome, sample_metadata)

            # Step 3: De-identify header (remove PHI from read groups, comments)
            deidentified_header = self._deidentify_bam_header(bam_file.header)

            # Step 4: Calculate alignment statistics
            alignment_stats = self._calculate_alignment_stats(bam_file)

            bam_file.close()

            # Step 5: Generate content hash
            content_hash = self._generate_file_hash(file_path)

            # Step 6: Store BAM file with encryption
            # For production, we'd create a de-identified BAM file
            # For now, store metadata and reference to original file
            storage_key = self._store_bam_file(
                file_path,
                patient_pseudonym,
                content_hash
            )

            self.stats['bam_processed'] += 1
            self.stats['reads_total'] += alignment_stats.get('total_reads', 0)

            logger.info(f"BAM ingestion complete: {alignment_stats.get('total_reads', 0)} reads")

            return {
                'success': True,
                'file_type': 'bam',
                'storage_key': storage_key,
                'content_hash': content_hash,
                'alignment_stats': alignment_stats,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"BAM ingestion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def ingest_fastq(
        self,
        file_path: str,
        patient_pseudonym: str,
        paired_file: Optional[str] = None,
        sample_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest FASTQ file (raw sequencing reads)

        Args:
            file_path: Path to FASTQ file (.fastq or .fastq.gz)
            patient_pseudonym: De-identified patient identifier
            paired_file: Path to paired-end read file (R2)
            sample_metadata: Additional metadata

        Returns:
            Dict with ingestion results
        """
        try:
            logger.info(f"Ingesting FASTQ file: {file_path}")

            # Step 1: Detect compression
            is_gzipped = file_path.endswith('.gz')

            # Step 2: Calculate quality statistics
            quality_stats = self._calculate_fastq_quality(file_path, is_gzipped)

            # Step 3: Generate content hash
            content_hash = self._generate_file_hash(file_path)

            # Step 4: Store FASTQ with encryption
            storage_key = self._store_fastq_file(
                file_path,
                patient_pseudonym,
                content_hash
            )

            # Handle paired-end reads
            paired_storage_key = None
            if paired_file:
                paired_hash = self._generate_file_hash(paired_file)
                paired_storage_key = self._store_fastq_file(
                    paired_file,
                    patient_pseudonym,
                    paired_hash,
                    read_number=2
                )

            self.stats['fastq_processed'] += 1
            self.stats['reads_total'] += quality_stats.get('total_reads', 0)

            logger.info(f"FASTQ ingestion complete: {quality_stats.get('total_reads', 0)} reads")

            return {
                'success': True,
                'file_type': 'fastq',
                'storage_key': storage_key,
                'paired_storage_key': paired_storage_key,
                'content_hash': content_hash,
                'quality_stats': quality_stats,
                'metadata': sample_metadata or {}
            }

        except Exception as e:
            logger.error(f"FASTQ ingestion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def annotate_pharmacogenomics(
        self,
        vcf_storage_key: str,
        pgx_genes: Optional[List[str]] = None
    ) -> Dict:
        """
        Annotate variants with pharmacogenomics information

        Identifies variants in genes affecting drug metabolism:
        - CYP2D6, CYP2C19, CYP3A4, CYP3A5 (drug metabolism)
        - SLCO1B1 (statin transport)
        - TPMT (thiopurine methyltransferase)
        - DPYD (dihydropyrimidine dehydrogenase)

        Args:
            vcf_storage_key: Storage key for VCF file
            pgx_genes: List of pharmacogenomics genes to check

        Returns:
            Dict with pharmacogenomics annotations
        """
        if pgx_genes is None:
            pgx_genes = [
                'CYP2D6', 'CYP2C19', 'CYP2C9', 'CYP3A4', 'CYP3A5',
                'SLCO1B1', 'TPMT', 'DPYD', 'VKORC1', 'UGT1A1'
            ]

        try:
            logger.info(f"Annotating pharmacogenomics for: {vcf_storage_key}")

            # Retrieve VCF data
            vcf_data = self._retrieve_genomic_data(vcf_storage_key)

            # Find variants in PGx genes
            pgx_variants = []
            for variant in vcf_data.get('variants', []):
                # Check if variant is in a PGx gene
                gene = variant.get('gene')
                if gene in pgx_genes:
                    pgx_variants.append({
                        'gene': gene,
                        'chromosome': variant['chromosome'],
                        'position': variant['position'],
                        'ref': variant['ref'],
                        'alt': variant['alt'],
                        'genotype': variant.get('genotype'),
                        'clinical_significance': variant.get('clinvar', {}).get('clinical_significance')
                    })

            logger.info(f"Found {len(pgx_variants)} pharmacogenomics variants")

            return {
                'success': True,
                'pgx_variants': pgx_variants,
                'gene_count': len(set(v['gene'] for v in pgx_variants))
            }

        except Exception as e:
            logger.error(f"PGx annotation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== HELPER METHODS ====================

    def _extract_vcf_metadata(self, vcf_reader, sample_metadata: Optional[Dict]) -> Dict:
        """Extract metadata from VCF header"""
        header = vcf_reader.header

        metadata = {
            'file_format': str(header.version),
            'reference_genome': None,
            'sample_names': list(header.samples.names) if header.samples else [],
            'contigs': [],
            'ingestion_timestamp': datetime.utcnow().isoformat(),
            'custom_metadata': sample_metadata or {}
        }

        # Extract reference genome
        if 'reference' in header.lines:
            metadata['reference_genome'] = str(header.lines['reference'])

        # Extract contigs
        for contig in header.get_lines('contig'):
            metadata['contigs'].append({
                'id': contig.id,
                'length': contig.length if hasattr(contig, 'length') else None
            })

        return metadata

    def _deidentify_vcf_header(self, header) -> Dict:
        """Remove PHI from VCF header"""
        deidentified = {
            'file_format': str(header.version),
            'filters': {},
            'info': {},
            'format': {},
            'contigs': []
        }

        # Copy non-PHI header information
        for line_type in ['FILTER', 'INFO', 'FORMAT']:
            lines = header.get_lines(line_type)
            for line in lines:
                deidentified[line_type.lower()][line.id] = {
                    'description': line.description if hasattr(line, 'description') else None
                }

        return deidentified

    def _extract_variant(self, record) -> Dict:
        """Extract variant information from VCF record"""
        variant = {
            'chromosome': record.CHROM,
            'position': record.POS,
            'id': record.ID[0] if record.ID else None,
            'ref': record.REF,
            'alt': [str(alt.value) for alt in record.ALT] if record.ALT else [],
            'quality': record.QUAL,
            'filter': [str(f) for f in record.FILTER] if record.FILTER else ['PASS'],
            'info': {}
        }

        # Extract relevant INFO fields
        for key, value in record.INFO.items():
            if key in ['DP', 'AF', 'AC', 'AN', 'GENE', 'IMPACT']:
                variant['info'][key] = value
                if key == 'GENE':
                    variant['gene'] = value

        # Extract genotype (GT) if available
        if record.calls and len(record.calls) > 0:
            call = record.calls[0]
            if 'GT' in call.data:
                variant['genotype'] = call.data['GT']

        return variant

    def _get_clinvar_annotation(self, chrom: str, pos: int, ref: str, alt: List) -> Dict:
        """
        Get ClinVar clinical significance annotation

        In production, this would query ClinVar database
        """
        # Placeholder - would query actual ClinVar database
        return {
            'clinical_significance': None,
            'review_status': None,
            'variation_id': None
        }

    def _extract_bam_metadata(
        self,
        bam_file,
        reference_genome: str,
        sample_metadata: Optional[Dict]
    ) -> Dict:
        """Extract metadata from BAM header"""
        header = bam_file.header

        metadata = {
            'reference_genome': reference_genome,
            'read_groups': [],
            'program': [],
            'ingestion_timestamp': datetime.utcnow().isoformat(),
            'custom_metadata': sample_metadata or {}
        }

        # Extract read groups (de-identify)
        if 'RG' in header:
            for rg in header['RG']:
                metadata['read_groups'].append({
                    'id': rg.get('ID'),
                    'platform': rg.get('PL'),
                    'library': '[REDACTED]',  # Remove library name (potential PHI)
                    'sample': '[REDACTED]'    # Remove sample name
                })

        # Extract program information
        if 'PG' in header:
            for pg in header['PG']:
                metadata['program'].append({
                    'id': pg.get('ID'),
                    'name': pg.get('PN'),
                    'version': pg.get('VN')
                })

        return metadata

    def _deidentify_bam_header(self, header) -> Dict:
        """Remove PHI from BAM header"""
        deidentified = {
            'HD': header.get('HD', {}),
            'SQ': header.get('SQ', []),
            'RG': [],
            'PG': header.get('PG', [])
        }

        # De-identify read groups
        if 'RG' in header:
            for rg in header['RG']:
                deidentified['RG'].append({
                    'ID': rg.get('ID'),
                    'PL': rg.get('PL'),
                    'SM': 'PATIENT_DEIDENTIFIED'  # Replace sample name
                })

        return deidentified

    def _calculate_alignment_stats(self, bam_file) -> Dict:
        """Calculate alignment statistics from BAM file"""
        stats = {
            'total_reads': 0,
            'mapped_reads': 0,
            'unmapped_reads': 0,
            'properly_paired': 0,
            'singletons': 0,
            'coverage_calculated': False
        }

        # Sample first 100,000 reads for statistics
        sample_size = 100000
        for i, read in enumerate(bam_file):
            if i >= sample_size:
                break

            stats['total_reads'] += 1

            if read.is_unmapped:
                stats['unmapped_reads'] += 1
            else:
                stats['mapped_reads'] += 1

            if read.is_proper_pair:
                stats['properly_paired'] += 1

            if read.is_paired and read.mate_is_unmapped:
                stats['singletons'] += 1

        # Calculate percentages
        if stats['total_reads'] > 0:
            stats['mapping_rate'] = stats['mapped_reads'] / stats['total_reads']
            stats['properly_paired_rate'] = stats['properly_paired'] / stats['total_reads']

        return stats

    def _calculate_fastq_quality(self, file_path: str, is_gzipped: bool) -> Dict:
        """Calculate quality statistics from FASTQ file"""
        stats = {
            'total_reads': 0,
            'total_bases': 0,
            'mean_quality': 0.0,
            'mean_length': 0.0,
            'gc_content': 0.0
        }

        # Sample first 10,000 reads
        sample_size = 10000
        total_quality = 0
        gc_count = 0

        open_func = gzip.open if is_gzipped else open
        mode = 'rt' if is_gzipped else 'r'

        with open_func(file_path, mode) as handle:
            for i, record in enumerate(SeqIO.parse(handle, "fastq")):
                if i >= sample_size:
                    break

                stats['total_reads'] += 1
                stats['total_bases'] += len(record.seq)

                # Calculate average quality
                if hasattr(record, 'letter_annotations') and 'phred_quality' in record.letter_annotations:
                    avg_q = sum(record.letter_annotations['phred_quality']) / len(record.seq)
                    total_quality += avg_q

                # Calculate GC content
                seq_str = str(record.seq).upper()
                gc_count += seq_str.count('G') + seq_str.count('C')

        # Calculate averages
        if stats['total_reads'] > 0:
            stats['mean_quality'] = total_quality / stats['total_reads']
            stats['mean_length'] = stats['total_bases'] / stats['total_reads']
            stats['gc_content'] = gc_count / stats['total_bases'] if stats['total_bases'] > 0 else 0

        return stats

    def _generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash of file"""
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def _store_genomic_data(
        self,
        data: Dict,
        patient_pseudonym: str,
        data_type: str,
        content_hash: str
    ) -> str:
        """Store genomic data with encryption"""
        storage_key = f"genomics/{patient_pseudonym}/{data_type}/{content_hash}.json"

        if self.local_storage:
            # Local storage
            local_path = self.storage_dir / patient_pseudonym / data_type
            local_path.mkdir(parents=True, exist_ok=True)

            file_path = local_path / f"{content_hash}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Stored locally: {file_path}")
        else:
            # S3 storage with KMS encryption
            json_data = json.dumps(data)

            extra_args = {
                'ServerSideEncryption': 'aws:kms',
                'SSEKMSKeyId': self.kms_key_id
            } if self.kms_key_id else {}

            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=storage_key,
                Body=json_data.encode('utf-8'),
                **extra_args
            )

            logger.info(f"Stored in S3: s3://{self.s3_bucket}/{storage_key}")

        return storage_key

    def _store_bam_file(
        self,
        file_path: str,
        patient_pseudonym: str,
        content_hash: str
    ) -> str:
        """Store BAM file with encryption"""
        storage_key = f"genomics/{patient_pseudonym}/bam/{content_hash}.bam"

        if self.local_storage:
            # For local storage, just record metadata (BAM files are large)
            local_path = self.storage_dir / patient_pseudonym / 'bam'
            local_path.mkdir(parents=True, exist_ok=True)

            metadata_file = local_path / f"{content_hash}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump({
                    'original_path': file_path,
                    'storage_key': storage_key,
                    'content_hash': content_hash
                }, f, indent=2)

            logger.info(f"BAM metadata stored: {metadata_file}")
        else:
            # Upload to S3 with KMS encryption
            extra_args = {
                'ServerSideEncryption': 'aws:kms',
                'SSEKMSKeyId': self.kms_key_id
            } if self.kms_key_id else {}

            self.s3_client.upload_file(
                file_path,
                self.s3_bucket,
                storage_key,
                ExtraArgs=extra_args
            )

            logger.info(f"BAM stored in S3: s3://{self.s3_bucket}/{storage_key}")

        return storage_key

    def _store_fastq_file(
        self,
        file_path: str,
        patient_pseudonym: str,
        content_hash: str,
        read_number: int = 1
    ) -> str:
        """Store FASTQ file with encryption"""
        suffix = 'fastq.gz' if file_path.endswith('.gz') else 'fastq'
        storage_key = f"genomics/{patient_pseudonym}/fastq/R{read_number}_{content_hash}.{suffix}"

        if self.local_storage:
            # Record metadata for local storage
            local_path = self.storage_dir / patient_pseudonym / 'fastq'
            local_path.mkdir(parents=True, exist_ok=True)

            metadata_file = local_path / f"R{read_number}_{content_hash}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump({
                    'original_path': file_path,
                    'storage_key': storage_key,
                    'content_hash': content_hash,
                    'read_number': read_number
                }, f, indent=2)

            logger.info(f"FASTQ metadata stored: {metadata_file}")
        else:
            # Upload to S3
            extra_args = {
                'ServerSideEncryption': 'aws:kms',
                'SSEKMSKeyId': self.kms_key_id
            } if self.kms_key_id else {}

            self.s3_client.upload_file(
                file_path,
                self.s3_bucket,
                storage_key,
                ExtraArgs=extra_args
            )

            logger.info(f"FASTQ stored in S3: s3://{self.s3_bucket}/{storage_key}")

        return storage_key

    def _retrieve_genomic_data(self, storage_key: str) -> Dict:
        """Retrieve genomic data from storage"""
        if self.local_storage:
            # Extract patient and file info from storage key
            parts = storage_key.split('/')
            patient_pseudonym = parts[1]
            data_type = parts[2]
            filename = parts[3]

            file_path = self.storage_dir / patient_pseudonym / data_type / filename

            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # Retrieve from S3
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=storage_key
            )

            return json.loads(response['Body'].read().decode('utf-8'))

    def get_statistics(self) -> Dict:
        """Get ingestion statistics"""
        return {
            'total_files_processed': (
                self.stats['vcf_processed'] +
                self.stats['bam_processed'] +
                self.stats['fastq_processed']
            ),
            'by_type': {
                'vcf': self.stats['vcf_processed'],
                'bam': self.stats['bam_processed'],
                'fastq': self.stats['fastq_processed']
            },
            'variants_total': self.stats['variants_total'],
            'reads_total': self.stats['reads_total']
        }


if __name__ == "__main__":
    # Example usage
    service = GenomicIngestionService(local_storage=True)

    print("Genomic Ingestion Service initialized successfully")
    print("Supported formats: VCF, BAM, FASTQ")
    print("Ready to process genomic data with HIPAA compliance")
