// Frontend JavaScript for Maharashtra Interoperability Portal

document.addEventListener('DOMContentLoaded', function() {
    
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
        
        // Auto-search if URL query parameter 'id' exists
        const urlParams = new URLSearchParams(window.location.search);
        const searchId = urlParams.get('id');
        if (searchId) {
            document.getElementById('trackInputId').value = searchId;
            performTrackSearch();
        }
    }
});

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
            
            // Build timeline
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
            
            // Build audit logs
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
