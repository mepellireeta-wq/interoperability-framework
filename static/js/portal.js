// Frontend JavaScript for Universal Interoperability Portal & AI Guide

let currentDomain = 'ALL';
let currentState = 'ALL';

document.addEventListener('DOMContentLoaded', function() {
    
    // Load initial scheme catalog
    loadSchemeCatalog();

    // State Selector Event Listener
    const stateSelect = document.getElementById('stateFilterSelect');
    if (stateSelect) {
        stateSelect.addEventListener('change', function() {
            currentState = this.value;
            loadSchemeCatalog();
        });
    }

    // AI Chatbot Assistant Submission Handler
    const chatForm = document.getElementById('aiChatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const input = document.getElementById('chatInputText');
            const userMsg = input.value.trim();
            if (!userMsg) return;

            const chatArea = document.getElementById('chatMessageArea');
            // User message bubble
            chatArea.innerHTML += `
                <div class="bg-secondary text-white p-2 px-3 rounded-3 mb-2 ms-auto max-w-80 text-end">
                    <strong>You:</strong> ${userMsg}
                </div>
            `;
            input.value = '';
            chatArea.scrollTop = chatArea.scrollHeight;

            try {
                const res = await fetch('/api/v1/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMsg })
                });
                const data = await res.json();

                // AI Response bubble
                chatArea.innerHTML += `
                    <div class="bg-primary text-white p-3 rounded-3 mb-2 max-w-80">
                        <strong><i class="fa-solid fa-robot me-1 text-warning"></i> AI Guide:</strong> ${data.reply.replace(/\n/g, '<br>')}
                    </div>
                `;
                chatArea.scrollTop = chatArea.scrollHeight;
            } catch (err) {
                console.error(err);
            }
        });
    }

    // SSO Login Handler
    const ssoForm = document.getElementById('ssoLoginForm');
    if (ssoForm) {
        ssoForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                const res = await fetch('/api/v1/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                
                if (res.ok) {
                    localStorage.setItem('sso_token', data.token);
                    alert(`SSO Login Successful! Welcome ${data.user.full_name} (${data.user.role})`);
                    const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
                    if (modal) modal.hide();
                    location.reload();
                } else {
                    alert(`Login Failed: ${data.error}`);
                }
            } catch (err) {
                console.error(err);
                alert("Error connecting to SSO Server");
            }
        });
    }

    // Unified Application Form Submission Handler
    const appForm = document.getElementById('unifiedApplicationForm');
    if (appForm) {
        appForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const payload = {
                service_code: document.getElementById('appServiceCode').value,
                service_title: document.getElementById('appServiceCode').options[document.getElementById('appServiceCode').selectedIndex].text,
                applicant: {
                    full_name: document.getElementById('appFullName').value,
                    email: document.getElementById('appEmail').value,
                    phone: document.getElementById('appPhone').value,
                    state: document.getElementById('appStateSelect') ? document.getElementById('appStateSelect').value : 'Maharashtra',
                    district: document.getElementById('appDistrict') ? document.getElementById('appDistrict').value : 'Pune',
                    state_id_number: document.getElementById('appStateId').value
                },
                scheme_data: {
                    qualification: 'Graduate',
                    preferred_district: 'Pune'
                }
            };
            
            try {
                const res = await fetch('/api/v1/applications/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                if (res.ok) {
                    document.getElementById('resultTrackingId').innerText = data.tracking_id;
                    document.getElementById('trackLink').href = `/track-page?id=${data.tracking_id}`;
                    document.getElementById('submissionResult').classList.remove('d-none');
                    appForm.classList.add('d-none');
                } else {
                    alert(`Submission Failed: ${data.error}`);
                }
            } catch (err) {
                console.error(err);
                alert("Server error submitting application");
            }
        });
    }

    // Live Tracking Search Handler
    const btnTrack = document.getElementById('btnSearchTrack');
    if (btnTrack) {
        btnTrack.addEventListener('click', performTrackSearch);
        
        const urlParams = new URLSearchParams(window.location.search);
        const searchId = urlParams.get('id');
        if (searchId) {
            document.getElementById('trackInputId').value = searchId;
            performTrackSearch();
        }
    }
});

