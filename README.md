# Secure IoT Satellite Communication System
## Overview
This project implements a secure, distributed IoT communication architecture simulating an Arctic sensor sending encrypted telemetry data through a satellite core with intrusion detection, to a ground station with a real-time monitoring dashboard.
The project focuses on confidentiality, integrity, availability, monitoring, and authorized security testing, in a controlled environment.

## System Architecture

<img width="1536" height="1024" alt="sat" src="https://github.com/user-attachments/assets/5b7b667b-8cb6-4199-a4e0-392fb65cdab1" />

### Components:
IoT Sensor: Generates and encrypts telemetry data
Satellite Core (IDS): Analyzes messages and detects suspicious behavior
Ground Station: Stores, visualizes, and monitors system data
Security Testing Tool: Performs authorized robustness and security tests

## How to Run the Project
### Prerequisites
Python 3.8+
Required libraries:
pip install cryptography flask plotly requests

## Launch Order (IMPORTANT)
Components must be started from receiver to sender:
### 1 Start Ground Station
python3 ground_station_dashboard.py
### 2 Start Satellite / Core (IDS)
python3 satellite_ids.py
### 3 Start IoT Sensor
python3 iot_sensor.py
### 4 Run Authorized Security Tests
python3 authorized_security_test.py

## Dashboard Features

Live telemetry data
Temperature history charts
System status indicators
Security alerts and statistics
Database-backed persistence

## Authorized Security Testing

This project includes a controlled security testing framework simulating:

## Simulated Threats

| Test               | Simulated Threat        |
|--------------------|-------------------------|
| Malformed messages | Protocol Injection      |
| Modified data      | Data Tampering          |
| Fake signatures    | Spoofing                |
| Repeated messages  | Replay Attack           |
| Rapid sending      | Low-rate Flooding       |

## All tests are:

Authorized
Ethical
Performed in a controlled environment

## Future Improvements

TLS encryption between satellite and ground
Certificate-based authentication
Advanced IDS rules
Scalability improvements
Containerization (Docker)
Cloud deployment

## Legal & Ethical Notice

This project is intended strictly for educational purposes and authorized security testing.
Unauthorized use, deployment, or testing on real systems is illegal and unethical.

## Author

Ben Hamou Mehdi	
Cybersecurity student

# Final Note

This project demonstrates applied cybersecurity concepts through a realistic and structured system design, emphasizing defensive security, monitoring, and responsible testing.
