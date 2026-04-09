document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and dropdown options
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsHtml = details.participants.length
          ? `<div class="participants-list">${details.participants
              .map((email) => `
                <div class="participant-item">
                  <span class="participant-email">${email}</span>
                  <button
                    class="remove-participant-button"
                    data-activity="${name}"
                    data-email="${email}"
                    aria-label="Remove ${email}"
                  >
                    ✕
                  </button>
                </div>`)
              .join("")}</div>`
          : `<p class="no-participants">No participants yet.</p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p><strong>Participants:</strong></p>
            ${participantsHtml}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        activityCard.querySelectorAll(".remove-participant-button").forEach((button) => {
          button.addEventListener("click", async (event) => {
            event.preventDefault();

            const activityName = button.dataset.activity;
            const participantEmail = button.dataset.email;

            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(participantEmail)}`,
                {
                  method: "DELETE",
                }
              );

              const result = await response.json();

              if (response.ok) {
                messageDiv.textContent = result.message;
                messageDiv.className = "success";
                fetchActivities();
              } else {
                messageDiv.textContent = result.detail || "Failed to remove participant";
                messageDiv.className = "error";
              }

              messageDiv.classList.remove("hidden");
              setTimeout(() => {
                messageDiv.classList.add("hidden");
              }, 5000);
            } catch (error) {
              messageDiv.textContent = "Failed to remove participant. Please try again.";
              messageDiv.className = "error";
              messageDiv.classList.remove("hidden");
              console.error("Error removing participant:", error);
            }
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh the activities list
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();

  // Test Runner functionality
  const runTestsBtn = document.getElementById("run-tests-btn");
  const testResults = document.getElementById("test-results");
  const testStatus = document.getElementById("test-status");
  const testOutput = document.getElementById("test-output");

  runTestsBtn.addEventListener("click", async () => {
    // Disable button and show loading state
    runTestsBtn.disabled = true;
    runTestsBtn.textContent = "Running Tests...";

    testResults.classList.add("hidden");

    try {
      const response = await fetch("/run-tests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const result = await response.json();

      // Show results
      testResults.classList.remove("hidden");

      if (result.success) {
        testStatus.textContent = "✅ All tests passed!";
        testStatus.className = "success";
      } else {
        testStatus.textContent = "❌ Some tests failed";
        testStatus.className = "failure";
      }

      // Display test output
      let output = result.stdout;
      if (result.stderr) {
        output += "\n\nSTDERR:\n" + result.stderr;
      }

      // Add summary if available
      if (result.summary) {
        testStatus.textContent += ` (${result.summary})`;
      }

      testOutput.textContent = output;

    } catch (error) {
      testResults.classList.remove("hidden");
      testStatus.textContent = "❌ Failed to run tests";
      testStatus.className = "failure";
      testOutput.textContent = `Error: ${error.message}`;
      console.error("Error running tests:", error);
    } finally {
      // Re-enable button
      runTestsBtn.disabled = false;
      runTestsBtn.textContent = "Run Tests";
    }
  });
});
