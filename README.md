# Universal Government Interoperability & Federated Service Delivery Framework

**Theme**: Smart Automation | **Category**: Software | **SIH 2026 Hackathon**  
**Repository**: [https://github.com/mepellireeta-wq/interoperability-framework](https://github.com/mepellireeta-wq/interoperability-framework)

---

## 🏛️ System Vision & Problem Statement

Government departments (such as Skills Development, Employment Directorate, and State Innovation Societies) operate independent portals, registries, and databases developed in isolation. Incompatible data formats, custom authentication schemes, and fragmented ownership prevent seamless information exchange. 

Citizens face redundant document submissions, multi-portal tracking confusion, and physical office visits. Government officials lack a 360-degree view of beneficiaries, approvals, and SLA compliance.

**Our Proposed Solution**: A lightweight, secure, standards-based **Interoperability Middleware Layer** connecting legacy and modern government systems without requiring complete system replacement.

---

## 🌟 Core System Architecture & Features

```
[ Citizen / Business User ]
           │
           ▼
  [ Unified Portal ] ──► 🔐 [ SSO / Federated Identity ]
           │
           ▼
   [ API Gateway ] ──► (Consent Manager + Service Discovery + RBAC)
           │
           ▼
[ Interoperability Layer ]
   ├── 📊 Data Standardization Schema (E-GOV-STD-INTEROP-2026)
   ├── 🆔 Master Data Management (MDM SHA-256 Beneficiary Deduplication)
   └── 🛡️ Data Quality Checker Rules
           │
           ▼
  [ Workflow Engine ] (Configurable Multi-Department Stage Approval Pipeline)
           │
 ┌─────────┼─────────┐
 ▼         ▼         ▼
[ Modern ] [ Legacy ] [ Direct   ]
[ REST   ] [ SOAP   ] [ Database ]
[ Dept A ] [ Dept B ] [ Dept C   ]
 └─────────┬─────────┘
           ▼
 [ Event / Message Bus ] ──► (Async Notifications, Audit Trails, IoT Telemetry)
           │
 ┌─────────┴─────────┐
 ▼                   ▼
[ 360° Unified Tracking ] [ Admin Dashboard & SLA Compliance Analytics ]
```

### Key Technical Pillars:
1. **Federated SSO & JWT Security**: Single sign-on with JWT claim validation and instant token revocation on logout (`services/sso_service.py`).
2. **API Gateway & DPDP Consent Manager**: Service Discovery Registry, RBAC protection, and citizen data sharing consent controls (`routes/gateway.py`).
3. **Data Standardization & MDM**: Normalizes raw inputs into `E-GOV-STD-INTEROP-2026` schema and hashes national IDs (SHA-256) to prevent duplicate grant disbursements (`services/mdm_service.py`).
4. **Configurable Workflow Engine & Legacy SOAP Adapters**: Transforms JSON contracts into XML/SOAP envelopes for older government servers (`services/connectors.py`).
5. **Event-Driven Message Bus**: Asynchronous governance event publishing (`services/event_bus.py`) with SMS and Email alert dispatching (`services/notification_service.py`).
6. **Executive Admin SLA Dashboard**: Real-time compliance countdown timers (<48h warnings), officer approval queues, and immutable audit trails (`routes/admin.py` & `templates/admin.html`).
7. **Hardware IoT Telemetry Connector**: Accepts automated ESP32 sensor telemetry alerts for infrastructure/overflow monitoring (`services/iot_connector.py`).

---

## 📡 REST API Endpoint Documentation

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health` | Middleware System Health Check | No |
| `POST` | `/api/v1/auth/login` | Federated SSO Authentication | No |
| `POST` | `/api/v1/auth/register` | Citizen Registration & MDM Profile Creator | No |
| `POST` | `/api/v1/auth/verify` | SSO Token Introspection | No |
| `POST` | `/api/v1/auth/logout` | Token Revocation & Logout | Yes |
| `GET` | `/api/v1/gateway/services` | Service Discovery Registry | No |
| `POST` | `/api/v1/gateway/consent/grant` | Record Citizen Data Sharing Consent | No |
| `GET` | `/api/v1/gateway/security-health` | SIH Governance Security Diagnostics | Yes (Admin/Officer) |
| `POST` | `/api/v1/applications/submit` | Unified Application Submission & Standardization | No |
| `GET` | `/api/v1/applications/track/<id>` | 360° Multi-Stage Application Timeline Tracking | No |
| `POST` | `/api/v1/workflows/advance` | Officer Workflow Stage Approval | Yes (Officer) |
| `GET` | `/api/v1/admin/stats` | Executive Governance Metrics & SLA Analytics | Yes (Admin) |
| `GET` | `/api/v1/admin/audit-logs` | Immutable Governance Audit Trail | Yes (Admin) |
| `POST` | `/api/v1/gateway/iot/telemetry` | Hardware / ESP32 Sensor Telemetry Alert | No |

---

## 👥 6-Member Team Work Allocation

| Member & Role | Core Module & Responsibilities | Assigned Files |
|---|---|---|
| **Member 1: Team Lead & Security Architect** | API Gateway, SSO / Federated Identity, Consent Manager, RBAC, Core Flask Server | `routes/auth.py`, `routes/gateway.py`, `services/sso_service.py`, `services/consent_service.py` |
| **Member 2: Frontend & Portal Specialist** | Unified Citizen/Business Portal UI, Application Form, Animated 360° Tracking Timeline UI | `templates/base.html`, `templates/index.html`, `templates/apply.html`, `templates/track.html`, `static/css/style.css`, `static/js/portal.js` |
| **Member 3: Interoperability & MDM Lead** | Database Schemas (`models.py`), E-Governance Data Standardization Schema Mapper, MDM Deduplication | `services/interop_service.py`, `services/mdm_service.py`, `database/models.py`, `database/db_init.py` |
| **Member 4: Workflow Engine & Connectors Dev** | Configurable Workflow Orchestration Engine, Modern REST Connectors & Legacy SOAP/XML Adapters | `services/workflow_engine.py`, `services/connectors.py`, `routes/workflows.py`, `routes/simulated_depts.py` |
| **Member 5: Event Bus & Admin Analytics Lead** | Event-Driven Message Bus Pipeline, SMS/Email Notification Simulator, Admin Dashboard & SLA Analytics | `services/event_bus.py`, `services/notification_service.py`, `routes/admin.py`, `templates/admin.html` |
| **Member 6: Testing & Hardware/IoT Specialist** | Automated API Test Suites, Edge-case Exception Handlers, ESP32 Hardware IoT Telemetry Connector | `tests/test_api.py`, `tests/test_workflows.py`, `services/iot_connector.py` |

---

## ⚡ Quickstart Setup Guide

```bash
# 1. Clone project repository
git clone https://github.com/mepellireeta-wq/interoperability-framework.git
cd interoperability-framework

# 2. Create & activate Python virtual environment
python -m venv venv
.\venv\Scripts\activate      # On Windows (or source venv/bin/activate on Linux/Mac)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize Database with Seed Data
python database/db_init.py

# 5. Launch application server
python app.py
```

Open **`http://127.0.0.1:5000`** in your web browser to access the portal!

### Demo Login Credentials:
- **Admin**: Username `admin` | Password `Admin@123`
- **Officer**: Username `officer_skills` | Password `Officer@123`
- **Citizen**: Username `citizen_demo` | Password `Citizen@123`

---
&copy; 2026 Universal Government Interoperability Framework | Smart India Hackathon 2026
