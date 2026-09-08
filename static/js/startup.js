document.addEventListener("DOMContentLoaded", () => {
  // Handle Application Submission Form
  const applyForm = document.getElementById("startup-apply-form");
  if (applyForm) {
    applyForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(applyForm);
      const data = Object.fromEntries(formData.entries());

      try {
        const response = await fetch("/startup/apply", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        const result = await response.json();
        if (result.success) {
          alert("Application submitted successfully!");
          window.location.href = "/startup/applications";
        } else {
          alert("Error: " + result.message);
        }
      } catch (err) {
        console.error("Submission failed:", err);
      }
    });
  }

  // Dynamic Score Calculation Preview
  const calculateScoreBtn = document.getElementById("calc-score-btn");
  if (calculateScoreBtn) {
    calculateScoreBtn.addEventListener("click", () => {
      // Mock score preview logic for UI testing
      const scorePreview = document.getElementById("score-preview");
      if (scorePreview) {
        scorePreview.innerText = "Estimated Readiness Score: 88/100";
      }
    });
  }
});
