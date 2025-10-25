from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# Mock data for drug discovery projects
DRUG_PROJECTS = [
    {
        "id": "DRUG-2025-001",
        "projectName": "Alzheimer's Disease Therapeutic",
        "targetProtein": "Beta-Amyloid",
        "stage": "Lead Optimization",
        "startDate": "2024-03-15",
        "leadCompounds": 12,
        "status": "active",
        "probability": 0.68,
        "estimatedCost": "$45M",
        "team": "Neuroscience Division",
        "indication": "Alzheimer's Disease",
        "predictedEfficacy": 0.72,
        "toxicityScore": 0.15
    },
    {
        "id": "DRUG-2025-002",
        "projectName": "Cancer Immunotherapy",
        "targetProtein": "PD-L1",
        "stage": "Clinical Trial Phase II",
        "startDate": "2023-08-20",
        "leadCompounds": 3,
        "status": "active",
        "probability": 0.82,
        "estimatedCost": "$120M",
        "team": "Oncology Division",
        "indication": "Non-Small Cell Lung Cancer",
        "predictedEfficacy": 0.85,
        "toxicityScore": 0.22
    },
    {
        "id": "DRUG-2025-003",
        "projectName": "Diabetes Management",
        "targetProtein": "GLP-1 Receptor",
        "stage": "Preclinical",
        "startDate": "2024-11-01",
        "leadCompounds": 45,
        "status": "active",
        "probability": 0.45,
        "estimatedCost": "$28M",
        "team": "Metabolic Disorders",
        "indication": "Type 2 Diabetes",
        "predictedEfficacy": 0.65,
        "toxicityScore": 0.10
    },
    {
        "id": "DRUG-2025-004",
        "projectName": "Cardiovascular Protection",
        "targetProtein": "PCSK9",
        "stage": "Lead Discovery",
        "startDate": "2024-09-12",
        "leadCompounds": 67,
        "status": "active",
        "probability": 0.52,
        "estimatedCost": "$35M",
        "team": "Cardiovascular Research",
        "indication": "Hypercholesterolemia",
        "predictedEfficacy": 0.78,
        "toxicityScore": 0.08
    },
    {
        "id": "DRUG-2025-005",
        "projectName": "Rare Disease Therapy",
        "targetProtein": "CFTR",
        "stage": "Clinical Trial Phase I",
        "startDate": "2024-05-30",
        "leadCompounds": 5,
        "status": "active",
        "probability": 0.58,
        "estimatedCost": "$89M",
        "team": "Rare Disease Unit",
        "indication": "Cystic Fibrosis",
        "predictedEfficacy": 0.70,
        "toxicityScore": 0.18
    }
]

MOLECULES = [
    {
        "id": "MOL-001",
        "projectId": "DRUG-2025-001",
        "compoundId": "BM-4523",
        "smiles": "CC(C)NCC(COc1ccccc1CCN)O",
        "molecularWeight": 324.42,
        "logP": 2.45,
        "hDonors": 3,
        "hAcceptors": 4,
        "bbbPermeability": "High",
        "admetScore": 0.82,
        "synthesisScore": 0.75,
        "bindingAffinity": -8.5,
        "toxicityPrediction": "Low",
        "drugLikeness": 0.88,
        "status": "Lead Compound"
    },
    {
        "id": "MOL-002",
        "projectId": "DRUG-2025-002",
        "compoundId": "ONC-7891",
        "smiles": "CN1CCN(CC1)c2ccc(NC(=O)c3ccc(C)c(Nc4nccc(c5cccnc5)n4)c3)cc2",
        "molecularWeight": 456.58,
        "logP": 3.12,
        "hDonors": 2,
        "hAcceptors": 5,
        "bbbPermeability": "Low",
        "admetScore": 0.78,
        "synthesisScore": 0.65,
        "bindingAffinity": -9.2,
        "toxicityPrediction": "Low",
        "drugLikeness": 0.85,
        "status": "Clinical Candidate"
    },
    {
        "id": "MOL-003",
        "projectId": "DRUG-2025-003",
        "compoundId": "DM-2341",
        "smiles": "CC(C)(C)c1ccc(cc1)C(=O)NC2CCC(CC2)n3c(=O)c4c([nH]c3=O)CCCC4",
        "molecularWeight": 398.52,
        "logP": 4.23,
        "hDonors": 2,
        "hAcceptors": 4,
        "bbbPermeability": "Medium",
        "admetScore": 0.72,
        "synthesisScore": 0.68,
        "bindingAffinity": -7.8,
        "toxicityPrediction": "Very Low",
        "drugLikeness": 0.82,
        "status": "Hit Compound"
    }
]

