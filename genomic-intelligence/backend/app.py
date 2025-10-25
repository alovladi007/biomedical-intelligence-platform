from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# Mock data for genomic analyses
GENOMIC_ANALYSES = [
    {
        "id": "GEN-2025-001",
        "patientId": "PT-45892",
        "patientName": "Sarah Johnson",
        "analysisType": "Whole Genome Sequencing",
        "status": "completed",
        "submittedDate": "2025-01-15",
        "completedDate": "2025-01-20",
        "variants": 4523,
        "clinicalVariants": 12,
        "pathogenicVariants": 3,
        "pharmacogenomics": True,
        "findings": ["BRCA1 pathogenic variant detected", "CYP2C19 poor metabolizer"],
        "riskScore": 0.75
    },
    {
        "id": "GEN-2025-002",
        "patientId": "PT-67234",
        "patientName": "Michael Chen",
        "analysisType": "Exome Sequencing",
        "status": "processing",
        "submittedDate": "2025-01-22",
        "completedDate": None,
        "variants": 2341,
        "clinicalVariants": 8,
        "pathogenicVariants": 1,
        "pharmacogenomics": True,
        "findings": ["Analysis in progress"],
        "riskScore": 0.45
    },
    {
        "id": "GEN-2025-003",
        "patientId": "PT-89123",
        "patientName": "Emily Rodriguez",
        "analysisType": "RNA Sequencing",
        "status": "completed",
        "submittedDate": "2025-01-18",
        "completedDate": "2025-01-21",
        "variants": 1892,
        "clinicalVariants": 5,
        "pathogenicVariants": 0,
        "pharmacogenomics": False,
        "findings": ["No pathogenic variants detected", "Normal expression patterns"],
        "riskScore": 0.15
    },
    {
        "id": "GEN-2025-004",
        "patientId": "PT-23456",
        "patientName": "David Williams",
        "analysisType": "Pharmacogenomics Panel",
        "status": "completed",
        "submittedDate": "2025-01-19",
        "completedDate": "2025-01-21",
        "variants": 234,
        "clinicalVariants": 15,
        "pathogenicVariants": 0,
        "pharmacogenomics": True,
        "findings": ["CYP2D6 intermediate metabolizer", "TPMT normal activity"],
        "riskScore": 0.30
    },
    {
        "id": "GEN-2025-005",
        "patientId": "PT-78901",
        "patientName": "Lisa Martinez",
        "analysisType": "Cancer Genomics Panel",
        "status": "completed",
        "submittedDate": "2025-01-17",
        "completedDate": "2025-01-22",
        "variants": 3456,
        "clinicalVariants": 18,
        "pathogenicVariants": 5,
        "pharmacogenomics": True,
        "findings": ["TP53 pathogenic mutation", "EGFR targetable mutation", "TMB: 12 mutations/Mb"],
        "riskScore": 0.85
    }
]

VARIANTS = [
    {
        "id": "VAR-001",
        "gene": "BRCA1",
        "chromosome": "17",
        "position": "43044295",
        "refAllele": "G",
        "altAllele": "A",
        "variantType": "SNV",
        "consequence": "Missense",
        "pathogenicity": "Pathogenic",
        "clinicalSignificance": "High",
        "alleleFrequency": 0.0001,
        "dbSNP": "rs80357906",
        "diseases": ["Breast cancer", "Ovarian cancer"],
        "evidence": "Multiple studies confirm pathogenicity"
    },
    {
        "id": "VAR-002",
        "gene": "CYP2C19",
        "chromosome": "10",
        "position": "94781859",
        "refAllele": "C",
        "altAllele": "T",
        "variantType": "SNV",
        "consequence": "Splice site",
        "pathogenicity": "Likely Pathogenic",
        "clinicalSignificance": "Moderate",
        "alleleFrequency": 0.12,
        "dbSNP": "rs4244285",
        "diseases": ["Poor drug metabolism"],
        "evidence": "PharmGKB Level 1A evidence"
    },
    {
        "id": "VAR-003",
        "gene": "TP53",
        "chromosome": "17",
        "position": "7577538",
        "refAllele": "C",
        "altAllele": "T",
        "variantType": "SNV",
        "consequence": "Nonsense",
        "pathogenicity": "Pathogenic",
        "clinicalSignificance": "High",
        "alleleFrequency": 0.00005,
        "dbSNP": "rs28934576",
        "diseases": ["Li-Fraumeni syndrome", "Multiple cancers"],
        "evidence": "Well-established pathogenic variant"
    },
    {
        "id": "VAR-004",
        "gene": "CFTR",
        "chromosome": "7",
        "position": "117559590",
        "refAllele": "CTT",
        "altAllele": "C",
        "variantType": "Deletion",
        "consequence": "Frameshift",
        "pathogenicity": "Pathogenic",
        "clinicalSignificance": "High",
        "alleleFrequency": 0.02,
        "dbSNP": "rs113993960",
        "diseases": ["Cystic fibrosis"],
        "evidence": "Common CF mutation (F508del)"
    }
]