// Interactive Metric Card Modal Handler
function openMetricDetailModal(type) {
    const modalHeader = document.getElementById('metricModalHeader');
    const modalTitle = document.getElementById('metricModalTitle');
    const modalBody = document.getElementById('metricModalBody');

    if (type === 'states') {
        modalHeader.className = 'modal-header border-0 bg-primary text-white';
        modalTitle.innerHTML = '<i class="fa-solid fa-network-wired text-warning me-2"></i> 28 States & 8 Union Territories Integration';
        modalBody.innerHTML = `
            <div class="p-2">
                <h5 class="fw-bold text-primary mb-3">Universal All-India Federated Middleware Overlay</h5>
                <p class="text-dark">Our platform acts as a national-level federated window linking all 28 States & 8 UTs (such as <strong>Andhra Pradesh, Telangana, Maharashtra, Karnataka, Tamil Nadu, Delhi, UP, Gujarat</strong>) and Central Ministries under one unified portal.</p>
                <div class="row g-3 mt-2">
                    <div class="col-md-6">
                        <div class="border rounded p-3 bg-light">
                            <strong class="text-primary d-block mb-1"><i class="fa-solid fa-check-circle me-1"></i> Zero Duplicate Submissions</strong>
                            <small class="text-muted">Citizens do not need to register on multiple state websites or re-upload documents 5 different times.</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="border rounded p-3 bg-light">
                            <strong class="text-primary d-block mb-1"><i class="fa-solid fa-globe me-1"></i> Area & District Filtering</strong>
                            <small class="text-muted">Select your home state and district to automatically view localized schemes and portals in your region.</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else if (type === 'quantum') {
        modalHeader.className = 'modal-header border-0 bg-success text-white';
        modalTitle.innerHTML = '<i class="fa-solid fa-atom text-warning me-2"></i> Quantum-Safe Post-Quantum Lattice Security';
        modalBody.innerHTML = `
            <div class="p-2">
                <h5 class="fw-bold text-success mb-3">NIST-Kyber-1024 & BB84 Quantum Key Distribution (QKD)</h5>
                <p class="text-dark">To protect sensitive citizen records (Aadhaar hashes, Bank accounts, Health cards) transferred between state and central servers, our middleware uses <strong>BB84 Quantum Key Distribution and Post-Quantum Lattice Cryptography</strong>.</p>
                <div class="row g-3 mt-2">
                    <div class="col-md-6">
                        <div class="border rounded p-3 bg-light">
                            <strong class="text-success d-block mb-1"><i class="fa-solid fa-shield-halved me-1"></i> 100% Quantum-Resistant</strong>
                            <small class="text-muted">Protects against future Quantum Supercomputer attacks ("Harvest Now, Decrypt Later" prevention).</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="border rounded p-3 bg-light">
                            <strong class="text-success d-block mb-1"><i class="fa-solid fa-bolt me-1"></i> Qubit State Measurement</strong>
                            <small class="text-muted">Generates 256-bit encryption keys using simulated Qubit measurement states (|0⟩, |1⟩) with 99.98% fidelity.</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else if (type === 'sso') {
        modalHeader.className = 'modal-header border-0 bg-warning text-dark';
        modalTitle.innerHTML = '<i class="fa-solid fa-fingerprint me-2"></i> Single SSO & Master Data Management (MDM)';
        modalBody.innerHTML = `
            <div class="p-2">
                <h5 class="fw-bold text-dark mb-3">Federated Single Sign-On & SHA-256 Deduplication</h5>
                <p class="text-dark">Provides a single secure identity for every citizen while preventing welfare grant fraud across departments.</p>
                <div class="row g-3 mt-2">
                    <div class="col-md-6">
                        <div class="border rounded p-3 bg-light">
                            <strong class="text-dark d-block mb-1"><i class="fa-solid fa-id-card me-1"></i> Federated SSO JWT Token</strong>
                            <small class="text-muted">Citizens log in ONCE and access Education, Health, Banking, and Skill portals seamlessly.</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="border rounded p-3 bg-light">
                            <strong class="text-dark d-block mb-1"><i class="fa-solid fa-user-shield me-1"></i> SHA-256 MDM Profile</strong>
                            <small class="text-muted">Hashes national ID credentials to catch duplicate applicants across departments without exposing raw PII.</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else if (type === 'sla') {
        modalHeader.className = 'modal-header border-0 bg-danger text-white';
        modalTitle.innerHTML = '<i class="fa-solid fa-chart-line text-warning me-2"></i> Real-Time SLA Countdown & Accountability';
        modalBody.innerHTML = `
            <div class="p-2">
                <h5 class="fw-bold text-danger mb-3">Service-Level Agreement (SLA) & Officer Review Queue</h5>
                <p class="text-dark">Eliminates bureaucratic delays by enforcing real-time countdown timers and automated SLA warnings on officer dashboards.</p>
                <div class="row g-3 mt-2">
                    <div class="col-md-6">
                        <div class="border rounded p-3 bg-light">
                            <strong class="text-danger d-block mb-1"><i class="fa-solid fa-clock me-1"></i> &lt; 48-Hour Target</strong>
                            <small class="text-muted">Tracks average processing times across Stage 1, Stage 2, and Stage 3 department approvals.</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="border rounded p-3 bg-light">
                            <strong class="text-danger d-block mb-1"><i class="fa-solid fa-bell me-1"></i> Automated Warning Timers</strong>
                            <small class="text-muted">If a file is delayed past 48 hours, the system triggers automated SLA warning alerts to department heads.</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    const modal = new bootstrap.Modal(document.getElementById('metricDetailModal'));
    modal.show();
}

function filterDomain(domain) {
    currentDomain = domain;
    // Highlight selected tab
    const tabs = document.querySelectorAll('#domainFilterTabs button');
    tabs.forEach(tab => {
        if (tab.innerText.includes(domain) || (domain === 'ALL' && tab.innerText.includes('All'))) {
            tab.classList.add('btn-primary', 'text-white');
            tab.classList.remove('btn-outline-primary');
        } else {
            tab.classList.remove('btn-primary', 'text-white');
            tab.classList.add('btn-outline-primary');
        }
    });
    loadSchemeCatalog();
}

async function loadSchemeCatalog() {
    const container = document.getElementById('schemeContainer');
    if (!container) return;
    
    try {
        const res = await fetch(`/api/v1/gateway/services?state=${currentState}&domain=${currentDomain}`);
        const data = await res.json();
        
        if (res.ok && data.services.length > 0) {
            container.innerHTML = '';
            data.services.forEach(scheme => {
                const domainBadgeClass = scheme.domain === 'Education' ? 'bg-primary' : (scheme.domain === 'Health' ? 'bg-danger' : (scheme.domain === 'Banking' ? 'bg-success' : 'bg-warning text-dark'));
                
                container.innerHTML += `
                    <div class="col-md-6 col-lg-4 mb-4">
                        <div class="glass-card h-100 p-4 d-flex flex-column justify-content-between shadow-sm border">
                            <div class="d-flex flex-column h-100">
                                <div class="d-flex align-items-center mb-3">
                                    <span class="badge ${domainBadgeClass} rounded-pill me-2 px-3 py-1">${scheme.domain || 'Multi-Sector'}</span>
                                    <span class="badge bg-secondary rounded-pill px-2 py-1 font-monospace">${scheme.integration_type}</span>
                                </div>
                                <h5 class="fw-bold text-dark mb-2 d-flex align-items-center" style="min-height: 56px;">${scheme.title}</h5>
                                <p class="text-muted small mb-3" style="min-height: 64px;">${scheme.description}</p>
                                <small class="text-primary font-monospace d-block mb-3" style="min-height: 24px;"><i class="fa-solid fa-building me-1"></i>${scheme.department}</small>
                            </div>
                            <a href="/apply-page?service=${scheme.service_code}" class="btn btn-outline-primary rounded-pill fw-bold w-100 mt-auto">
                                Apply Now <i class="fa-solid fa-arrow-right ms-1"></i>
                            </a>
                        </div>
                    </div>
                `;
            });
        } else {
            container.innerHTML = `<div class="col-12 text-center text-muted py-4"><h5>No schemes found for selected state/sector criteria</h5></div>`;
        }
    } catch (err) {
        console.error(err);
    }
}

async function performTrackSearch() {
    const trackId = document.getElementById('trackInputId').value.trim();
    if (!trackId) {
        alert("Please enter a valid Tracking ID");
        return;
    }
    
    try {
        const res = await fetch(`/api/v1/applications/track/${trackId}`);
        const data = await res.json();
        
        if (res.ok) {
            document.getElementById('displayTrackingId').innerText = data.tracking_id;
            document.getElementById('trackServiceTitle').innerText = data.service_title;
            document.getElementById('displayStatus').innerText = data.status;
            document.getElementById('displayDate').innerText = `Submitted: ${data.created_at.split('T')[0]}`;
            
            const container = document.getElementById('timelineContainer');
            container.innerHTML = '';
            
            data.workflow_timeline.forEach(step => {
                const dotClass = step.status === 'COMPLETED' ? 'completed' : (step.status === 'IN_PROGRESS' ? 'in_progress' : 'pending');
                const badgeClass = step.status === 'COMPLETED' ? 'bg-success' : (step.status === 'IN_PROGRESS' ? 'bg-warning text-dark' : 'bg-secondary');
                
                container.innerHTML += `
                    <div class="timeline-item">
                        <div class="timeline-dot ${dotClass}"></div>
                        <div class="glass-card p-3 ms-2">
                            <div class="d-flex justify-content-between">
                                <h6 class="fw-bold text-dark mb-1">Stage ${step.stage_number}: ${step.stage_name}</h6>
                                <span class="badge ${badgeClass}">${step.status}</span>
                            </div>
                            <small class="text-primary fw-bold">${step.department_name}</small>
                            <p class="small text-muted mb-0 mt-1">${step.remarks}</p>
                        </div>
                    </div>
                `;
            });
            
            const auditContainer = document.getElementById('auditLogContainer');
            auditContainer.innerHTML = '';
            data.audit_logs.forEach(log => {
                auditContainer.innerHTML += `<div>[${log.timestamp.split('.')[0]}] ${log.action}: ${log.details}</div>`;
            });
            
        } else {
            alert(`Tracking Record Not Found: ${data.error}`);
        }
    } catch (err) {
        console.error(err);
        alert("Error fetching tracking status");
    }
}
