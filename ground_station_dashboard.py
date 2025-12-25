from flask import Flask, render_template, jsonify, request
import socket
import json
import threading
import sqlite3
from datetime import datetime
from cryptography.fernet import Fernet
import plotly.graph_objs as go
import plotly.utils
import random

app = Flask(__name__)

SECRET_KEY = b'GS****************************ss='
DISCORD_WEBHOOK = "VOTRE_WEBHOOK_DISCORD"

telemetry_data = []
alerts = []
system_status = {
    "satellite_connected": False,
    "last_message": None,
    "message_count": 0,
    "attack_count": 0
}

def init_database():
    conn = sqlite3.connect('satellite_monitoring.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT,
            temperature REAL,
            humidity REAL,
            battery REAL,
            latitude REAL,
            longitude REAL,
            timestamp DATETIME,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            source_ip TEXT,
            details TEXT,
            severity TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[Ground] Database initialized")

def save_telemetry(data):
    conn = sqlite3.connect('satellite_monitoring.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO telemetry 
        (sensor_id, temperature, humidity, battery, latitude, longitude, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('sensor_id'),
        data.get('temperature'),
        data.get('humidity'),
        data.get('battery'),
        data.get('latitude'),
        data.get('longitude'),
        data.get('timestamp')
    ))
    conn.commit()
    conn.close()

def save_security_event(event_type, source_ip, details, severity):
    conn = sqlite3.connect('satellite_monitoring.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO security_events (event_type, source_ip, details, severity)
        VALUES (?, ?, ?, ?)
    ''', (event_type, source_ip, details, severity))
    conn.commit()
    conn.close()

def receive_from_satellite():
    global telemetry_data, alerts, system_status
    
    print("[Ground] Starting satellite receiver...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 5001))
    server.listen(5)
    
    while True:
        try:
            client, addr = server.accept()
            system_status["satellite_connected"] = True

            data = client.recv(4096).decode('utf-8')
            message = json.loads(data)

            try:
                cipher = Fernet(SECRET_KEY)
                encrypted = message['encrypted_data'].encode('latin-1')
                decrypted = cipher.decrypt(encrypted).decode('utf-8')
                sensor_data = json.loads(decrypted)

                telemetry_data.append(sensor_data)
                if len(telemetry_data) > 100:
                    telemetry_data.pop(0)

                save_telemetry(sensor_data)
                system_status["message_count"] += 1
                system_status["last_message"] = datetime.now().isoformat()

                print(f"[Ground] Received: {sensor_data['sensor_id']} - {sensor_data['temperature']}°C")

            except Exception as e:
                print(f"[Ground] Processing error: {e}")
                alerts.append({
                    "type": "PROCESSING_ERROR",
                    "message": str(e),
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "severity": "HIGH"
                })

            client.close()

        except Exception as e:
            print(f"[Ground] Error: {e}")

# Routes Flask
@app.route('/')
def dashboard():
    """Dashboard principal"""
    return render_template('dashboard.html')

@app.route('/api/telemetry')
def api_telemetry():
    """API des données télémetriques"""
    return jsonify({
        "telemetry": telemetry_data[-20:],  
        "status": system_status
    })

@app.route('/api/security')
def api_security():
    """API des événements de sécurité"""
    conn = sqlite3.connect('satellite_monitoring.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT event_type, source_ip, details, severity, timestamp 
        FROM security_events 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''')
    
    events = []
    for row in cursor.fetchall():
        events.append({
            "type": row[0],
            "source": row[1],
            "details": row[2],
            "severity": row[3],
            "time": row[4]
        })
    
    conn.close()
    
    return jsonify({
        "events": events,
        "stats": {
            "total_messages": system_status["message_count"],
            "satellite_connected": system_status["satellite_connected"]
        }
    })

@app.route('/api/charts/temperature')
def temperature_chart():
    """Données pour graphique température"""
    conn = sqlite3.connect('satellite_monitoring.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, temperature 
        FROM telemetry 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''')
    
    data = cursor.fetchall()
    conn.close()
    
    times = [row[0] for row in data]
    temps = [row[1] for row in data]
    
    trace = go.Scatter(
        x=list(reversed(times)),
        y=list(reversed(temps)),
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#FF6B6B', width=2)
    )
    
    layout = go.Layout(
        title='Temperature History',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(title='Time', gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title='°C', gridcolor='rgba(255,255,255,0.1)')
    )
    
    return json.dumps({'data': [trace], 'layout': layout}, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/stats')
def api_stats():
    """Statistiques système"""
    conn = sqlite3.connect('satellite_monitoring.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    total_telemetry = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM security_events WHERE severity = 'HIGH'")
    high_alerts = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT AVG(temperature), AVG(humidity), AVG(battery)
        FROM telemetry 
        WHERE timestamp > datetime('now', '-1 hour')
    ''')
    
    avg_data = cursor.fetchone()
    
    conn.close()
    
    return jsonify({
        "telemetry_count": total_telemetry,
        "high_alerts": high_alerts,
        "averages": {
            "temperature": round(avg_data[0], 2) if avg_data[0] else 0,
            "humidity": round(avg_data[1], 2) if avg_data[1] else 0,
            "battery": round(avg_data[2], 2) if avg_data[2] else 0
        },
        "system": system_status
    })

def start():
    """Démarre l'application"""
    init_database()
    
    receiver = threading.Thread(target=receive_from_satellite, daemon=True)
    receiver.start()
    
    print("\n[Ground] Arctic Research Dashboard")
    print(f"[Ground] Dashboard: http://192.168.1.30:8080")
    print("[Ground] APIs:")
    print("  - /api/telemetry     : Latest sensor data")
    print("  - /api/security      : Security events")
    print("  - /api/stats         : System statistics")
    print("  - /api/charts/temperature : Temperature chart data")
    
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == "__main__":