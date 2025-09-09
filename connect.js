particlesJS("particles-js", {
    "particles": {
      "number": { "value": 80 },
      "color": { "value": "#ffffff" },
      "shape": { "type": "circle" },
      "opacity": {
        "value": 0.8,
        "random": true
      },
      "size": {
        "value": 10,
        "random": true
      },
      "move": {
        "enable": true,
        "speed": 1,
        "direction": "top",
        "out_mode": "out"
      }
    },
    "interactivity": { "detect_on": "canvas", "events": { "onhover": { "enable": false } } },
    "retina_detect": true
  });

  // Simple scroll animation
document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".grid-card");
  
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
          }
        });
      },
      { threshold: 0.2 }
    );
  
    cards.forEach(card => {
      observer.observe(card);
    });
  });

  async function handleLogin(event) {
      event.preventDefault();
      
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;

      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        
        if (response.ok) {
          // Store token in localStorage
          localStorage.setItem('token', data.token);
          // Redirect to dashboard or home page
          window.location.href = '/dashboard.html';
        } else {
          alert(data.message);
        }
      } catch (err) {
        console.error('Error:', err);
        alert('An error occurred during login');
      }
    }