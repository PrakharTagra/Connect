async function sendMsg() {
    let inp = document.getElementById("msg");
    let text = inp.value.trim();
    if (!text) return;

    let chat = document.getElementById("chat");
    chat.innerHTML += `<div style="text-align:right;"><b>You:</b> ${text}</div>`;
    inp.value = "";
    chat.scrollTop = chat.scrollHeight;

    try {
        let resp = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: text})
        });

        if (!resp.ok) throw new Error("API response error");

        let data = await resp.json();
        chat.innerHTML += `<div style="text-align:left;"><b>Lynq:</b> ${data.reply}</div>`;
        chat.scrollTop = chat.scrollHeight;
    } catch (err) {
        chat.innerHTML += `<div style="color:red; text-align:left;"><b>Lynq:</b> Sorry, something went wrong. Try again.</div>`;
        chat.scrollTop = chat.scrollHeight;
        console.error(err);
    }
}

document.getElementById("msg").addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMsg();
});


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
const chat = document.querySelector(".chat");
const chat_container = document.querySelector("#chat-container");
const ct = document.querySelector(".ct");

chat.addEventListener("click", () => {
  chat_container.style.display = "block";
  chat.style.display = "none";
  requestAnimationFrame(() => {
    chat_container.classList.add("active");
  });
});

ct.addEventListener("click", () => {
  chat_container.classList.remove("active");
  setTimeout(() => {
    chat_container.style.display = "none";
    chat.style.display = "block";
  }, 500);
});
function loadProfile(){
      const user = JSON.parse(localStorage.getItem("user") || "null");
      if (user) {
        document.getElementById("profileName").textContent = user.name || "User";
        document.getElementById("profileEmail").textContent = user.email || "";
        document.getElementById("profileRole").textContent = user.role ? user.role : "";
        document.getElementById("profileCollege").textContent = user.college ? user.college : "";
      } else {
        document.getElementById("profileName").textContent = "Guest";
        document.getElementById("profileEmail").textContent = "Not logged in";
        document.getElementById("profileRole").textContent = "";
        document.getElementById("profileCollege").textContent = "";
      }
    }

    document.getElementById("logoutBtn").addEventListener("click", function(){
      localStorage.removeItem("user");
      // go back to login page
      window.location.href = "login.html";
    });

    loadProfile();
let div1=document.querySelector(".div1")
let profile=document.querySelector(".profile-card");
let login=document.querySelector(".Login")
window.addEventListener("DOMContentLoaded", function () {
    const user = JSON.parse(localStorage.getItem("user") || "null");

    if (user) {
      div1.style.display="none";
      profile.style.display="block"
      login.style.display="none"
    }
  });