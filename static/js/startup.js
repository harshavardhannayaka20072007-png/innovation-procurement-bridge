document.addEventListener("DOMContentLoaded", function () {
  const applicationForm = document.getElementById("applicationForm");
  const formResponse = document.getElementById("formResponse");

  if (applicationForm) {
    applicationForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const formData = new FormData(applicationForm);
      const data = {
        challenge_id: parseInt(formData.get("challenge_id")),
        solution: formData.get("solution"),
        technology: formData.get("technology"),
        timeline: formData.get("timeline")
      };

      try {
        const response = await fetch("/applications/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
          formResponse.innerHTML = `<div class="alert alert-success">${result.message || "Application submitted successfully!"}</div>`;
          applicationForm.reset();
        } else {
          formResponse.innerHTML = `<div class="alert alert-danger">${result.message || "Failed to submit application."}</div>`;
        }
      } catch (err) {
        console.error("Submission error:", err);
        formResponse.innerHTML = `<div class="alert alert-danger">Unable to submit application. Please try again.</div>`;
      }
    });
  }
});