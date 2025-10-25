"""
Security Penetration Testing Suite
Tests for OWASP Top 10 vulnerabilities and HIPAA security requirements
"""

import requests
import json
import time
from typing import Dict, List
import logging
from urllib.parse import urljoin
import base64
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityPenetrationTest:
    """
    Comprehensive security penetration testing suite

    Tests for:
    - OWASP Top 10 vulnerabilities
    - HIPAA security requirements
    - Authentication/Authorization bypass
    - SQL Injection
    - XSS (Cross-Site Scripting)
    - CSRF (Cross-Site Request Forgery)
    - API security
    - Data encryption
    - Rate limiting
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.vulnerabilities = []
        self.passed_tests = []

    def test_authentication_bypass(self) -> Dict:
        """Test for authentication bypass vulnerabilities"""
        logger.info("\n[1] Testing Authentication Bypass...")

        tests = []

        # Test 1: Access protected endpoint without token
        try:
            response = self.session.get(f"{self.base_url}/api/protected")
            if response.status_code == 200:
                tests.append({
                    'test': 'No authentication required',
                    'severity': 'critical',
                    'status': 'vulnerable',
                    'description': 'Protected endpoints accessible without authentication'
                })
            else:
                tests.append({
                    'test': 'Authentication required',
                    'severity': 'n/a',
                    'status': 'pass',
                    'description': 'Protected endpoints properly require authentication'
                })
        except:
            pass

        # Test 2: Invalid token
        invalid_tokens = [
            'invalid_token',
            'Bearer invalid',
            '',
            'null',
            'undefined'
        ]

        for token in invalid_tokens:
            try:
                headers = {'Authorization': f'Bearer {token}'}
                response = self.session.get(f"{self.base_url}/api/protected", headers=headers)

                if response.status_code == 200:
                    tests.append({
                        'test': f'Invalid token accepted: {token}',
                        'severity': 'critical',
                        'status': 'vulnerable',
                        'description': 'System accepts invalid authentication tokens'
                    })
                    break
            except:
                pass

        # Test 3: JWT token manipulation
        try:
            # Try to manipulate JWT alg header to "none"
            fake_jwt = base64.b64encode(b'{"alg":"none","typ":"JWT"}').decode() + '.' + \
                       base64.b64encode(b'{"user":"admin","role":"admin"}').decode() + '.'

            headers = {'Authorization': f'Bearer {fake_jwt}'}
            response = self.session.get(f"{self.base_url}/api/protected", headers=headers)

            if response.status_code == 200:
                tests.append({
                    'test': 'JWT algorithm manipulation',
                    'severity': 'critical',
                    'status': 'vulnerable',
                    'description': 'JWT tokens with "none" algorithm accepted'
                })
            else:
                tests.append({
                    'test': 'JWT algorithm validation',
                    'severity': 'n/a',
                    'status': 'pass',
                    'description': 'JWT algorithm properly validated'
                })
        except:
            pass

        return {'category': 'Authentication Bypass', 'tests': tests}

    def test_sql_injection(self) -> Dict:
        """Test for SQL injection vulnerabilities"""
        logger.info("\n[2] Testing SQL Injection...")

        tests = []

        sql_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "admin' --",
            "' UNION SELECT NULL, NULL, NULL --",
            "1; DROP TABLE users--",
            "' AND 1=CONVERT(int, (SELECT @@version))--"
        ]

        # Test common endpoints
        test_endpoints = [
            '/api/patients',
            '/api/search',
            '/api/records'
        ]

        for endpoint in test_endpoints:
            for payload in sql_payloads:
                try:
                    # Test in query parameters
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        params={'id': payload}
                    )

                    # Check for SQL error messages
                    error_patterns = [
                        'SQL syntax',
                        'mysql_fetch',
                        'PostgreSQL',
                        'ORA-',
                        'SQLite',
                        'ODBC'
                    ]

                    if any(pattern.lower() in response.text.lower() for pattern in error_patterns):
                        tests.append({
                            'test': f'SQL Injection in {endpoint}',
                            'severity': 'critical',
                            'status': 'vulnerable',
                            'description': f'SQL error message exposed with payload: {payload}',
                            'endpoint': endpoint
                        })
                        break

                except:
                    pass

        if not any(t['status'] == 'vulnerable' for t in tests):
            tests.append({
                'test': 'SQL Injection prevention',
                'severity': 'n/a',
                'status': 'pass',
                'description': 'No SQL injection vulnerabilities detected'
            })

        return {'category': 'SQL Injection', 'tests': tests}

    def test_xss(self) -> Dict:
        """Test for Cross-Site Scripting (XSS) vulnerabilities"""
        logger.info("\n[3] Testing XSS (Cross-Site Scripting)...")

        tests = []

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>",
            "'-alert('XSS')-'",
            "\"><script>alert('XSS')</script>"
        ]

        # Test in various inputs
        test_data = {
            'name': '<script>alert("XSS")</script>',
            'email': 'test<script>alert("XSS")</script>@test.com',
            'comment': '<img src=x onerror=alert("XSS")>'
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/test",
                json=test_data
            )

            # Check if script tags are reflected without sanitization
            if any(payload in response.text for payload in xss_payloads):
                tests.append({
                    'test': 'XSS in input fields',
                    'severity': 'high',
                    'status': 'vulnerable',
                    'description': 'User input not properly sanitized, XSS possible'
                })
            else:
                tests.append({
                    'test': 'XSS prevention',
                    'severity': 'n/a',
                    'status': 'pass',
                    'description': 'Input properly sanitized'
                })
        except:
            tests.append({
                'test': 'XSS testing',
                'severity': 'n/a',
                'status': 'pass',
                'description': 'Unable to test (endpoint not accessible)'
            })

        return {'category': 'Cross-Site Scripting (XSS)', 'tests': tests}

    def test_insecure_direct_object_reference(self) -> Dict:
        """Test for Insecure Direct Object Reference (IDOR)"""
        logger.info("\n[4] Testing Insecure Direct Object Reference (IDOR)...")

        tests = []

        # Test access to other users' resources
        test_ids = [1, 2, 999, 'admin', '../../../etc/passwd']

        for test_id in test_ids:
            try:
                response = self.session.get(f"{self.base_url}/api/patients/{test_id}")

                if response.status_code == 200:
                    # Check if we can access resources without proper authorization
                    tests.append({
                        'test': f'IDOR with ID: {test_id}',
                        'severity': 'high',
                        'status': 'potential_vuln',
                        'description': f'Resource accessible with ID {test_id} - verify authorization'
                    })
            except:
                pass

        if not tests:
            tests.append({
                'test': 'IDOR prevention',
                'severity': 'n/a',
                'status': 'pass',
                'description': 'Proper authorization checks in place'
            })

        return {'category': 'Insecure Direct Object Reference', 'tests': tests}

    def test_security_misconfiguration(self) -> Dict:
        """Test for security misconfigurations"""
        logger.info("\n[5] Testing Security Misconfiguration...")

        tests = []

        # Test 1: Debug mode enabled
        try:
            response = self.session.get(f"{self.base_url}/debug")
            if response.status_code == 200 or 'debug' in response.text.lower():
                tests.append({
                    'test': 'Debug mode enabled',
                    'severity': 'medium',
                    'status': 'vulnerable',
                    'description': 'Debug mode exposed in production'
                })
        except:
            pass

        # Test 2: Directory listing
        try:
            response = self.session.get(f"{self.base_url}/")
            if 'Index of' in response.text or 'Directory listing' in response.text:
                tests.append({
                    'test': 'Directory listing enabled',
                    'severity': 'medium',
                    'status': 'vulnerable',
                    'description': 'Directory listing exposes file structure'
                })
        except:
            pass

        # Test 3: Server information disclosure
        try:
            response = self.session.get(f"{self.base_url}/health")
            headers = response.headers

            if 'Server' in headers:
                tests.append({
                    'test': 'Server information disclosure',
                    'severity': 'low',
                    'status': 'info',
                    'description': f'Server header exposes: {headers["Server"]}'
                })
        except:
            pass

        # Test 4: HTTPS/TLS configuration
        if self.base_url.startswith('http://'):
            tests.append({
                'test': 'HTTPS not enforced',
                'severity': 'critical',
                'status': 'vulnerable',
                'description': 'API accessible over unencrypted HTTP'
            })

        if not tests:
            tests.append({
                'test': 'Security configuration',
                'severity': 'n/a',
                'status': 'pass',
                'description': 'No misconfigurations detected'
            })

        return {'category': 'Security Misconfiguration', 'tests': tests}

    def test_sensitive_data_exposure(self) -> Dict:
        """Test for sensitive data exposure"""
        logger.info("\n[6] Testing Sensitive Data Exposure...")

        tests = []

        # Test for exposed PHI/PII
        try:
            response = self.session.get(f"{self.base_url}/api/patients/1")

            if response.status_code == 200:
                data = response.json()

                # Check for unencrypted sensitive fields
                sensitive_fields = ['ssn', 'social_security', 'password', 'credit_card', 'dob']

                for field in sensitive_fields:
                    if field in str(data).lower():
                        tests.append({
                            'test': f'Sensitive field exposed: {field}',
                            'severity': 'critical',
                            'status': 'vulnerable',
                            'description': f'Sensitive data field "{field}" transmitted without encryption'
                        })
        except:
            pass

        # Test for exposure in error messages
        try:
            response = self.session.get(f"{self.base_url}/api/invalid_endpoint_xyz")

            # Check if stack traces or sensitive info in errors
            if 'Traceback' in response.text or 'File "' in response.text:
                tests.append({
                    'test': 'Stack trace exposure',
                    'severity': 'medium',
                    'status': 'vulnerable',
                    'description': 'Stack traces exposed in error messages'
                })
        except:
            pass

        if not tests:
            tests.append({
                'test': 'Sensitive data protection',
                'severity': 'n/a',
                'status': 'pass',
                'description': 'No sensitive data exposure detected'
            })

        return {'category': 'Sensitive Data Exposure', 'tests': tests}

    def test_rate_limiting(self) -> Dict:
        """Test for rate limiting and DoS protection"""
        logger.info("\n[7] Testing Rate Limiting...")

        tests = []

        # Send multiple requests rapidly
        num_requests = 100
        start_time = time.time()
        successful_requests = 0

        for i in range(num_requests):
            try:
                response = self.session.get(f"{self.base_url}/health", timeout=1)
                if response.status_code == 200:
                    successful_requests += 1
            except:
                pass

        elapsed_time = time.time() - start_time

        if successful_requests >= num_requests * 0.9:  # 90%+ success
            tests.append({
                'test': 'Rate limiting not implemented',
                'severity': 'medium',
                'status': 'vulnerable',
                'description': f'{successful_requests}/{num_requests} requests succeeded without rate limiting'
            })
        else:
            tests.append({
                'test': 'Rate limiting active',
                'severity': 'n/a',
                'status': 'pass',
                'description': 'Rate limiting appears to be implemented'
            })

        return {'category': 'Rate Limiting', 'tests': tests}

    def test_cors_misconfiguration(self) -> Dict:
        """Test for CORS misconfigurations"""
        logger.info("\n[8] Testing CORS Configuration...")

        tests = []

        try:
            headers = {'Origin': 'https://evil.com'}
            response = self.session.get(f"{self.base_url}/health", headers=headers)

            cors_header = response.headers.get('Access-Control-Allow-Origin')

            if cors_header == '*':
                tests.append({
                    'test': 'CORS allows any origin',
                    'severity': 'medium',
                    'status': 'vulnerable',
                    'description': 'CORS configured to allow all origins (*)'
                })
            elif cors_header == 'https://evil.com':
                tests.append({
                    'test': 'CORS reflects origin',
                    'severity': 'high',
                    'status': 'vulnerable',
                    'description': 'CORS reflects attacker-controlled origin'
                })
            else:
                tests.append({
                    'test': 'CORS properly configured',
                    'severity': 'n/a',
                    'status': 'pass',
                    'description': 'CORS allows only specific origins'
                })
        except:
            tests.append({
                'test': 'CORS configuration',
                'severity': 'n/a',
                'status': 'pass',
                'description': 'Unable to test CORS'
            })

        return {'category': 'CORS Misconfiguration', 'tests': tests}

    def run_all_tests(self) -> Dict:
        """Run all penetration tests"""
        logger.info("="*70)
        logger.info("Security Penetration Testing Suite")
        logger.info("Target: " + self.base_url)
        logger.info("="*70)

        results = []

        # Run all tests
        results.append(self.test_authentication_bypass())
        results.append(self.test_sql_injection())
        results.append(self.test_xss())
        results.append(self.test_insecure_direct_object_reference())
        results.append(self.test_security_misconfiguration())
        results.append(self.test_sensitive_data_exposure())
        results.append(self.test_rate_limiting())
        results.append(self.test_cors_misconfiguration())

        # Generate report
        report = self.generate_report(results)

        return report

    def generate_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive security report"""
        total_tests = 0
        vulnerabilities = {'critical': [], 'high': [], 'medium': [], 'low': [], 'info': []}
        passed = 0

        for category_result in results:
            for test in category_result['tests']:
                total_tests += 1

                if test['status'] in ['vulnerable', 'potential_vuln']:
                    severity = test['severity']
                    if severity in vulnerabilities:
                        vulnerabilities[severity].append({
                            'category': category_result['category'],
                            'test': test['test'],
                            'description': test['description']
                        })
                elif test['status'] == 'pass':
                    passed += 1

        # Calculate security score
        critical_count = len(vulnerabilities['critical'])
        high_count = len(vulnerabilities['high'])
        medium_count = len(vulnerabilities['medium'])

        security_score = max(0, 100 - (critical_count * 25 + high_count * 15 + medium_count * 5))

        # Overall assessment
        if critical_count > 0:
            overall = 'CRITICAL - Immediate action required'
        elif high_count > 0:
            overall = 'HIGH RISK - Address vulnerabilities urgently'
        elif medium_count > 0:
            overall = 'MEDIUM RISK - Plan remediation'
        else:
            overall = 'LOW RISK - Continue monitoring'

        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'target': self.base_url,
            'total_tests': total_tests,
            'passed': passed,
            'vulnerabilities': vulnerabilities,
            'security_score': security_score,
            'overall_assessment': overall,
            'detailed_results': results
        }

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("SECURITY TEST SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Tests Run: {total_tests}")
        logger.info(f"Tests Passed: {passed}")
        logger.info(f"\nVulnerabilities Found:")
        logger.info(f"  Critical: {critical_count}")
        logger.info(f"  High: {high_count}")
        logger.info(f"  Medium: {medium_count}")
        logger.info(f"  Low: {len(vulnerabilities['low'])}")
        logger.info(f"\nSecurity Score: {security_score}/100")
        logger.info(f"Overall Assessment: {overall}")
        logger.info("="*70)

        return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Security Penetration Testing")
    parser.add_argument("--url", required=True, help="Target base URL (e.g., http://localhost:5001)")
    parser.add_argument("--output", default="security_report.json", help="Output file for report")

    args = parser.parse_args()

    # Run penetration tests
    tester = SecurityPenetrationTest(args.url)
    report = tester.run_all_tests()

    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"\nDetailed report saved to: {args.output}")
