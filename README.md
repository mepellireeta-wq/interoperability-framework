# Universal Government Interoperability & Federated Service Delivery Framework

**Theme**: Smart Automation | **Category**: Software | **SIH 2026 Hackathon**  
**Repository**: [https://github.com/mepellireeta-wq/interoperability-framework](https://github.com/mepellireeta-wq/interoperability-framework)

---

## 🏛️ Project Overview

Government departments across states and central ministries operate independent portals, registries, and databases developed in isolation. Incompatible data formats, custom authentication schemes, and fragmented ownership prevent seamless information exchange.

**Our Proposed Solution**: A lightweight, secure, standards-based **Universal Interoperability Middleware Layer** connecting legacy and modern government systems without requiring complete system replacement.

---

## ⚡ Quickstart Setup Guide (Run on Your Laptop)

Follow these simple step-by-step commands to clone and run the complete system on your laptop:

```bash
# 1. Clone the repository
git clone https://github.com/mepellireeta-wq/interoperability-framework.git
cd interoperability-framework

# 2. Create and activate Python Virtual Environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\activate

# On Linux / Mac:
source venv/bin/activate

# 3. Install all required dependencies
pip install -r requirements.txt

# 4. Initialize Database with Seed Data
python database/db_init.py

# 5. Launch the application server
python app.py
```

Once running, your local server will be active at: **`http://127.0.0.1:5000`**

---

## 🔗 Direct Localhost Links

When the server is running (`python app.py`), click any link below to test the portal live in your browser:

| Portal Section | Direct Localhost Link | Description |
|---|---|---|
| 🏠 **Home Page** | [http://127.0.0.1:5000/](http://127.0.0.1:5000/) | Universal Landing Page & Scheme Highlights |
| 🔑 **Sign In** | [http://127.0.0.1:5000/login-page](http://127.0.0.1:5000/login-page) | Federated SSO Sign In (Role-based Navigation) |
| ✍️ **Sign Up** | [http://127.0.0.1:5000/register-page](http://127.0.0.1:5000/register-page) | New Citizen Account Registration |
| 👤 **Citizen Portal** | [http://127.0.0.1:5000/citizen-portal](http://127.0.0.1:5000/citizen-portal) | Scoped Citizen Workspace & Submitted Applications |
| 📝 **Apply for Schemes** | [http://127.0.0.1:5000/apply-page](http://127.0.0.1:5000/apply-page) | Unified Application Form across all 28 States & UTs |
| 🔍 **Track Application** | [http://127.0.0.1:5000/track-page](http://127.0.0.1:5000/track-page) | 360° Real-Time Timeline Progress Tracking |
| 🎓 **Schemes Catalog** | [http://127.0.0.1:5000/schemes](http://127.0.0.1:5000/schemes) | Multi-Sector Scheme Directory (Education, Health, Banking, etc.) |
| 🏛️ **Governance Overview** | [http://127.0.0.1:5000/governance](http://127.0.0.1:5000/governance) | IndEA 2.0 Governance & 28 States Directory |
| ⛓️ **Blockchain Verifier** | [http://127.0.0.1:5000/blockchain-verifier](http://127.0.0.1:5000/blockchain-verifier) | Public SHA-256 Blockchain Ledger & Certificate Authenticator |
| 🔒 **Official Admin Portal** | [http://127.0.0.1:5000/admin-portal](http://127.0.0.1:5000/admin-portal) | Protected Governance SLA Dashboard & Pending Queue |
| 💻 **Developer Tech Portal** | [http://127.0.0.1:5000/developer-tech](http://127.0.0.1:5000/developer-tech) | Quantum Cryptography Specs, QKD Telemetry & API Schemas |

---

## 🔑 Demo Login Credentials

| Role | Username | Password | Default Redirect Portal |
|---|---|---|---|
| 👨‍💼 **System Administrator** | `admin` | `Admin@123` | Official Admin Portal (`/admin-portal`) |
| 👤 **Citizen User** | `citizen_demo` | `Citizen@123` | Citizen Workspace (`/citizen-portal`) |

---

## 🔄 Step-by-Step System Workflow

```
[ Step 1: Citizen SSO Sign Up / Login ]
                   │
                   ▼
[ Step 2: Unified Scheme Application Submission ]
                   │
                   ▼
[ Step 3: Data Standardization (E-GOV-STD-INTEROP-2026) & SHA-256 MDM Deduplication ]
                   │
                   ▼
[ Step 4: Multi-Department Workflow Engine Routing ]
  ├── Stage 1: Skills Dept (Modern REST API Connector)
  ├── Stage 2: Employment Dept (Legacy SOAP/XML Adapter)
  └── Stage 3: Innovation Society (Direct Database Sync)
                   │
                   ▼
[ Step 5: Real-Time 360° Timeline Tracking & Public Blockchain Block Creation ]
                   │
                   ▼
[ Step 6: Executive Admin SLA Analytics & Approval Queue ]
```

1. **SSO Authentication**: Citizen registers or logs in via Federated SSO issuing a secure JWT token.
2. **Unified Submission**: Citizen selects a scheme (e.g. *Integrated Skill-to-Entrepreneurship Pathway*) and submits ONE form with data consent.
3. **Standardization & MDM**: Data is transformed into standard schema `E-GOV-STD-INTEROP-2026`. Master Data Management (MDM) hashes national IDs (SHA-256) to block duplicate subsidy claims.
4. **Multi-Department Routing**: Application progresses through automated stage connectors (REST, Legacy SOAP/XML, and Direct DB).
5. **Blockchain Block Mining**: Upon stage approval, an immutable cryptographic SHA-256 block is recorded on the public ledger.
6. **SLA Monitoring**: Officials process pending queues while SLA warning timers (<48h) ensure fast sanction delivery.

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

---

## 📡 REST API Endpoint Reference

| Method | Endpoint | Description | Access Role |
|---|---|---|---|
| `GET` | `/api/health` | Middleware System Health Check | Public |
| `POST` | `/api/v1/auth/login` | Federated SSO Authentication | Public |
| `POST` | `/api/v1/auth/register` | Citizen Registration & MDM Profile Creator | Public |
| `POST` | `/api/v1/auth/logout` | Token Revocation & Logout | Authenticated |
| `GET` | `/api/v1/gateway/services` | Service Discovery Registry | Public |
| `POST` | `/api/v1/applications/submit` | Unified Application Submission | Public |
| `GET` | `/api/v1/applications/track/<id>` | 360° Application Timeline Tracking | Public |
| `GET` | `/api/v1/admin/pending-applications` | Admin Queue & Pending Metrics | Admin / Officer |
| `POST` | `/api/v1/workflows/advance` | Officer Stage Approval / Sanction | Admin / Officer |
| `GET` | `/api/v1/blockchain/ledger` | Retrieve Public Blockchain Ledger | Public |
| `POST` | `/api/v1/blockchain/verify` | Verify Application Certificate Hash | Public |
| `POST` | `/api/v1/ai/chat` | AI Chatbot Assistant & Status Guide | Public |

---
&copy; 2026 Universal Government Interoperability Framework | Smart India Hackathon 2026
