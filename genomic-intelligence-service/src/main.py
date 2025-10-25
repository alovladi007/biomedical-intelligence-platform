"""
Genomic Intelligence Service - FastAPI Application
Provides REST API for variant annotation and pharmacogenomics predictions
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn
import logging
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from variant_annotator import VariantAnnotator
from pharmacogenomics import PharmacogenomicsPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Genomic Intelligence Service",
    description="AI-powered variant annotation and pharmacogenomics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
annotator = VariantAnnotator()
pgx_predictor = PharmacogenomicsPredictor()

# Pydantic models
class VariantAnnotationRequest(BaseModel):
    chromosome: str = Field(..., description="Chromosome (e.g., 'chr1', '1')")
    position: int = Field(..., description="Genomic position (1-based)")
    ref: str = Field(..., description="Reference allele")
    alt: str = Field(..., description="Alternate allele")
    gene: Optional[str] = Field(None, description="Gene symbol")

class DrugResponseRequest(BaseModel):
    gene: str = Field(..., description="Gene name (CYP2D6, CYP2C19, TPMT, DPYD)")
    phenotype: str = Field(..., description="Phenotype (poor_metabolizer, normal_metabolizer, etc.)")
    drug: str = Field(..., description="Drug name")

class WarfarinDoseRequest(BaseModel):
    cyp2c9_genotype: str = Field(..., description="CYP2C9 genotype (e.g., '*1/*1')")
    vkorc1_genotype: str = Field(..., description="VKORC1 genotype (e.g., 'GG')")
    age: Optional[int] = Field(None, description="Patient age")
    weight: Optional[float] = Field(None, description="Patient weight (kg)")

class GenotypesRequest(BaseModel):
    genotypes: Dict[str, str] = Field(..., description="Dictionary of gene: phenotype pairs")

@app.get("/")
async def root():
    return {
        "service": "Genomic Intelligence",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": ["/health", "/annotate/variant", "/pharmacogenomics/predict", "/docs"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Genomic Intelligence",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/annotate/variant")
async def annotate_variant(request: VariantAnnotationRequest):
    """Annotate a single genetic variant"""
    try:
        result = annotator.annotate_variant(
            chromosome=request.chromosome,
            position=request.position,
            ref=request.ref,
            alt=request.alt,
            gene=request.gene
        )
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Variant annotation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/annotate/vcf")
async def annotate_vcf(file: UploadFile = File(...), max_variants: int = 1000):
    """Annotate all variants in a VCF file"""
    try:
        if not file.filename.endswith('.vcf') and not file.filename.endswith('.vcf.gz'):
            raise HTTPException(status_code=400, detail="File must be VCF format (.vcf or .vcf.gz)")

        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.vcf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = annotator.annotate_vcf(tmp_path, max_variants=max_variants)

        # Cleanup
        import os
        os.unlink(tmp_path)

        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"VCF annotation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pharmacogenomics/genes")
async def list_pharmacogenes():
    """List all pharmacogenes"""
    genes = annotator.list_pharmacogenes()
    return {"pharmacogenes": genes, "count": len(genes)}

@app.post("/pharmacogenomics/predict")
async def predict_drug_response(request: DrugResponseRequest):
    """Predict drug response based on genotype"""
    try:
        result = pgx_predictor.predict_drug_response(
            gene=request.gene,
            phenotype=request.phenotype,
            drug=request.drug
        )
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drug response prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pharmacogenomics/warfarin-dose")
async def calculate_warfarin_dose(request: WarfarinDoseRequest):
    """Calculate personalized warfarin dose"""
    try:
        result = pgx_predictor.calculate_warfarin_dose(
            cyp2c9_genotype=request.cyp2c9_genotype,
            vkorc1_genotype=request.vkorc1_genotype,
            age=request.age,
            weight=request.weight
        )
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Warfarin dosing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pharmacogenomics/all-interactions")
async def get_all_interactions(request: GenotypesRequest):
    """Get all drug-gene interactions for patient genotypes"""
    try:
        recommendations = pgx_predictor.get_all_drug_interactions(request.genotypes)
        return {
            "total_interactions": len(recommendations),
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"All interactions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Genomic Intelligence Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=5007, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    logger.info(f"Starting Genomic Intelligence Service on {args.host}:{args.port}")
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload, log_level="info")
