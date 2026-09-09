document.addEventListener('DOMContentLoaded', () => {
    // 1. Application Evaluation Form Handler
    const evalForm = document.getElementById('evaluationForm');
    if (evalForm) {
        evalForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(evalForm);
            const data = Object.fromEntries(formData.entries());

            try {
                // Connects to actual scores backend endpoint
                const res = await fetch('/scores/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res.ok) {
                    alert('Evaluation submitted successfully!');
                    window.location.href = '/evaluator/dashboard';
                } else {
                    const error = await res.json();
                    alert('Error submitting evaluation: ' + (error.message || 'Server error'));
                }
            } catch (err) {
                alert('Network error. Unable to connect to the server.');
            }
        });
    }

    // 2. Milestone Verification Form Handler
    const milestoneForm = document.getElementById('milestoneForm');
    if (milestoneForm) {
        milestoneForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(milestoneForm);
            const data = Object.fromEntries(formData.entries());

            try {
                // Connects to actual milestones verification backend endpoint
                const res = await fetch('/milestones/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res.ok) {
                    alert('Milestone verification recorded successfully!');
                    window.location.href = '/evaluator/dashboard';
                } else {
                    const error = await res.json();
                    alert('Error updating milestone: ' + (error.message || 'Server error'));
                }
            } catch (err) {
                alert('Network error. Unable to connect to the server.');
            }
        });
    }

    // 3. Final Strategic Decision Form Handler
    const decisionForm = document.getElementById('decisionForm');
    if (decisionForm) {
        decisionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(decisionForm);
            const data = Object.fromEntries(formData.entries());

            try {
                // Connects to actual POST /decisions/ backend endpoint
                const res = await fetch('/decisions/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res.ok) {
                    alert('Final strategic recommendation recorded!');
                    window.location.href = '/evaluator/dashboard';
                } else {
                    const error = await res.json();
                    alert('Error submitting decision: ' + (error.message || 'Server error'));
                }
            } catch (err) {
                alert('Network error. Unable to connect to the server.');
            }
        });
    }
});