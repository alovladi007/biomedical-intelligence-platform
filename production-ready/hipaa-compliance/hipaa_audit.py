"""
Full HIPAA Compliance Audit Framework
Comprehensive audit of all HIPAA Security Rule requirements (45 CFR § 164.302-318)
"""

import json
import logging
from typing import Dict, List
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HIPAAComplianceAudit:
    """
    Complete HIPAA Security Rule compliance audit

    Covers:
    - Administrative Safeguards (§164.308)
    - Physical Safeguards (§164.310)
    - Technical Safeguards (§164.312)
    - Organizational Requirements (§164.314)
    - Policies and Procedures (§164.316)
    - Documentation Requirements (§164.316(b))
    """

    def __init__(self, organization_name: str):
        self.organization_name = organization_name
        self.audit_results = []
        self.compliance_score = 0

    def audit_administrative_safeguards(self) -> Dict:
        """
        Audit Administrative Safeguards (§164.308)

        Required implementations:
        - Security Management Process
        - Assigned Security Responsibility
        - Workforce Security
        - Information Access Management
        - Security Awareness and Training
        - Security Incident Procedures
        - Contingency Plan
        - Evaluation
        - Business Associate Contracts
        """
        logger.info("\n[ADMINISTRATIVE SAFEGUARDS - §164.308]")

        checks = []

        # §164.308(a)(1) - Security Management Process
        checks.extend([
            {
                'regulation': '§164.308(a)(1)(i)',
                'requirement': 'Security Management Process',
                'implementation': 'Required',
                'questions': [
                    'Risk analysis conducted and documented?',
                    'Risk management strategy implemented?',
                    'Sanction policy for violations?',
                    'Information system activity review process?'
                ],
                'evidence_required': [
                    'Risk analysis documentation',
                    'Risk management plan',
                    'Sanctions policy',
                    'Audit logs review procedures'
                ]
            },
            {
                'regulation': '§164.308(a)(1)(ii)(A)',
                'requirement': 'Risk Analysis',
                'implementation': 'Required',
                'questions': [
                    'Potential risks to ePHI identified?',
                    'Likelihood and impact assessed?',
                    'Current security measures evaluated?'
                ]
            },
            {
                'regulation': '§164.308(a)(1)(ii)(B)',
                'requirement': 'Risk Management',
                'implementation': 'Required',
                'questions': [
                    'Security measures implemented to reduce risks?',
                    'Risks reduced to reasonable and appropriate level?'
                ]
            },
            {
                'regulation': '§164.308(a)(1)(ii)(C)',
                'requirement': 'Sanction Policy',
                'implementation': 'Required',
                'questions': [
                    'Sanctions applied to workforce members who violate policies?',
                    'Sanction policy documented and communicated?'
                ]
            },
            {
                'regulation': '§164.308(a)(1)(ii)(D)',
                'requirement': 'Information System Activity Review',
                'implementation': 'Required',
                'questions': [
                    'Information system activity regularly reviewed?',
                    'Audit logs, access reports, security incidents reviewed?'
                ]
            }
        ])

        # §164.308(a)(2) - Assigned Security Responsibility
        checks.append({
            'regulation': '§164.308(a)(2)',
            'requirement': 'Assigned Security Responsibility',
            'implementation': 'Required',
            'questions': [
                'Security official designated?',
                'Security responsibilities clearly defined?'
            ],
            'evidence_required': ['Security officer designation document']
        })

        # §164.308(a)(3) - Workforce Security
        checks.extend([
            {
                'regulation': '§164.308(a)(3)(i)',
                'requirement': 'Workforce Security',
                'implementation': 'Required',
                'questions': [
                    'Procedures for workforce member authorization?',
                    'Workforce clearance procedures?',
                    'Termination procedures?'
                ]
            },
            {
                'regulation': '§164.308(a)(3)(ii)(A)',
                'requirement': 'Authorization and/or Supervision',
                'implementation': 'Addressable',
                'questions': [
                    'Authorization procedures for workforce access to ePHI?',
                    'Supervision of workforce members?'
                ]
            },
            {
                'regulation': '§164.308(a)(3)(ii)(B)',
                'requirement': 'Workforce Clearance Procedure',
                'implementation': 'Addressable',
                'questions': [
                    'Clearance procedures appropriate to access level?',
                    'Background checks conducted?'
                ]
            },
            {
                'regulation': '§164.308(a)(3)(ii)(C)',
                'requirement': 'Termination Procedures',
                'implementation': 'Addressable',
                'questions': [
                    'Procedures for terminating access?',
                    'Access terminated within 24 hours of termination?'
                ]
            }
        ])

        # §164.308(a)(4) - Information Access Management
        checks.extend([
            {
                'regulation': '§164.308(a)(4)(i)',
                'requirement': 'Information Access Management',
                'implementation': 'Required',
                'questions': [
                    'Policies for authorizing access to ePHI?',
                    'Access limited to minimum necessary?'
                ]
            },
            {
                'regulation': '§164.308(a)(4)(ii)(B)',
                'requirement': 'Access Authorization',
                'implementation': 'Addressable',
                'questions': [
                    'Access authorization policies and procedures?',
                    'Role-based access control implemented?'
                ]
            },
            {
                'regulation': '§164.308(a)(4)(ii)(C)',
                'requirement': 'Access Establishment and Modification',
                'implementation': 'Addressable',
                'questions': [
                    'Procedures for granting access?',
                    'Procedures for modifying access?',
                    'Access reviewed periodically?'
                ]
            }
        ])

        # §164.308(a)(5) - Security Awareness and Training
        checks.extend([
            {
                'regulation': '§164.308(a)(5)(i)',
                'requirement': 'Security Awareness and Training',
                'implementation': 'Required',
                'questions': [
                    'Security awareness training program implemented?',
                    'All workforce members trained?',
                    'Annual refresher training provided?'
                ]
            },
            {
                'regulation': '§164.308(a)(5)(ii)(A)',
                'requirement': 'Security Reminders',
                'implementation': 'Addressable',
                'questions': [
                    'Periodic security reminders provided?',
                    'Phishing awareness training?'
                ]
            },
            {
                'regulation': '§164.308(a)(5)(ii)(B)',
                'requirement': 'Protection from Malicious Software',
                'implementation': 'Addressable',
                'questions': [
                    'Training on malware threats?',
                    'Antivirus/anti-malware deployed?'
                ]
            },
            {
                'regulation': '§164.308(a)(5)(ii)(C)',
                'requirement': 'Log-in Monitoring',
                'implementation': 'Addressable',
                'questions': [
                    'Login attempts monitored?',
                    'Unusual login activity reported?'
                ]
            },
            {
                'regulation': '§164.308(a)(5)(ii)(D)',
                'requirement': 'Password Management',
                'implementation': 'Addressable',
                'questions': [
                    'Password policies established?',
                    'Complex passwords required (8+ chars, uppercase, lowercase, numbers, special)?',
                    'Password rotation enforced (every 90 days)?',
                    'Previous passwords prevented from reuse?'
                ]
            }
        ])

        # §164.308(a)(6) - Security Incident Procedures
        checks.extend([
            {
                'regulation': '§164.308(a)(6)(i)',
                'requirement': 'Security Incident Procedures',
                'implementation': 'Required',
                'questions': [
                    'Procedures for identifying security incidents?',
                    'Procedures for responding to incidents?',
                    'Procedures for mitigating harmful effects?'
                ]
            },
            {
                'regulation': '§164.308(a)(6)(ii)',
                'requirement': 'Response and Reporting',
                'implementation': 'Required',
                'questions': [
                    'Incident response plan documented?',
                    'Incidents tracked and documented?',
                    'Breaches reported per §164.404-414?'
                ]
            }
        ])

        # §164.308(a)(7) - Contingency Plan
        checks.extend([
            {
                'regulation': '§164.308(a)(7)(i)',
                'requirement': 'Contingency Plan',
                'implementation': 'Required',
                'questions': [
                    'Data backup plan established?',
                    'Disaster recovery plan documented?',
                    'Emergency mode operation plan?'
                ]
            },
            {
                'regulation': '§164.308(a)(7)(ii)(A)',
                'requirement': 'Data Backup Plan',
                'implementation': 'Required',
                'questions': [
                    'ePHI backed up regularly?',
                    'Backups tested for restore?',
                    'Backups stored securely offsite?'
                ]
            },
            {
                'regulation': '§164.308(a)(7)(ii)(B)',
                'requirement': 'Disaster Recovery Plan',
                'implementation': 'Required',
                'questions': [
                    'Disaster recovery procedures established?',
                    'RTO (Recovery Time Objective) defined?',
                    'RPO (Recovery Point Objective) defined?',
                    'Plan tested annually?'
                ]
            },
            {
                'regulation': '§164.308(a)(7)(ii)(C)',
                'requirement': 'Emergency Mode Operation Plan',
                'implementation': 'Required',
                'questions': [
                    'Emergency operations procedures established?',
                    'ePHI accessible during emergencies?'
                ]
            },
            {
                'regulation': '§164.308(a)(7)(ii)(E)',
                'requirement': 'Applications and Data Criticality Analysis',
                'implementation': 'Addressable',
                'questions': [
                    'Critical applications identified?',
                    'Data criticality assessed?',
                    'Priority recovery order established?'
                ]
            }
        ])

        # §164.308(a)(8) - Evaluation
        checks.append({
            'regulation': '§164.308(a)(8)',
            'requirement': 'Evaluation',
            'implementation': 'Required',
            'questions': [
                'Periodic technical and non-technical evaluations conducted?',
                'Security measures effectiveness assessed?',
                'Evaluations conducted at least annually?',
                'Evaluations after environmental or operational changes?'
            ],
            'evidence_required': ['Annual security evaluation reports']
        })

        # §164.308(b) - Business Associate Contracts
        checks.append({
            'regulation': '§164.308(b)(1)',
            'requirement': 'Business Associate Contracts',
            'implementation': 'Required',
            'questions': [
                'Written BAAs with all business associates?',
                'BAAs include required provisions (§164.314)?',
                'Subcontractor agreements in place?'
            ],
            'evidence_required': ['Signed Business Associate Agreements']
        })

        return {
            'category': 'Administrative Safeguards',
            'regulation': '§164.308',
            'total_checks': len(checks),
            'checks': checks
        }

    def audit_physical_safeguards(self) -> Dict:
        """Audit Physical Safeguards (§164.310)"""
        logger.info("\n[PHYSICAL SAFEGUARDS - §164.310]")

        checks = []

        # §164.310(a) - Facility Access Controls
        checks.extend([
            {
                'regulation': '§164.310(a)(1)',
                'requirement': 'Facility Access Controls',
                'implementation': 'Required',
                'questions': [
                    'Procedures to limit physical access to ePHI?',
                    'Authorized personnel only can access facilities?'
                ]
            },
            {
                'regulation': '§164.310(a)(2)(i)',
                'requirement': 'Contingency Operations',
                'implementation': 'Addressable',
                'questions': [
                    'Facility access procedures during emergencies?'
                ]
            },
            {
                'regulation': '§164.310(a)(2)(ii)',
                'requirement': 'Facility Security Plan',
                'implementation': 'Addressable',
                'questions': [
                    'Facility security plan documented?',
                    'Physical barriers (locks, badges)?',
                    'Visitor logs maintained?'
                ]
            },
            {
                'regulation': '§164.310(a)(2)(iii)',
                'requirement': 'Access Control and Validation Procedures',
                'implementation': 'Addressable',
                'questions': [
                    'Procedures for controlling/validating access?',
                    'Badge access system?',
                    'Sign-in/sign-out logs?'
                ]
            },
            {
                'regulation': '§164.310(a)(2)(iv)',
                'requirement': 'Maintenance Records',
                'implementation': 'Addressable',
                'questions': [
                    'Facility repairs/modifications documented?',
                    'Security impact assessed?'
                ]
            }
        ])

        # §164.310(b) - Workstation Use
        checks.append({
            'regulation': '§164.310(b)',
            'requirement': 'Workstation Use',
            'implementation': 'Required',
            'questions': [
                'Policies for workstation use?',
                'Proper use of workstations accessing ePHI defined?',
                'Acceptable use policy documented?'
            ]
        })

        # §164.310(c) - Workstation Security
        checks.append({
            'regulation': '§164.310(c)',
            'requirement': 'Workstation Security',
            'implementation': 'Required',
            'questions': [
                'Physical safeguards for workstations?',
                'Privacy screens used?',
                'Auto-lock after inactivity (15 min)?',
                'Workstations positioned to minimize ePHI exposure?'
            ]
        })

        # §164.310(d) - Device and Media Controls
        checks.extend([
            {
                'regulation': '§164.310(d)(1)',
                'requirement': 'Device and Media Controls',
                'implementation': 'Required',
                'questions': [
                    'Policies for receipt and removal of hardware/media?',
                    'ePHI disposal procedures?',
                    'Media reuse procedures?'
                ]
            },
            {
                'regulation': '§164.310(d)(2)(i)',
                'requirement': 'Disposal',
                'implementation': 'Required',
                'questions': [
                    'Procedures for final disposal of ePHI?',
                    'Secure deletion/destruction methods?',
                    'Certificate of destruction obtained?'
                ]
            },
            {
                'regulation': '§164.310(d)(2)(ii)',
                'requirement': 'Media Re-use',
                'implementation': 'Required',
                'questions': [
                    'Procedures for removing ePHI before reuse?',
                    'Secure wiping procedures?'
                ]
            },
            {
                'regulation': '§164.310(d)(2)(iii)',
                'requirement': 'Accountability',
                'implementation': 'Addressable',
                'questions': [
                    'Hardware/media movements tracked?',
                    'Inventory of devices maintained?'
                ]
            },
            {
                'regulation': '§164.310(d)(2)(iv)',
                'requirement': 'Data Backup and Storage',
                'implementation': 'Addressable',
                'questions': [
                    'Backup media stored securely?',
                    'Offsite backup storage?',
                    'Backup media encrypted?'
                ]
            }
        ])

        return {
            'category': 'Physical Safeguards',
            'regulation': '§164.310',
            'total_checks': len(checks),
            'checks': checks
        }

    def audit_technical_safeguards(self) -> Dict:
        """Audit Technical Safeguards (§164.312)"""
        logger.info("\n[TECHNICAL SAFEGUARDS - §164.312]")

        checks = []

        # §164.312(a) - Access Control
        checks.extend([
            {
                'regulation': '§164.312(a)(1)',
                'requirement': 'Access Control',
                'implementation': 'Required',
                'questions': [
                    'Technical policies to limit ePHI access?',
                    'Access limited to authorized persons?'
                ]
            },
            {
                'regulation': '§164.312(a)(2)(i)',
                'requirement': 'Unique User Identification',
                'implementation': 'Required',
                'questions': [
                    'Unique user IDs assigned?',
                    'No shared accounts?',
                    'User identification tracked in audit logs?'
                ]
            },
            {
                'regulation': '§164.312(a)(2)(ii)',
                'requirement': 'Emergency Access Procedure',
                'implementation': 'Required',
                'questions': [
                    'Emergency access procedures established?',
                    'Break-glass accounts available?',
                    'Emergency access logged and reviewed?'
                ]
            },
            {
                'regulation': '§164.312(a)(2)(iii)',
                'requirement': 'Automatic Logoff',
                'implementation': 'Addressable',
                'questions': [
                    'Automatic logoff after inactivity?',
                    'Timeout set to 15 minutes or less?'
                ]
            },
            {
                'regulation': '§164.312(a)(2)(iv)',
                'requirement': 'Encryption and Decryption',
                'implementation': 'Addressable',
                'questions': [
                    'ePHI encrypted at rest?',
                    'Encryption algorithm (AES-256)?',
                    'ePHI encrypted in transit (TLS 1.2/1.3)?',
                    'Encryption keys managed securely?'
                ]
            }
        ])

        # §164.312(b) - Audit Controls
        checks.append({
            'regulation': '§164.312(b)',
            'requirement': 'Audit Controls',
            'implementation': 'Required',
            'questions': [
                'Audit logs implemented?',
                'All ePHI access logged?',
                'Logs include: user ID, timestamp, action, resource?',
                'Logs retained for 6 years?',
                'Logs protected from modification?',
                'Logs reviewed regularly?'
            ],
            'evidence_required': ['Audit log samples', 'Log review procedures']
        })

        # §164.312(c) - Integrity
        checks.extend([
            {
                'regulation': '§164.312(c)(1)',
                'requirement': 'Integrity',
                'implementation': 'Required',
                'questions': [
                    'Policies to ensure ePHI not improperly altered/destroyed?',
                    'Data integrity controls implemented?'
                ]
            },
            {
                'regulation': '§164.312(c)(2)',
                'requirement': 'Mechanism to Authenticate ePHI',
                'implementation': 'Addressable',
                'questions': [
                    'Methods to verify ePHI not altered?',
                    'Digital signatures or checksums used?',
                    'Version control implemented?'
                ]
            }
        ])

        # §164.312(d) - Person or Entity Authentication
        checks.append({
            'regulation': '§164.312(d)',
            'requirement': 'Person or Entity Authentication',
            'implementation': 'Required',
            'questions': [
                'Authentication procedures implemented?',
                'Multi-factor authentication (MFA) required?',
                'Password complexity enforced?',
                'Failed login attempts tracked?',
                'Account lockout after 5 failed attempts?'
            ]
        })

        # §164.312(e) - Transmission Security
        checks.extend([
            {
                'regulation': '§164.312(e)(1)',
                'requirement': 'Transmission Security',
                'implementation': 'Required',
                'questions': [
                    'Technical measures to guard against unauthorized ePHI access during transmission?',
                    'Network security measures?'
                ]
            },
            {
                'regulation': '§164.312(e)(2)(i)',
                'requirement': 'Integrity Controls',
                'implementation': 'Addressable',
                'questions': [
                    'Measures to ensure transmitted ePHI not improperly modified?',
                    'Message authentication codes used?'
                ]
            },
            {
                'regulation': '§164.312(e)(2)(ii)',
                'requirement': 'Encryption',
                'implementation': 'Addressable',
                'questions': [
                    'ePHI encrypted during network transmission?',
                    'TLS 1.2 or higher used?',
                    'VPN for remote access?',
                    'Email encryption for ePHI?'
                ]
            }
        ])

        return {
            'category': 'Technical Safeguards',
            'regulation': '§164.312',
            'total_checks': len(checks),
            'checks': checks
        }

    def audit_organizational_requirements(self) -> Dict:
        """Audit Organizational Requirements (§164.314)"""
        logger.info("\n[ORGANIZATIONAL REQUIREMENTS - §164.314]")

        checks = []

        # §164.314(a) - Business Associate Contracts
        checks.extend([
            {
                'regulation': '§164.314(a)(1)',
                'requirement': 'Business Associate Contracts or Other Arrangements',
                'implementation': 'Required',
                'questions': [
                    'Written BAAs with all business associates?',
                    'BAAs include all required provisions?',
                    'BAAs reviewed annually?'
                ]
            },
            {
                'regulation': '§164.314(a)(2)(i)',
                'requirement': 'BAA Required Provisions',
                'implementation': 'Required',
                'questions': [
                    'BAA requires BA to comply with HIPAA?',
                    'BAA requires safeguards for ePHI?',
                    'BAA requires breach reporting?',
                    'BAA requires subcontractor agreements?',
                    'BAA allows termination for violations?'
                ]
            }
        ])

        # §164.314(b) - Other Arrangements
        checks.append({
            'regulation': '§164.314(b)(1)',
            'requirement': 'Requirements for Group Health Plans',
            'implementation': 'Required',
            'questions': [
                'Group health plan documents include privacy provisions?'
            ]
        })

        return {
            'category': 'Organizational Requirements',
            'regulation': '§164.314',
            'total_checks': len(checks),
            'checks': checks
        }

    def audit_policies_and_procedures(self) -> Dict:
        """Audit Policies and Procedures (§164.316)"""
        logger.info("\n[POLICIES AND PROCEDURES - §164.316]")

        checks = []

        # §164.316(a) - Policies and Procedures
        checks.append({
            'regulation': '§164.316(a)',
            'requirement': 'Policies and Procedures',
            'implementation': 'Required',
            'questions': [
                'Written policies and procedures for all HIPAA requirements?',
                'Policies reviewed annually?',
                'Policies approved by management?',
                'Policies accessible to workforce?'
            ],
            'evidence_required': ['Complete HIPAA policies and procedures manual']
        })

        # §164.316(b) - Documentation
        checks.extend([
            {
                'regulation': '§164.316(b)(1)',
                'requirement': 'Documentation',
                'implementation': 'Required',
                'questions': [
                    'All required documentation maintained?',
                    'Documentation includes policies, procedures, actions, activities, assessments?',
                    'Documentation retained for 6 years?',
                    'Documentation available to workforce and for review?'
                ]
            },
            {
                'regulation': '§164.316(b)(2)(i)',
                'requirement': 'Time Limit',
                'implementation': 'Required',
                'questions': [
                    'Documentation retained for 6 years from creation or last effective date?'
                ]
            },
            {
                'regulation': '§164.316(b)(2)(ii)',
                'requirement': 'Availability',
                'implementation': 'Required',
                'questions': [
                    'Documentation made available to responsible parties?'
                ]
            },
            {
                'regulation': '§164.316(b)(2)(iii)',
                'requirement': 'Updates',
                'implementation': 'Required',
                'questions': [
                    'Documentation reviewed and updated as needed?',
                    'Changes documented?'
                ]
            }
        ])

        return {
            'category': 'Policies and Procedures',
            'regulation': '§164.316',
            'total_checks': len(checks),
            'checks': checks
        }

    def conduct_full_audit(self) -> Dict:
        """Conduct complete HIPAA compliance audit"""
        logger.info("="*70)
        logger.info("HIPAA SECURITY RULE COMPLIANCE AUDIT")
        logger.info(f"Organization: {self.organization_name}")
        logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)

        # Run all audits
        results = []
        results.append(self.audit_administrative_safeguards())
        results.append(self.audit_physical_safeguards())
        results.append(self.audit_technical_safeguards())
        results.append(self.audit_organizational_requirements())
        results.append(self.audit_policies_and_procedures())

        # Generate comprehensive report
        report = self.generate_compliance_report(results)

        return report

    def generate_compliance_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive compliance report"""
        total_checks = sum(r['total_checks'] for r in results)

        report = {
            'organization': self.organization_name,
            'audit_date': datetime.now().isoformat(),
            'auditor': 'Automated HIPAA Compliance Audit System',
            'total_requirements_checked': total_checks,
            'results_by_category': results,
            'required_evidence': self._collect_required_evidence(results),
            'recommendations': self._generate_recommendations(results)
        }

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("AUDIT SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Requirements Checked: {total_checks}")
        logger.info("\nRequirements by Category:")
        for result in results:
            logger.info(f"  {result['category']}: {result['total_checks']} checks")

        logger.info(f"\nTotal Evidence Items Required: {len(report['required_evidence'])}")
        logger.info("="*70)

        return report

    def _collect_required_evidence(self, results: List[Dict]) -> List[Dict]:
        """Collect all required evidence items"""
        evidence = []
        for category_result in results:
            for check in category_result['checks']:
                if 'evidence_required' in check:
                    for item in check['evidence_required']:
                        evidence.append({
                            'category': category_result['category'],
                            'regulation': check['regulation'],
                            'requirement': check['requirement'],
                            'evidence': item
                        })
        return evidence

    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = [
            "1. Conduct annual risk analysis and document findings",
            "2. Implement multi-factor authentication (MFA) for all ePHI access",
            "3. Ensure all workforce members complete annual HIPAA training",
            "4. Maintain audit logs for all ePHI access (6-year retention)",
            "5. Encrypt all ePHI at rest (AES-256) and in transit (TLS 1.3)",
            "6. Implement automatic logoff after 15 minutes of inactivity",
            "7. Test disaster recovery plan annually",
            "8. Review and update Business Associate Agreements",
            "9. Conduct security incident response drills quarterly",
            "10. Document all policies and procedures (6-year retention)",
            "11. Implement role-based access control (RBAC)",
            "12. Perform penetration testing annually",
            "13. Conduct vulnerability scans quarterly",
            "14. Maintain inventory of all devices accessing ePHI",
            "15. Implement secure disposal procedures for all media containing ePHI"
        ]
        return recommendations

    def save_report(self, report: Dict, filename: str):
        """Save audit report to file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"\nDetailed audit report saved to: {filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HIPAA Compliance Audit")
    parser.add_argument("--organization", required=True, help="Organization name")
    parser.add_argument("--output", default="hipaa_audit_report.json", help="Output file")

    args = parser.parse_args()

    # Conduct audit
    auditor = HIPAAComplianceAudit(args.organization)
    report = auditor.conduct_full_audit()

    # Save report
    auditor.save_report(report, args.output)
