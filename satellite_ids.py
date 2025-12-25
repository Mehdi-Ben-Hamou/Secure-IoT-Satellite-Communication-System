import socket
import json
import time
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
import requests

GROUND_IP = "192.168.1.30"
GROUND_PORT = 5001

# Même clé que IoT
SECRET_KEY = b'GS****************************ss='
cipher = Fernet(SECRET_KEY)

class IntrusionDetectionSystem:
    def __init__(self):
        self.message_count = {}
        self.blocked_ips = []
        self.alerts = []

    def log_alert(self, alert_type, source_ip, details):
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "source": source_ip,
            "details": details,
            "severity": "HIGH" if "ATTACK" in alert_type else "MEDIUM"
        }
        self.alerts.append(alert)
        
    def analyze_message(self, message, client_ip):
        """Analyse approfondie du message"""
        checks = []

        # Vérification basique
        if client_ip in self.blocked_ips:
            return False, ["BLOCKED_IP"]

        # Vérification structure
        required = ["sender", "encrypted_data", "signature"]
        for field in required:
            if field not in message:
                self.log_alert("INVALID_STRUCTURE", client_ip, f"Missing {field}")
                return False, ["INVALID_STRUCTURE"]

        # Flood detection
        current_time = time.time()
        if client_ip not in self.message_count:
            self.message_count[client_ip] = []

        self.message_count[client_ip] = [
            t for t in self.message_count[client_ip] 
            if current_time - t < 10
        ]

        if len(self.message_count[client_ip]) > 15:
            self.log_alert("FLOOD_ATTACK_DETECTED", client_ip, 
                          f"{len(self.message_count[client_ip])} messages/10s")
            self.blocked_ips.append(client_ip)
            return False, ["FLOOD_ATTACK"]

        self.message_count[client_ip].append(current_time)

        # Vérification chiffrement
        try:
            encrypted = message['encrypted_data'].encode('latin-1')
            decrypted = cipher.decrypt(encrypted).decode('utf-8')
            data = json.loads(decrypted)
            checks.append("DECRYPTION_OK")

            # Vérification données
            temp = data.get("temperature", 0)
            if temp < -50 or temp > 50:
                self.log_alert("DATA_TAMPERING", client_ip, f"Temp: {temp}°C")
                checks.append("DATA_ANOMALY")

            # Vérification séquence
            if "sequence" in data:
                expected_sig = f"SIG_{data['sequence']:06d}"
                if message['signature'] != expected_sig:
                    self.log_alert("SIGNATURE_TAMPERING", client_ip, 
                                  f"Expected {expected_sig}, got {message['signature']}")
                    checks.append("SIGNATURE_INVALID")

        except InvalidToken:
            self.log_alert("ENCRYPTION_TAMPERING", client_ip, "Invalid encryption token")
            return False, ["ENCRYPTION_FAILED"]
        except Exception as e:
            self.log_alert("PROCESSING_ERROR", client_ip, str(e)[:100])
            checks.append("PROCESSING_ERROR")

        return True, checks
    
    def forward_to_ground(self, message):
        try:
            with socket.socket() as s:
                s.settimeout(3)
                s.connect((GROUND_IP, GROUND_PORT))
                s.sendall(json.dumps(message).encode())
                return True
        except:
            return False
    
    def start(self):
        print("[Satellite] Intrusion Detection System starting...")
        print(f"[Satellite] Listening: 0.0.0.0:5000")
        print(f"[Satellite] Forwarding to: {GROUND_IP}:{GROUND_PORT}")

        with socket.socket() as server:
            server.bind(('0.0.0.0', 5000))
            server.listen(10)

            while True:
                try:
                    client, addr = server.accept()
                    client_ip = addr[0]

                    data = client.recv(4096).decode('utf-8')
                    message = json.loads(data)

                    print(f"\n[Satellite] From {client_ip}: {message.get('sender', 'Unknown')}")

                    valid, checks = self.analyze_message(message, client_ip)

                    for check in checks:
                        print(f"[Satellite] Check: {check}")

                    if not valid:
                        print(f"[Satellite] Message rejected")
                        client.close()
                        continue

                    # Latence satellite
                    taime.sleep(0.5)

                    # Transmission
                    if self.forward_to_ground(message):
                        print("[Satellite] Forwarded successfully")
                    else:
                        print("[Satellite] Forwarding failed")

                    client.close()

                except json.JSONDecodeError:
                    print("[Satellite] Invalid JSON - rejected")
                except Exception as e:
                    print(f"[Satellite] Error: {e}")

if __name__ == "__main__":
    ids = IntrusionDetectionSystem()
    ids.start()
