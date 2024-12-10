document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("newsletter-form");
  const emailInput = document.getElementById("email");
  const feedbackMessage = document.getElementById("feedback");

  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent form submission for demonstration

    const email = emailInput.value;

    // Simple email validation (basic check)
    if (validateEmail(email)) {
      feedbackMessage.textContent = "Thank you for subscribing!";
      feedbackMessage.style.color = "#4caf50"; // Green for success
      feedbackMessage.style.display = "block";
      emailInput.value = ""; // Clear input after submission
    } else {
      feedbackMessage.textContent = "Please enter a valid email address.";
      feedbackMessage.style.color = "#ff0202"; // Red for error
      feedbackMessage.style.display = "block";
    }
  });

  // Email validation function (simple regex)
  function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }
});
let currentSlide = 0;

function moveCarousel(direction) {
  const carousel = document.querySelector(".reviews-carousel");
  const cards = document.querySelectorAll(".review-card");
  const totalSlides = cards.length;

  currentSlide += direction;

  if (currentSlide < 0) {
    currentSlide = totalSlides - 1;
  } else if (currentSlide >= totalSlides) {
    currentSlide = 0;
  }

  const offset = -currentSlide * 100;
  carousel.style.transform = `translateX(${offset}%)`;
}

function toggleFaq(element) {
  const faqItem = element.parentElement;
  const faqAnswer = faqItem.querySelector(".faq-answer");
  const faqIcon = element.querySelector(".faq-icon");

  // Check if the answer is already open
  const isOpen = faqAnswer.style.maxHeight;

  // Close all other answers
  document.querySelectorAll(".faq-answer").forEach((answer) => {
    answer.style.maxHeight = null;
    answer.previousElementSibling.querySelector(".faq-icon").textContent = "+";
  });

  // Toggle current answer
  if (!isOpen) {
    faqAnswer.style.maxHeight = faqAnswer.scrollHeight + "px";
    faqIcon.textContent = "−";
  }
}
// Optional: Add animations on hover or other interactions if needed.
document.querySelectorAll('.step').forEach(step => {
    step.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-10px)';
    });
    step.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });
  
