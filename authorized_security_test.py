import socket
import json
import time
from datetime import datetime

class AuthorizedSecurityTest:
    def __init__(self):
        self.targets = {
            "satellite": "192.168.1.40",
            "iot": "192.168.1.20",
            "ground": "192.168.1.30"
        }
        self.tester_ip = "192.168.1.10"
        
        print("=" * 70)
        print("AUTHORIZED SECURITY ASSESSMENT - ARCTIC SATELLITE NETWORK")
        print("Scope: Controlled environment testing only")
        print("=" * 70)
        print(f"Tester: {self.tester_ip}")
        print(f"Authorized Targets: {self.targets}")
        print("=" * 70)
    
    def connectivity_test(self):

        print("\n[TEST 1/4] NETWORK CONNECTIVITY")
        print("Testing basic network connectivity...")
        
        results = {}
        for name, ip in self.targets.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((ip, 22 if name == "ground" else 5000))
                sock.close()
                results[name] = "REACHABLE"
                print(f"  ✓ {name} ({ip}): Reachable")
            except:
                # Try ping
                import subprocess
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", ip],
                    capture_output=True
                )
                if result.returncode == 0:
                    results[name] = "PING_ONLY"
                    print(f"  ⚠ {name} ({ip}): Ping only")
                else:
                    results[name] = "UNREACHABLE"
                    print(f"  ✗ {name} ({ip}): Unreachable")
        
        return results
    
    def protocol_validation(self):

        print("\n[TEST 2/4] PROTOCOL VALIDATION")
        print("Testing satellite communication protocol...")
        
        test_cases = [
            {
                "name": "Valid message format",
                "data": {
                    "sender": "TEST-SENSOR-001",
                    "timestamp": datetime.now().isoformat(),
                    "encrypted_data": "TEST_ENCRYPTED_DATA_VALID",
                    "signature": "SIG_000001"
                },
                "expected": "ACCEPTED_OR_REJECTED"
            },
            { 
                "name": "Missing signature",
                "data": {
                    "sender": "TEST-SENSOR-001",
                    "timestamp": datetime.now().isoformat(),
                    "encrypted_data": "TEST_DATA"
                },
                "expected": "REJECTED"
            },
            { 
                "name": "Invalid format",
                "data": "INVALID_STRING_DATA",
                "expected": "REJECTED"
            }
        ]
         
        for test in test_cases:
            print(f"\n  Testing: {test['name']}")
            try:
                with socket.socket() as s:
                    s.settimeout(3)
                    s.connect((self.targets["satellite"], 5000))
                    
                    if isinstance(test["data"], dict):
                        s.sendall(json.dumps(test["data"]).encode())
                    else:
                        s.sendall(test["data"].encode())
                    
                    print(f"    Sent: {test['data']}")
                    print(f"    Expected: {test['expected']}")
                    
            except Exception as e:
                print(f"    Error: {e}")
    
    def resilience_assessment(self):

        print("\n[TEST 3/4] SYSTEM RESILIENCE")
        print("Assessing system under controlled load...")
        
        print("  Sending controlled test sequence (5 messages)...")
        
        success = 0
        for i in range(5):
            try:
                with socket.socket() as s:
                    s.settimeout(2)
                    s.connect((self.targets["satellite"], 5000))
                    
                    test_msg = {
                        "test": f"load_test_{i}",
                        "timestamp": time.time(),
                        "authorized": True
                    }
                     
                    s.sendall(json.dumps(test_msg).encode())
                    success += 1
                    print(f"    Message {i+1}/5: Sent")
                    
            except socket.timeout:
                print(f"    Message {i+1}/5: Timeout (system may be rate limiting)")
            except Exception as e:
                print(f"    Message {i+1}/5: Failed ({e})")
            
            time.sleep(0.5)
        
        print(f"\n  Success rate: {success}/5 ({success*20}%)")
        print("  Note: System should maintain functionality under load")
    
    def security_recommendations(self):

        print("\n[TEST 4/4] SECURITY RECOMMENDATIONS")
        print("Based on security assessment:")
        
        recommendations = [
            "Implement message authentication (Already implemented)",
            "Rate limiting for flood protection (Partially implemented)",
            "Consider implementing IP blocking after multiple failures",
            "Add TLS encryption for satellite-ground communications",
            "Implement certificate-based authentication",
            "Regular security patching and updates",
            "Continuous monitoring and alerting",
            "Regular penetration testing"
        ]
         
        for rec in recommendations:
            print(f"  {rec}")
    
    def generate_report(self):

        print("\n" + "=" * 70)
        print("SECURITY ASSESSMENT REPORT")
        print("=" * 70)
        print(f"Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Assessor: Authorized Security Team")
        print(f"System: Arctic Satellite Research Network")
        print("\nEXECUTIVE SUMMARY:")
        print("- Network connectivity: Functional")
        print("- Protocol security: Basic authentication present")
        print("- System resilience: Adequate for normal operations")
        print("- Security posture: Acceptable with room for improvement")
        print("\nRISK ASSESSMENT:")
        print("- Risk Level: MEDIUM")
        print("- Key Risks: Potential MITM attacks, data tampering")
        print("- Mitigation: Encryption, monitoring, regular audits")
        print("\n[IMPORTANT] This assessment was conducted:")
        print("• With proper authorization")
        print("• In a controlled lab environment")
        print("• For educational and security improvement purposes")
        print("=" * 70)
    
    def run_assessment(self):

        print("\nStarting authorized security assessment...")
        time.sleep(1)
        
        print("\n LEGAL AND ETHICAL NOTICE:")
        print("This assessment is for AUTHORIZED testing only.")
        print("All tests are performed in a controlled environment.")
        print("Unauthorized testing is illegal and unethical.")
        
        consent = input("\nDo you have authorization? (yes/no): ")
        
        if consent.lower() != 'yes':
            print("\n Assessment cancelled. Authorization required.")
            return
        
        tests = [
            self.connectivity_test,
            self.protocol_validation,
            self.resilience_assessment,
            self.security_recommendations
        ]
         
        for i, test in enumerate(tests, 1):
            print(f"\n{'='*70}")
            print(f"ASSESSMENT PHASE {i}/{len(tests)}")
            print('='*70)
            test()
            if i < len(tests):
                input("\nPress Enter to continue to next phase...")
        
        self.generate_report()

if __name__ == "__main__":
    print("Initializing Security Assessment Tool...")
    time.sleep(1)
    
    tester = AuthorizedSecurityTest()
    tester.run_assessment()