CLINICAL_TRIALS = [
    {
        "id": "CT-2025-001",
        "projectId": "DRUG-2025-002",
        "nctId": "NCT05234567",
        "title": "Phase II Study of ONC-7891 in NSCLC",
        "phase": "Phase II",
        "status": "Recruiting",
        "enrollment": 240,
        "enrolled": 167,
        "sites": 18,
        "startDate": "2024-06-01",
        "estimatedCompletion": "2026-12-31",
        "primaryEndpoint": "Overall Response Rate",
        "secondaryEndpoints": ["Progression-Free Survival", "Overall Survival", "Safety"],
        "inclusionCriteria": "Advanced NSCLC, PD-L1 positive",
        "adverseEvents": 23,
        "seriousAdverseEvents": 3,
        "dropoutRate": 0.08
    },
    {
        "id": "CT-2025-002",
        "projectId": "DRUG-2025-005",
        "nctId": "NCT05198765",
        "title": "Phase I Safety Study of CFTR Modulator",
        "phase": "Phase I",
        "status": "Active",
        "enrollment": 45,
        "enrolled": 38,
        "sites": 5,
        "startDate": "2024-10-15",
        "estimatedCompletion": "2025-08-30",
        "primaryEndpoint": "Safety and Tolerability",
        "secondaryEndpoints": ["Pharmacokinetics", "CFTR Function"],
        "inclusionCriteria": "Cystic Fibrosis patients age 12+",
        "adverseEvents": 8,
        "seriousAdverseEvents": 0,
        "dropoutRate": 0.04
    }
]

ADVERSE_EVENTS = [
    {
        "id": "AE-001",
        "trialId": "CT-2025-001",
        "event": "Fatigue",
        "severity": "Grade 1",
        "frequency": 45,
        "predicted": True,
        "confidence": 0.82,
        "timeToOnset": "2 weeks",
        "resolution": "Self-limiting"
    },
    {
        "id": "AE-002",
        "trialId": "CT-2025-001",
        "event": "Nausea",
        "severity": "Grade 2",
        "frequency": 28,
        "predicted": True,
        "confidence": 0.75,
        "timeToOnset": "1 week",
        "resolution": "Manageable with antiemetics"
    },
    {
        "id": "AE-003",
        "trialId": "CT-2025-001",
        "event": "Elevated ALT",
        "severity": "Grade 3",
        "frequency": 3,
        "predicted": False,
        "confidence": 0.45,
        "timeToOnset": "4 weeks",
        "resolution": "Dose reduction required"
    }
]

REPURPOSING_CANDIDATES = [
    {
        "id": "REP-001",
        "drugName": "Metformin",
        "currentIndication": "Type 2 Diabetes",
        "proposedIndication": "Cancer Prevention",
        "evidenceScore": 0.78,
        "mechanismSimilarity": 0.82,
        "clinicalEvidence": "Retrospective studies show reduced cancer incidence",
        "estimatedCost": "$5M",
        "timeToMarket": "3-4 years",
        "riskLevel": "Low",
        "publications": 127
    },
    {
        "id": "REP-002",
        "drugName": "Sildenafil",
        "currentIndication": "Erectile Dysfunction",
        "proposedIndication": "Pulmonary Hypertension",
        "evidenceScore": 0.92,
        "mechanismSimilarity": 0.95,
        "clinicalEvidence": "Multiple successful trials completed",
        "estimatedCost": "$15M",
        "timeToMarket": "2-3 years",
        "riskLevel": "Very Low",
        "publications": 234
    },
    {
        "id": "REP-003",
        "drugName": "Thalidomide",
        "currentIndication": "Multiple Myeloma",
        "proposedIndication": "Leprosy",
        "evidenceScore": 0.88,
        "mechanismSimilarity": 0.72,
        "clinicalEvidence": "Strong anti-inflammatory effects demonstrated",
        "estimatedCost": "$8M",
        "timeToMarket": "2-3 years",
        "riskLevel": "Moderate",
        "publications": 89
    }
]

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "drug-discovery-ai",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/projects', methods=['GET'])
def get_projects():
    return jsonify({
        "projects": DRUG_PROJECTS,
        "total": len(DRUG_PROJECTS)
    })

@app.route('/api/v1/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    project = next((p for p in DRUG_PROJECTS if p['id'] == project_id), None)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/v1/molecules', methods=['GET'])
def get_molecules():
    project_id = request.args.get('projectId')
    if project_id:
        molecules = [m for m in MOLECULES if m['projectId'] == project_id]
        return jsonify({
            "molecules": molecules,
            "total": len(molecules)
        })
    return jsonify({
        "molecules": MOLECULES,
        "total": len(MOLECULES)
    })

@app.route('/api/v1/clinical-trials', methods=['GET'])
def get_clinical_trials():
    return jsonify({
        "trials": CLINICAL_TRIALS,
        "total": len(CLINICAL_TRIALS)
    })

@app.route('/api/v1/adverse-events', methods=['GET'])
def get_adverse_events():
    trial_id = request.args.get('trialId')
    if trial_id:
        events = [e for e in ADVERSE_EVENTS if e['trialId'] == trial_id]
        return jsonify({
            "events": events,
            "total": len(events)
        })
    return jsonify({
        "events": ADVERSE_EVENTS,
        "total": len(ADVERSE_EVENTS)
    })

@app.route('/api/v1/repurposing', methods=['GET'])
def get_repurposing():
    return jsonify({
        "candidates": REPURPOSING_CANDIDATES,
        "total": len(REPURPOSING_CANDIDATES)
    })

@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    return jsonify({
        "totalProjects": len(DRUG_PROJECTS),
        "activeProjects": len([p for p in DRUG_PROJECTS if p['status'] == 'active']),
        "clinicalTrials": len(CLINICAL_TRIALS),
        "leadCompounds": sum(p['leadCompounds'] for p in DRUG_PROJECTS),
        "repurposingCandidates": len(REPURPOSING_CANDIDATES),
        "avgSuccessProbability": round(sum(p['probability'] for p in DRUG_PROJECTS) / len(DRUG_PROJECTS), 2)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5008)
