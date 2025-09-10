// ===== CHAT FUNCTIONALITY =====
async function sendMsg() {
    const inp = document.getElementById("msg");
    const text = inp.value.trim();
    if (!text) return;

    const chat = document.getElementById("chat");
    chat.innerHTML += `<div style="text-align:right;"><b>You:</b> ${text}</div>`;
    inp.value = "";
    chat.scrollTop = chat.scrollHeight;

    try {
        const resp = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        if (!resp.ok) throw new Error("API response error");

        const data = await resp.json();
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

// ===== SEARCH FUNCTIONALITY =====
async function doSearch() {
    const q = document.getElementById("query").value;
    const resp = await fetch("/search?q=" + encodeURIComponent(q));
    const data = await resp.json();
    const cont = document.getElementById("results");
    cont.innerHTML = "";
    for (const r of data.results) {
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `
          <h3>${r.name}</h3>
          <p><b>Domain:</b> ${r.domain}</p>
          <p><b>Grad Year:</b> ${r.grad_year}, <b>Exp:</b> ${r.exp} yrs</p>
          <p><b>Company:</b> ${r.company}</p>
          <a href="/profile/${r.id}">View Profile →</a>
        `;
        cont.appendChild(div);
    }
}

// ===== CHAT BOX TOGGLE =====
const chatToggle = document.querySelector(".chat");
const chatContainer = document.querySelector("#chat-container");
const chatClose = document.querySelector(".ct");

if (chatToggle && chatContainer && chatClose) {
    chatToggle.addEventListener("click", () => {
        chatContainer.style.display = "block";
        chatToggle.style.display = "none";
        requestAnimationFrame(() => chatContainer.classList.add("active"));
    });

    chatClose.addEventListener("click", () => {
        chatContainer.classList.remove("active");
        setTimeout(() => {
            chatContainer.style.display = "none";
            chatToggle.style.display = "block";
        }, 500);
    });
}

// ===== PROFILE LOADING & SESSION MANAGEMENT =====
function loadProfile() {
    const user = JSON.parse(localStorage.getItem("user") || "null");
    const div1 = document.querySelector(".div1");
    const profile = document.querySelector(".profile-card");
    const loginBtn = document.querySelector(".Login");

    if (user) {
        div1 && (div1.style.display = "none");
        profile && (profile.style.display = "block");
        loginBtn && (loginBtn.style.display = "none");

        document.getElementById("profileName").textContent = user.name || "User";
        document.getElementById("profileEmail").textContent = user.email || "";
        document.getElementById("profileRole").textContent = user.role || "";
        document.getElementById("profileCollege").textContent = user.college || "";
    } else {
        div1 && (div1.style.display = "block");
        profile && (profile.style.display = "none");
        loginBtn && (loginBtn.style.display = "block");
    }
}

loadProfile();

// ===== LOGOUT FUNCTION =====
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("user");
        window.location.href = "../static/assets/reg.html"; // login/register page
    });
}

// ===== LOGIN & REGISTER REDIRECT =====
const user = JSON.parse(localStorage.getItem("user") || "null");
if (!user && window.location.pathname !== "/static/assets/reg.html") {
    window.location.href = "../static/assets/reg.html"; // force login page
}