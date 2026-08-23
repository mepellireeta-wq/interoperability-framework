# Universal Government Interoperability & Federated Service Delivery Framework

**Theme**: Smart Automation | **Category**: Software  

---

## 🏛️ System Vision

An interoperability framework, middleware layer, and federated service delivery architecture designed to eliminate fragmented service delivery across government departments. Supports API-based exchange, common data standards, master data management (MDM), consent-based data sharing, single sign-on (SSO), event-driven notifications, unified application tracking, and configurable workflow orchestration.

---

## 👥 6-Member Team 2-Day Work Allocation

| Member & Role | Core Module & Responsibilities | Phase Ownership |
|---|---|---|
| **Member 1: Team Lead & Security Architect** | API Gateway, SSO / Federated Identity Module, Consent Manager, RBAC, Core Flask Server | **Phases 1, 2, 4, 5, 16** |
| **Member 2: Frontend & Portal Specialist** | Unified Citizen/Business Portal UI, Application Form Interfaces, Animated 360° Tracking Timeline UI | **Phases 6, 11, 15** |
| **Member 3: Interoperability & MDM Lead** | Database Schema (`models.py`), E-Governance Data Standardization Schema Mapper, Master Data Management (MDM) | **Phases 3, 7, 13** |
| **Member 4: Workflow Engine & Connectors Dev** | Configurable Workflow Orchestration Engine, Modern REST Connectors & Legacy Adapters (Depts A, B, C) | **Phases 8, 9** |
| **Member 5: Event Bus & Admin Analytics Lead** | Event-Driven Message Bus Pipeline, Citizen Notification Engine (SMS/Email), Admin Dashboard & SLA Analytics | **Phases 10, 12, 14** |
| **Member 6: Testing & Hardware/IoT Specialist** | Automated API Test Suites, Edge-case Exception Handlers, Optional ESP32 Sensor Telemetry | **Phases 6, 17, 20** |

---

## ⚡ Quickstart Guide

```bash
# 1. Enter project folder
cd C:\Users\mepel\OneDrive\Desktop\sih-interop

# 2. Initialize virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Initialize Database
python database/db_init.py

# 5. Run application
python app.py
```
Visit `http://127.0.0.1:5000/api/health` to verify.
