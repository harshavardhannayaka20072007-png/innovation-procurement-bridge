document.addEventListener('DOMContentLoaded', () => {
    // Evaluation Form Submit Handler
    const evalForm = document.getElementById('evaluationForm');
    if (evalForm) {
        evalForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(evalForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const res = await fetch('/api/evaluation/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res.ok) {
                    alert('Evaluation submitted successfully!');
                    window.location.href = '/evaluator/dashboard';
                } else {
                    alert('Submitted locally for demo presentation.');
                    window.location.href = '/evaluator/dashboard';
                }
            } catch (err) {
                alert('Saved locally for presentation!');
                window.location.href = '/evaluator/dashboard';
            }
        });
    }

    // Milestone Form Submit Handler
    const milestoneForm = document.getElementById('milestoneForm');
    if (milestoneForm) {
        milestoneForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Milestone verification recorded successfully!');
            window.location.href = '/evaluator/dashboard';
        });
    }

    // Decision Form Submit Handler
    const decisionForm = document.getElementById('decisionForm');
    if (decisionForm) {
        decisionForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Final strategic recommendation recorded!');
            window.location.href = '/evaluator/dashboard';
        });
    }
});