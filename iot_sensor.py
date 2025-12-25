import socket
import json
import time
import random
from datetime import datetime
from cryptography.fernet import Fernet

SATELLITE_IP = "192.168.1.40"
SATELLITE_PORT = 5000

SECRET_KEY = b'GS****************************ss='  # À remplacer
cipher = Fernet(SECRET_KEY)

def create_sensor_data(seq):
    return {
        "sensor_id": "ARCTIC-SENSOR-01",
        "sequence": seq,
        "timestamp": datetime.now().isoformat(),
        "temperature": round(-15.0 + random.uniform(-5, 5), 2),
        "humidity": round(random.uniform(30, 70), 1),
        "battery": round(random.uniform(80, 100), 1),
        "latitude": 78.2235,
        "longitude": 15.6267
    }

def send_secure_data():
    print("[IoT] Starting secure sensor...")
    print(f"[IoT] Target: {SATELLITE_IP}:{SATELLITE_PORT}")
    
    seq = 0
    while True:
        try:
            data = create_sensor_data(seq)
            encrypted = cipher.encrypt(json.dumps(data).encode())
            message = {
                "sender": data["sensor_id"],
                "timestamp": data["timestamp"],
                "encrypted_data": encrypted.decode('latin-1'),
                "signature": f"SIG_{seq:06d}"
            }

            with socket.socket() as s:
                s.settimeout(5)
                s.connect((SATELLITE_IP, SATELLITE_PORT))
                s.sendall(json.dumps(message).encode())

                print(f"[IoT] #{seq} sent: {data['temperature']}°C")

            seq += 1
            time.sleep(8)

        except Exception as e:
            print(f"[IoT] Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    send_secure_data()
