const toggleFormButton = document.getElementById("toggle-form");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const studentBtn = document.getElementById("student-btn");
const instructorBtn = document.getElementById("instructor-btn");
const roleMessage = document.getElementById("role-message");
const socialLoginText = document.getElementById("social-login-text");

// Toggle between Login and Signup forms
toggleFormButton.addEventListener("click", () => {
  if (signupForm.style.display === "none") {
    signupForm.style.display = "block";
    loginForm.style.display = "none";
    toggleFormButton.textContent = "Already have an account? Login";
    socialLoginText.textContent = "Or Sign Up with";
  } else {
    signupForm.style.display = "none";
    loginForm.style.display = "block";
    toggleFormButton.textContent = "Don't have an account? Sign Up";
    socialLoginText.textContent = "Or Login with";
  }
});

// Update role selection and message
studentBtn.addEventListener("click", () => {
  studentBtn.classList.add("active");
  instructorBtn.classList.remove("active");
  roleMessage.textContent =
    "Sign up to unlock new learning opportunities as a student!";
});

instructorBtn.addEventListener("click", () => {
  instructorBtn.classList.add("active");
  studentBtn.classList.remove("active");
  roleMessage.textContent =
    "Sign up to share knowledge and teach as an instructor!";
  // Email and Password validation

  document.addEventListener("DOMContentLoaded", function () {
    const signupForm = document.querySelector("#signup-form form");

    signupForm.addEventListener("submit", function (event) {
      // Get form inputs
      const name = document.querySelector("#signup-name").value.trim();
      const email = document.querySelector("#signup-email").value.trim();
      const password = document.querySelector("#signup-password").value.trim();

      // Name validation
      if (!name) {
        alert("Please enter your full name.");
        event.preventDefault();
        return;
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        alert("Please enter a valid email address.");
        event.preventDefault();
        return;
      }

      // Password validation (e.g., minimum 8 characters)
      if (password.length < 8) {
        alert("Password must be at least 8 characters long.");
        event.preventDefault();
        return;
      }

      // If all validations pass, allow form submission
      alert("All validations passed. Submitting form!");
    });
  });
});
