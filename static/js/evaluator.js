document.addEventListener('DOMContentLoaded', () => {
    // Strategic Decision Form Handler (POST /decisions/)
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