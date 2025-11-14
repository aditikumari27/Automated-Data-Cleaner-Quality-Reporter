/*
 * script.js
 * Contains original form submission logic + new page interactivity
 */

document.addEventListener('DOMContentLoaded', function() {

  // --- ORIGINAL SCRIPT (Preserved) ---
  // Disables the submit button to prevent multiple submissions
  const form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', function() {
      const btn = form.querySelector('button[type=submit]');
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Cleaning...';
        // Add a pulsing glow effect while cleaning
        btn.style.animation = 'pulsing 1.5s infinite';
      }
    });
  }

  // --- NEW: Custom File Input Label ---
  // Shows the selected filename in the custom input
  const fileInput = document.querySelector('input[type="file"]');
  if (fileInput) {
    const fileLabel = document.querySelector('label[for="file-upload"]');
    if (fileLabel) {
      fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
          fileLabel.textContent = this.files[0].name;
          fileLabel.style.borderColor = '#00ffff'; // Use accent color
          fileLabel.style.color = '#00ffff';
        } else {
          fileLabel.textContent = 'Select CSV file';
          fileLabel.style.borderColor = 'rgba(255, 255, 255, 0.1)';
          fileLabel.style.color = '#ccc';
        }
      });
    }
  }

  // --- NEW: Single-Page App "Page" Navigation ---
  const navLinks = document.querySelectorAll('.nav-link');
  const pages = document.querySelectorAll('.page-content');

  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const pageId = this.dataset.page;

      // Remove active class from all links and pages
      navLinks.forEach(nav => nav.classList.remove('active'));
      pages.forEach(page => page.classList.remove('active'));

      // Add active class to the clicked link and corresponding page
      this.classList.add('active');
      document.getElementById('page-' + pageId).classList.add('active');
    });
  });


  // --- NEW: Data-Type Dash Game Logic ---
  const gameData = [
    { value: "DataLoom", type: "String" },
    { value: "1984", type: "Integer" },
    { value: "true", type: "Boolean" },
    { value: "3.14159", type: "Float" },
    { value: "user@domain.com", type: "Email" },
    { value: "Hello World!", type: "String" },
    { value: "42", type: "Integer" },
    { value: "-500", type: "Integer" },
    { value: "false", type: "Boolean" },
    { value: "0.05", type: "Float" },
    { value: "support@dataloom.ai", type: "Email" },
    { value: "CSV", type: "String" },
    { value: "1", type: "Integer" },
    { value: "0", type: "Integer" },
    { value: "9.81", type: "Float" },
    { value: "test.email@example.co.uk", type: "Email" },
    { value: "JavaScript", type: "String" }
  ];

  const timerDisplay = document.getElementById('game-timer');
  const scoreDisplay = document.getElementById('game-score');
  const valueBox = document.getElementById('game-value-box');
  const messageDisplay = document.getElementById('game-message');
  const typeButtons = document.querySelectorAll('.game-type-btn');
  const startButton = document.getElementById('game-start-btn');

  let score = 0;
  let timeLeft = 20;
  let gameTimer;
  let currentItem = null;

  function initGame() {
    score = 0;
    timeLeft = 20;
    scoreDisplay.textContent = `Score: ${score}`;
    timerDisplay.textContent = `Time: ${timeLeft}`;
    messageDisplay.textContent = "";
    valueBox.textContent = "Get Ready!";
    startButton.textContent = "Start Game";
    startButton.disabled = false;
    typeButtons.forEach(btn => btn.disabled = true);
  }

  function startGame() {
    startButton.disabled = true;
    typeButtons.forEach(btn => btn.disabled = false);
    score = 0;
    timeLeft = 20;
    scoreDisplay.textContent = `Score: ${score}`;
    timerDisplay.textContent = `Time: ${timeLeft}`;
    
    nextItem();
    
    gameTimer = setInterval(() => {
      timeLeft--;
      timerDisplay.textContent = `Time: ${timeLeft}`;
      if (timeLeft <= 0) {
        endGame();
      }
    }, 1000);
  }

  function endGame() {
    clearInterval(gameTimer);
    typeButtons.forEach(btn => btn.disabled = true);
    startButton.disabled = false;
    startButton.textContent = "Play Again?";
    valueBox.textContent = `Game Over! Final Score: ${score}`;
    messageDisplay.textContent = "";
  }

  function nextItem() {
    currentItem = gameData[Math.floor(Math.random() * gameData.length)];
    valueBox.textContent = currentItem.value;
  }

  function checkAnswer(e) {
    const selectedType = e.target.dataset.type;
    
    if (selectedType === currentItem.type) {
      score++;
      scoreDisplay.textContent = `Score: ${score}`;
      messageDisplay.textContent = "Correct!";
      messageDisplay.className = "correct";
    } else {
      messageDisplay.textContent = "Wrong!";
      messageDisplay.className = "wrong";
    }
    
    // Briefly show the message
    setTimeout(() => {
      messageDisplay.textContent = "";
      messageDisplay.className = "";
      if (timeLeft > 0) {
        nextItem();
      }
    }, 400);
  }

  // Event Listeners for Game
  if (startButton) {
    startButton.addEventListener('click', startGame);
    typeButtons.forEach(btn => {
      btn.addEventListener('click', checkAnswer);
    });
    
    // Initialize game on load
    initGame();
  }


  // --- NEW: Add pulsing animation to CSS (needed for submit button) ---
  const styleSheet = document.createElement("style");
  styleSheet.type = "text/css";
  styleSheet.innerText = `
    @keyframes pulsing {
      0% { box-shadow: 0 0 15px var(--color-accent); }
      50% { box-shadow: 0 0 30px var(--color-accent); }
      100% { box-shadow: 0 0 15px var(--color-accent); }
    }
  `;
  document.head.appendChild(styleSheet);

});