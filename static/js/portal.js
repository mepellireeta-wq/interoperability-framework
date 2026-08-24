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
                    <div class="col-md-6 col-lg-4">
                        <div class="glass-card h-100 p-4 d-flex flex-column justify-content-between">
                            <div>
                                <div class="d-flex align-items-center mb-3">
                                    <span class="badge ${domainBadgeClass} rounded-pill me-2">${scheme.domain || 'Multi-Sector'}</span>
                                    <span class="badge bg-secondary rounded-pill">${scheme.integration_type}</span>
                                </div>
                                <h5 class="fw-bold text-dark">${scheme.title}</h5>
                                <p class="text-muted small">${scheme.description}</p>
                                <small class="text-primary font-monospace d-block mb-2"><i class="fa-solid fa-building me-1"></i>${scheme.department}</small>
                            </div>
                            <a href="/apply-page?service=${scheme.service_code}" class="btn btn-outline-primary rounded-pill fw-bold w-100 mt-3">
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
