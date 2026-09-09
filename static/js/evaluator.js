// Evaluator Scoring Dynamic Live Calculation
document.addEventListener("DOMContentLoaded", function () {
    const scoreInputs = document.querySelectorAll(".score-input");
    const totalScoreDisplay = document.getElementById("totalScoreDisplay");

    if (scoreInputs.length > 0 && totalScoreDisplay) {
        function updateTotalScore() {
            let sum = 0;
            scoreInputs.forEach(input => {
                sum += parseInt(input.value || 0, 10);
            });
            totalScoreDisplay.textContent = sum;
        }

        scoreInputs.forEach(input => {
            input.addEventListener("input", updateTotalScore);
        });
        updateTotalScore();
    }
});
