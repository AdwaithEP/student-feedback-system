const feedbackForm = document.getElementById("feedbackForm");

feedbackForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    if (!formData.get("rating")) {
        alert("Please select a rating!");
        return;
    }

    fetch("/", {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        alert("Feedback submitted successfully!");
        feedbackForm.reset();

        // Reset stars visually
        const stars = document.querySelectorAll(".rating input");
        stars.forEach(star => star.checked = false);
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    });
});