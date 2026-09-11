# 🧮 Comprehensive Algorithms & Cryptographic Models Guide

This document details every **algorithm, mathematical protocol, cryptographic function, and data structure** implemented across the Universal Government Interoperability Middleware platform.

---

## 1. 🛡️ Post-Quantum Cryptography & Quantum Physics Algorithms

### A. NIST Kyber-1024 (CRYSTALS-Kyber) Algorithm
- **Type**: Lattice-Based Post-Quantum Key Encapsulation Mechanism (KEM).
- **Module**: `services/quantum_engine.py`
- **Mathematical Principle**: Based on the **Learning With Errors over Module Lattices (M-LWE)** hard mathematical problem.
- **How It Works**:
  1. Generates 1024-bit polynomial matrices over a polynomial ring $R_q = \mathbb{Z}_q[X]/(X^n + 1)$.
  2. Encapsulates a 256-bit shared secret key using lattice vectors with small noise components.
  3. Decapsulates using the secret key matrix $S$ such that $V - S^T U \approx M$.
- **Why Used**: Protects cross-state government communications against future Quantum Supercomputer attacks ("Harvest Now, Decrypt Later" prevention).

### B. BB84 Quantum Key Distribution (QKD) Protocol Simulation
- **Type**: Quantum Physics Key Exchange Algorithm.
- **Module**: `services/quantum_engine.py`
- **Mathematical Principle**: Heisenberg’s Uncertainty Principle & Photon Polarization Measurement.
- **How It Works**:
  1. **Sender (Alice)** prepares random photon qubits using 2 non-orthogonal bases:
     - Rectilinear Basis ($+$): $|0\rangle$ (0°), $|1\rangle$ (90°)
     - Diagonal Basis ($\times$): $|+\rangle$ (45°), $|-\rangle$ (135°)
  2. **Receiver (Bob)** measures incoming qubits choosing random bases.
  3. **Sifting Phase**: Alice and Bob publicly compare bases (discarding mismatched bases) to arrive at a raw 256-bit symmetric encryption key.
  4. **Quantum Bit Error Rate (QBER) Check**: Computes error percentage ($QBER = \frac{E_{bits}}{N_{sample}}$). If $QBER > 11\%$, eavesdropping is detected and the key is aborted.

---

## 2. ⛓️ Blockchain & Cryptographic Hashing Algorithms

### A. SHA-256 (Secure Hash Algorithm 256-bit)
- **Type**: Cryptographic Hash Function (FIPS 180-4 Standard).
- **Modules**: `services/blockchain_service.py`, `services/mdm_service.py`
- **Mathematical Principle**: Merkle-Damgård construction operating on 512-bit message blocks with 64 rounds of bitwise rotations, logical functions (Ch, Maj, $\Sigma_0$, $\Sigma_1$), and modular additions.
- **Why Used**:
  - Computes block hashes for government sanction verification.
  - Hashes national ID numbers (`state_id_hash = SHA256(sso_id + salt)`) for identity deduplication without exposing PII.

### B. Merkle Tree Hashing Algorithm
- **Type**: Binary Cryptographic Hash Tree Structure.
- **Module**: `services/blockchain_service.py`
- **Algorithm Execution**:
  1. Hashes individual transaction records: $L_i = \text{SHA256}(\text{tx}_i)$.
  2. Combines pairs of adjacent hashes: $H_{parent} = \text{SHA256}(L_1 \parallel L_2)$.
  3. Recursively computes upward until a single 32-byte **Merkle Root Hash** is formed.
- **Why Used**: Allows instantaneous, lightweight verification of multi-department approval steps without needing to scan the entire blockchain ledger.

---

## 3. 🔑 Authentication & Identity Deduplication Algorithms

