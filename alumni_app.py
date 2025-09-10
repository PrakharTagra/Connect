from flask import Flask, render_template, request, jsonify
import pandas as pd
import os, re, time
from functools import lru_cache
from dotenv import load_dotenv
import requests

# ---------------- Init Flask ----------------
app = Flask(__name__)

# ---------------- Load Env ----------------
load_dotenv("./static/assets/hi.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")

if not GEMINI_API_KEY or not GEMINI_API_URL:
    raise ValueError("GEMINI_API_KEY or GEMINI_API_URL not found in hi.env!")

# ---------------- Load CSV ----------------
CSV_PATH = "alumni_dataset_20.csv"
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV file {CSV_PATH} not found!")

df = pd.read_csv(CSV_PATH)
for col in ["Name", "Domain", "Projects", "Skills", "Achievements", "Current_Position"]:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str)
if "Graduation_Year" not in df.columns:
    df["Graduation_Year"] = 2020
if "Years_of_Experience" not in df.columns:
    df["Years_of_Experience"] = 0
if "id" not in df.columns:
    df = df.reset_index().rename(columns={"index": "id"})
# ---------------- Gemini Query (with retry) ----------------
@lru_cache(maxsize=128)
def query_gemini(prompt, max_tokens=200, retries=5, delay=2):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens}
    }

    for attempt in range(retries):
        try:
            time.sleep(1)  # avoid rate-limit
            resp = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            out = resp.json()
            return out["candidates"][0]["content"]["parts"][0]["text"]

        except Exception:
            time.sleep(delay * (attempt + 1))
            continue

    return "(Service is busy, please try again later.)"

# ---------------- Routes ----------------
@app.route("/")
def index():
    cards = df.to_dict(orient="records")
    return render_template("index.html", cards=cards)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"reply": "Say something 💬"})
    
    # Optional: include relevant alumni in the prompt
    relevant_alumni = df[df.apply(lambda r: msg.lower() in r["Name"].lower() or
                                                msg.lower() in r["Domain"].lower(), axis=1)].head(5)
    
    prompt = "You are Lynq, a helpful alumni chatbot.\n"
    for _, r in relevant_alumni.iterrows():
        prompt += f"- {r['Name']} ({r['Domain']}, {r['Current_Position']}), Skills: {r['Skills']}\n"
    prompt += f"\nUser says: {msg}\nRespond helpfully."
    
    reply = query_gemini(prompt)
    return jsonify({"reply": reply})

# Make helpers available in Jinja templates
@app.route("/alumnisearch")
def alumnisearch():
    # Show some sample alumni cards initially
    cards = df.sample(min(12, len(df))).to_dict(orient="records")
    return render_template("alumnisearch.html", cards=cards)

# ---------------- Profile Page ----------------
@app.route("/profile/<int:pid>")
def profile_page(pid):
    # Get the alumni data
    row = df[df["id"] == pid]
    if row.empty:
        return "Profile not found", 404
    r = row.iloc[0].to_dict()

    # Generate bio using Gemini API (optional)
    prompt = (
        f"Write a short engaging alumni bio for {r.get('Name')}.\n"
        f"Domain: {r.get('Domain')}\n"
        f"Skills: {r.get('Skills')}\n"
        f"Achievements: {r.get('Achievements')}\n"
        f"Current Position: {r.get('Current_Position')}"
    )
    bio = query_gemini(prompt)

    return render_template("profile.html", alum=r, bio=bio)

# ---------------- Search API (for alumni search dynamic search) ----------------
@app.route("/search")
def api_search():
    q = request.args.get("q", "")
    tokens = [t.strip().lower() for t in re.split(r"[\s,;|/]+", q) if t.strip()]
    mask = pd.Series([False]*len(df))
    for t in tokens:
        mask |= df["Name"].str.lower().str.contains(re.escape(t))
        mask |= df["Domain"].str.lower().str.contains(re.escape(t))
        mask |= df["Skills"].str.lower().str.contains(re.escape(t))
        mask |= df["Current_Position"].str.lower().str.contains(re.escape(t))
    results = df[mask]
    items = []
    for _, r in results.iterrows():
        items.append({
            "id": int(r["id"]),
            "name": r["Name"],
            "domain": r["Domain"],
            "grad_year": r["Graduation_Year"],
            "exp": r["Years_of_Experience"],
            "company": r["Current_Position"]
        })
    return jsonify({"results": items})
# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
# ---------------- Alumni Search Page ----------------