DRUG_RESPONSES = [
    {
        "id": "PGX-001",
        "patientId": "PT-45892",
        "drug": "Clopidogrel",
        "gene": "CYP2C19",
        "genotype": "*2/*2",
        "phenotype": "Poor Metabolizer",
        "recommendation": "Alternative medication recommended",
        "evidence": "Level 1A",
        "alternativeDrugs": ["Prasugrel", "Ticagrelor"],
        "dosageAdjustment": "N/A - avoid use"
    },
    {
        "id": "PGX-002",
        "patientId": "PT-45892",
        "drug": "Warfarin",
        "gene": "CYP2C9",
        "genotype": "*1/*3",
        "phenotype": "Intermediate Metabolizer",
        "recommendation": "Reduced initial dose, frequent INR monitoring",
        "evidence": "Level 1A",
        "alternativeDrugs": ["DOACs (Apixaban, Rivaroxaban)"],
        "dosageAdjustment": "25-50% dose reduction"
    },
    {
        "id": "PGX-003",
        "patientId": "PT-23456",
        "drug": "Codeine",
        "gene": "CYP2D6",
        "genotype": "*1/*4",
        "phenotype": "Intermediate Metabolizer",
        "recommendation": "Standard dosing with monitoring",
        "evidence": "Level 1A",
        "alternativeDrugs": ["Morphine", "Hydromorphone"],
        "dosageAdjustment": "Standard dose, monitor response"
    }
]

POPULATION_STUDIES = [
    {
        "id": "POP-001",
        "studyName": "GWAS: Cardiovascular Disease Risk",
        "population": "European",
        "sampleSize": 125000,
        "significantLoci": 47,
        "status": "completed",
        "startDate": "2024-06-01",
        "endDate": "2025-01-15",
        "findings": "Identified 12 novel risk loci for coronary artery disease",
        "pValue": 5e-8,
        "heritability": 0.42
    },
    {
        "id": "POP-002",
        "studyName": "Rare Disease Cohort Analysis",
        "population": "Global",
        "sampleSize": 8500,
        "significantLoci": 23,
        "status": "ongoing",
        "startDate": "2024-09-01",
        "endDate": None,
        "findings": "Preliminary results show promising candidate genes",
        "pValue": 1e-6,
        "heritability": 0.68
    }
]

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "genomic-intelligence",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/analyses', methods=['GET'])
def get_analyses():
    return jsonify({
        "analyses": GENOMIC_ANALYSES,
        "total": len(GENOMIC_ANALYSES)
    })

@app.route('/api/v1/analyses/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    analysis = next((a for a in GENOMIC_ANALYSES if a['id'] == analysis_id), None)
    if analysis:
        return jsonify(analysis)
    return jsonify({"error": "Analysis not found"}), 404

@app.route('/api/v1/variants', methods=['GET'])
def get_variants():
    return jsonify({
        "variants": VARIANTS,
        "total": len(VARIANTS)
    })

@app.route('/api/v1/variants/<variant_id>', methods=['GET'])
def get_variant(variant_id):
    variant = next((v for v in VARIANTS if v['id'] == variant_id), None)
    if variant:
        return jsonify(variant)
    return jsonify({"error": "Variant not found"}), 404

@app.route('/api/v1/pharmacogenomics', methods=['GET'])
def get_pharmacogenomics():
    patient_id = request.args.get('patientId')
    if patient_id:
        responses = [r for r in DRUG_RESPONSES if r['patientId'] == patient_id]
        return jsonify({
            "drugResponses": responses,
            "total": len(responses)
        })
    return jsonify({
        "drugResponses": DRUG_RESPONSES,
        "total": len(DRUG_RESPONSES)
    })

@app.route('/api/v1/population-studies', methods=['GET'])
def get_population_studies():
    return jsonify({
        "studies": POPULATION_STUDIES,
        "total": len(POPULATION_STUDIES)
    })

@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    return jsonify({
        "totalAnalyses": len(GENOMIC_ANALYSES),
        "completedAnalyses": len([a for a in GENOMIC_ANALYSES if a['status'] == 'completed']),
        "processingAnalyses": len([a for a in GENOMIC_ANALYSES if a['status'] == 'processing']),
        "totalVariants": sum(a['variants'] for a in GENOMIC_ANALYSES),
        "pathogenicVariants": sum(a['pathogenicVariants'] for a in GENOMIC_ANALYSES),
        "pharmacogenomicsTests": len([a for a in GENOMIC_ANALYSES if a['pharmacogenomics']]),
        "avgProcessingTime": "5.2 days"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5007)
