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
async function sendMsg() {
  let inp = document.getElementById("msg");
  let text = inp.value;
  if (!text) return;

  let chat = document.getElementById("chat");
  chat.innerHTML += `<div style="text-align:right;"><b>You:</b> ${text}</div>`;
  inp.value = "";

  // Send message to general chatbot API
  let resp = await fetch("/api/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: text})
  });

  let data = await resp.json();
  chat.innerHTML += `<div style="text-align:left;"><b>Lynq:</b> ${data.reply}</div>`;
  chat.scrollTop = chat.scrollHeight;}

async function doSearch() {
      let q = document.getElementById("query").value;
      let resp = await fetch("/search?q=" + encodeURIComponent(q));
      let data = await resp.json();
      let cont = document.getElementById("results");
      cont.innerHTML = "";
      for (let r of data.results) {
        let div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `
          <h3>${r.name} ${r.domain_emoji}</h3>
          <p><b>Domain:</b> ${r.domain}</p>
          <p><b>Grad Year:</b> ${r.grad_year}, <b>Exp:</b> ${r.exp} yrs</p>
          <p><b>Company:</b> ${r.company}</p>
          <p class="badges">${r.ach_badges}</p>
          <a href="/profile/${r.id}">View Profile →</a>
        `;
        cont.appendChild(div);
      }
    }