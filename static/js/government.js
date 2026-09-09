document.addEventListener("DOMContentLoaded", function () {

    /* --------------------------------
       Table Search
    -------------------------------- */
    const searchInputs = document.querySelectorAll("[data-search-input]");

    searchInputs.forEach(function (input) {
        input.addEventListener("input", function () {
            const searchTerm = input.value.toLowerCase().trim();
            const rows = document.querySelectorAll("[data-search-row]");

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();

                row.style.display = text.includes(searchTerm)
                    ? ""
                    : "none";
            });
        });
    });


    /* --------------------------------
       Create Challenge
       POST /challenges/
    -------------------------------- */
    const challengeForm = document.getElementById("challengeForm");

    if (challengeForm) {
        challengeForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const submitButton =
                challengeForm.querySelector("[type='submit']");

            if (submitButton) {
                submitButton.disabled = true;
            }

            const formData = new FormData(challengeForm);

            const payload = {
                title: formData.get("title"),
                department: formData.get("department"),
                description: formData.get("description"),
                requirements: formData.get("requirements"),
                deadline: formData.get("deadline")
            };

            try {
                const response = await fetch("/challenges/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json().catch(function () {
                    return {};
                });

                if (!response.ok) {
                    throw new Error(
                        data.message ||
                        data.error ||
                        "Unable to create challenge."
                    );
                }

                window.location.href = "/government/challenges";

            } catch (error) {
                console.error(error);

                alert(
                    error.message ||
                    "Unable to create challenge. Please try again."
                );

                if (submitButton) {
                    submitButton.disabled = false;
                }
            }
        });
    }


    /* --------------------------------
       Publish Challenge
       PUT /challenges/<id>/publish
    -------------------------------- */
    const publishButtons =
        document.querySelectorAll("[data-publish-challenge]");

    publishButtons.forEach(function (button) {
        button.addEventListener("click", async function () {

            const challengeId =
                button.getAttribute("data-publish-challenge");

            if (!challengeId) {
                return;
            }

            const confirmed = window.confirm(
                "Are you sure you want to publish this challenge?"
            );

            if (!confirmed) {
                return;
            }

            button.disabled = true;

            try {
                const response = await fetch(
                    `/challenges/${challengeId}/publish`,
                    {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );

                const data = await response.json().catch(function () {
                    return {};
                });

                if (!response.ok) {
                    throw new Error(
                        data.message ||
                        data.error ||
                        "Unable to publish challenge."
                    );
                }

                window.location.reload();

            } catch (error) {
                console.error(error);

                alert(
                    error.message ||
                    "Unable to publish challenge."
                );

                button.disabled = false;
            }
        });
    });


    /* --------------------------------
       Application Review Actions
    -------------------------------- */
    const applicationButtons =
        document.querySelectorAll("[data-application-id]");

    applicationButtons.forEach(function (button) {
        button.addEventListener("click", function () {

            const url = button.getAttribute("data-url");

            if (url) {
                window.location.href = url;
            }
        });
    });


    /* --------------------------------
       Pilot Actions
    -------------------------------- */
    const pilotButtons =
        document.querySelectorAll("[data-pilot-id]");

    pilotButtons.forEach(function (button) {
        button.addEventListener("click", function () {

            const url = button.getAttribute("data-url");

            if (url) {
                window.location.href = url;
            }
        });
    });


    /* --------------------------------
       Confirmation Actions
    -------------------------------- */
    const confirmationElements =
        document.querySelectorAll("[data-confirm]");

    confirmationElements.forEach(function (element) {
        element.addEventListener("click", function (event) {

            const message =
                element.getAttribute("data-confirm");

            if (message && !window.confirm(message)) {
                event.preventDefault();
            }
        });
    });


    /* --------------------------------
       Disable Form While Submitting
    -------------------------------- */
    const disableOnSubmit =
        document.querySelectorAll("[data-disable-on-submit]");

    disableOnSubmit.forEach(function (form) {
        form.addEventListener("submit", function () {

            const controls =
                form.querySelectorAll("button, input[type='submit']");

            controls.forEach(function (control) {
                control.disabled = true;
            });
        });
    });

});