### A. PBKDF2-HMAC-SHA256 (Password-Based Key Derivation Function 2)
- **Type**: Key Derivation & Hashing Algorithm.
- **Module**: `services/sso_service.py`
- **Algorithm Formula**: $DK = \text{PBKDF2}(\text{Password}, \text{Salt}, c, dkLen)$ with $c \ge 100,000$ iterations.
- **Why Used**: Prevents rainbow table and brute-force password cracking attacks.

### B. HMAC-SHA256 JWT Token Signing
- **Type**: Keyed-Hash Message Authentication Code.
- **Module**: `services/sso_service.py`
- **Algorithm Formula**: $\text{HMAC}(K, M) = \text{SHA256}((K' \oplus opad) \parallel \text{SHA256}((K' \oplus ipad) \parallel M))$.
- **Why Used**: Signs 256-bit SSO tokens to guarantee user role scopes (**ADMIN**, **OFFICER**, **CITIZEN**) cannot be tampered with on the client side.

### C. Master Data Management (MDM) Identity Resolution Matcher
- **Type**: Deterministic Hashing & Deduplication Matcher.
- **Module**: `services/mdm_service.py`
- **How It Works**: Computes a unique state identity key `state_id_hash` from national credentials, checking if an identity has already claimed grants in other departments or states.

---

## 4. 🔄 System Interoperability & Resiliency Algorithms

### A. Exponential Backoff & Jitter Retry Algorithm
- **Type**: Asynchronous Fault-Tolerance Algorithm.
- **Module**: `services/event_bus.py`
- **Algorithm Formula**:
  $$T_{\text{wait}} = \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{retry\_count}}) + \text{random\_jitter}$$
- **Why Used**: Prevents "thundering herd" problems when retrying failed inter-departmental network requests.

### B. SLA Countdown & Escalation Tracking Algorithm
- **Type**: Real-time State & SLA Compliance Computation.
- **Module**: `services/workflow_engine.py`
- **Algorithm Execution**: Computes elapsed time $\Delta T = T_{\text{current}} - T_{\text{submission}}$. If $\Delta T > 48\text{ hours}$, status escalates to `SLA_WARNING` and notifies the department head.

---

## 5. 🤖 Artificial Intelligence & Recommendation Algorithms

### A. Keyword Intent & TF-IDF Cosine Matching Algorithm
- **Type**: Natural Language Processing (NLP) Intent Matching.
- **Module**: `services/ai_chat.py`
- **Why Used**: Parses citizen natural language text (e.g. *"I need a startup loan"* or *"scholarship for college"*) into structured query topics (`BANKING_MUDRA_LOAN`, `EDU_SCHOLARSHIP_GRANT`).

### B. Rule-Based Decision Tree Eligibility Filter
- **Type**: Automated Matching Decision Engine.
- **Module**: `routes/gateway.py`
- **Why Used**: Filters 100+ state schemes based on citizen demographic inputs (State/UT, Income Level, Qualification, Sector).

---

## 📊 Summary Table for Viva Presentation

| Algorithm | Category | Primary Function in Project |
| :--- | :--- | :--- |
| **NIST Kyber-1024** | Post-Quantum Cryptography | Lattice-based encryption for quantum-safe inter-state data transfer. |
| **BB84 QKD** | Quantum Physics Protocol | Quantum key generation with QBER eavesdropping detection. |
| **SHA-256** | Cryptographic Hashing | Block hashing & SHA-256 PII identity deduplication. |
| **Merkle Tree** | Data Structure & Hashing | Compresses multi-department logs into a single verifiable Merkle Root. |
| **PBKDF2-HMAC-SHA256** | Password Cryptography | Secure password derivation and storage. |
| **HMAC-SHA256 (JWT)** | Token Authentication | Single Sign-On (SSO) session token verification. |
| **Exponential Backoff** | Resiliency / Fault Tolerance | Retries failed department API calls safely without server overload. |
| **SLA Time-Delta Engine** | Workflow Monitoring | Enforces < 48-hour processing deadlines across department officers. |
