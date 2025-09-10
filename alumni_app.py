from flask import Flask, render_template, request, jsonify
import pandas as pd
import os, re, time
from functools import lru_cache
from dotenv import load_dotenv
import requests

app = Flask(__name__)

load_dotenv("./static/assets/hi.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")
if not GEMINI_API_KEY or not GEMINI_API_URL:
    raise ValueError("GEMINI_API_KEY or GEMINI_API_URL not found!")

CSV_PATH = "alumni_dataset_20.csv"
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"{CSV_PATH} not found!")

df = pd.read_csv("alumni_dataset_20.csv")
required_cols = ["Name", "Domain", "Projects", "Skills", "Achievements", "Current_Position"]
for col in required_cols:
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].fillna("").astype(str)
if "Graduation_Year" not in df.columns:
    df["Graduation_Year"] = 2020
if "Years_of_Experience" not in df.columns:
    df["Years_of_Experience"] = 0
if "id" not in df.columns:
    df = df.reset_index().rename(columns={"index": "id"})

@lru_cache(maxsize=128)
def query_gemini(prompt, max_tokens=200, retries=5, delay=2):
    headers = {"Content-Type": "application/json","x-goog-api-key": GEMINI_API_KEY}
    data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": max_tokens}}
    for attempt in range(retries):
        try:
            resp = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            out = resp.json()
            return out["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            time.sleep(delay * (attempt + 1))
            continue
    return "(Service busy, try again later.)"

def clean_reply(text):
    text = re.sub(r"[*_#>`-]+", "", text)
    text = re.sub(r"[^.]*\b(could you|tell me|need more|please provide|once I have)\b[^.]*\.", "", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()

@app.route("/")
def index():
    cards = df.to_dict(orient="records")
    return render_template("index.html", cards=cards)

@app.route("/alumnisearch")
def alumnisearch():
    cards = df.to_dict(orient="records")
    return render_template("alumnisearch.html", cards=cards)

@app.route("/profile/<int:pid>")
def profile_page(pid):
    row = df[df["id"] == pid]
    if row.empty:
        return "Profile not found", 404
    r = row.iloc[0].to_dict()
    prompt = (
        f"Write a short engaging alumni bio for {r.get('Name')}.\n"
        f"Domain: {r.get('Domain')}\n"
        f"Skills: {r.get('Skills')}\n"
        f"Achievements: {r.get('Achievements')}\n"
        f"Current Position: {r.get('Current_Position')}"
    )
    bio = query_gemini(prompt)
    bio = clean_reply(bio)
    return render_template("profile.html", alum=r, bio=bio)

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
    results = df[mask].head(12)
    items = []
    for _, r in results.iterrows():
        items.append({
            "id": int(r["id"]),
            "name": r["Name"],
            "domain": r["Domain"],
            "grad_year": r["Graduation_Year"],
            "exp": r["Years_of_Experience"],
            "company": r["Current_Position"],
            "projects": r["Projects"]
        })
    return jsonify({"results": items})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"reply": "Say something."})
    relevant_alumni = df[df.apply(lambda r: msg.lower() in r["Name"].lower() or msg.lower() in r["Domain"].lower(), axis=1)].head(5)
    prompt = "You are Lynq, a helpful alumni chatbot.\n"
    for _, r in relevant_alumni.iterrows():
        prompt += f"{r['Name']} ({r['Domain']}, {r['Current_Position']}), Skills: {r['Skills']}, Experience: {r['Years_of_Experience']} years.\n"
    prompt += f"User says: {msg}\nReply in 2-3 plain sentences recommending alumni."
    reply = query_gemini(prompt)
    reply = clean_reply(reply)
    return jsonify({"reply": reply})

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.json or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"results": [], "reply": "Please describe what you are looking for."})
    tokens = [t.strip().lower() for t in re.split(r"[\s,;|/]+", msg) if t.strip()]
    scores = []
    for _, r in df.iterrows():
        score = 0
        text_fields = " ".join([r.get(c,"") for c in ["Name","Domain","Skills","Projects","Achievements","Current_Position"]]).lower()
        for t in tokens:
            if t in text_fields:
                score += 2
            if t.isdigit() and int(r.get("Years_of_Experience",0)) >= int(t):
                score += 3
        scores.append((score, r.to_dict()))
    scores = sorted(scores, key=lambda x: x[0], reverse=True)
    top_alumni = [s[1] for s in scores if s[0] > 0][:5]
    if not top_alumni:
        top_alumni = df.sample(min(3, len(df))).to_dict(orient="records")
    summary_prompt = f"User query: {msg}\n\nBest matching alumni:\n"
    for alum in top_alumni:
        summary_prompt += f"{alum['Name']} ({alum['Domain']}, {alum['Current_Position']}), Skills: {alum['Skills']}, Experience: {alum['Years_of_Experience']} years.\n"
    ai_reply = query_gemini(
        f"You are Lynq, an alumni recommendation bot. "
        f"Never ask the user questions. "
        f"Do not use bullet points, stars, or markdown. "
        f"Write exactly 2-3 plain sentences recommending the best alumni below.\n\n"
        f"{summary_prompt}"
    )
    ai_reply = clean_reply(ai_reply)
    return jsonify({"results": top_alumni, "reply": ai_reply})

if __name__ == "__main__":
    app.run(debug=True, port=5000)