# from flask import Flask, request, jsonify, render_template, send_from_directory
# import pandas as pd
# import os, re, requests
# import random

# app = Flask(__name__)

# # ---------------- GEMINI KEYS ----------------
# GEMINI_API_KEY = "AIzaSyCAdAgEP4eaf6j3zLOkxN678Hvf98zXn4s"
# GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

# # ---------------- Dataset ----------------
# CSV_PATH = "alumni_dataset_20.csv"
# if not os.path.exists(CSV_PATH):
#     raise FileNotFoundError(f"CSV file {CSV_PATH} not found!")

# df = pd.read_csv(CSV_PATH)
# for col in ["Name", "Domain", "Projects", "Skills", "Achievements", "Current_Position"]:
#     if col in df.columns:
#         df[col] = df[col].fillna("").astype(str)

# if "Graduation_Year" not in df.columns:
#     df["Graduation_Year"] = 2020
# if "Years_of_Experience" not in df.columns:
#     df["Years_of_Experience"] = 0
# if "id" not in df.columns:
#     df = df.reset_index().rename(columns={"index": "id"})

# if "Email" not in df.columns:
#     def make_email(name, year):
#         user = re.sub(r"[^a-z0-9]", "", name.lower().split()[0])
#         return f"{user}{int(year)%100}@alumni.example.com"
#     df["Email"] = df.apply(lambda r: make_email(r["Name"], r["Graduation_Year"]), axis=1)

# if "Instagram" not in df.columns:
#     df["Instagram"] = df["Name"].apply(lambda n: "@" + re.sub(r"\s+", "", n.split()[0].lower()) + "_inst")
# if "X_handle" not in df.columns:
#     df["X_handle"] = df["Name"].apply(lambda n: "@" + re.sub(r"\s+", "", n.split()[0].lower()) + "x")

# # ---------------- Emoji Helpers ----------------
# DOMAIN_EMOJI = {"Computer Science": "💻", "CS": "💻", "IT": "💻",
#                 "Electronics": "📡", "Mechanical": "⚙️", "Civil": "🏗️",
#                 "Biotech": "🧬", "Electrical": "🔌"}

# ACHIEV_EMOJI = {"IAS": "🏛️", "Startup": "🚀", "Founder": "🚀",
#                 "Patent": "📜", "Published": "📚", "Award": "🏆", "Fellowship": "🎓"}

# def get_domain_emoji(domain):
#     for k,v in DOMAIN_EMOJI.items():
#         if k.lower() in domain.lower():
#             return v
#     return "🔧"

# def achievement_badges(ach):
#     badges = [v for k,v in ACHIEV_EMOJI.items() if k.lower() in str(ach).lower()]
#     if ach and not badges:
#         badges.append("🌟")
#     return " ".join(badges)

# # ---------------- Gemini API ----------------
# def query_gemini(prompt, max_tokens=800):
#     headers = {
#         "Content-Type": "application/json",
#         "x-goog-api-key": GEMINI_API_KEY
#     }
#     data = {
#         "contents": [{"parts": [{"text": prompt}]}],
#         "generationConfig": {"maxOutputTokens": max_tokens}
#     }
#     try:
#         resp = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=20)
#         resp.raise_for_status()
#         out = resp.json()
#         return out["candidates"][0]["content"]["parts"][0]["text"]
#     except Exception as e:
#         return f"(Gemini error ❌: {e})"

# # ---------------- Search ----------------
# # def search_alumni_core(q):
# #     if not q or not str(q).strip():
# #         return df.copy().head(50)
# #     s = str(q).strip()
# #     m = re.match(r"^\s*([<>]=?)\s*(\d+)\s*$", s)
# #     try:
# #         if m:
# #             op, num = m.group(1), int(m.group(2))
# #             if op == ">": return df[df["Years_of_Experience"] > num]
# #             if op == ">=": return df[df["Years_of_Experience"] >= num]
# #             if op == "<": return df[df["Years_of_Experience"] < num]
# #             if op == "<=": return df[df["Years_of_Experience"] <= num]
# #     except: pass
# #     if s.isdigit():
# #         num = int(s)
# #         by_year = df[df["Graduation_Year"] == num]
# #         return by_year if not by_year.empty else df[df["Years_of_Experience"] == num]

# #     tokens = [t.strip().lower() for t in re.split(r"[\s,;|/]+", s) if t.strip()]
# #     mask = pd.Series([False]*len(df))
# #     for t in tokens:
# #         mask |= df["Name"].str.lower().str.contains(re.escape(t), na=False)
# #         mask |= df["Current_Position"].str.lower().str.contains(re.escape(t), na=False)
# #         mask |= df["Domain"].str.lower().str.contains(re.escape(t), na=False)
# #         mask |= df["Skills"].str.lower().str.contains(re.escape(t), na=False)
# #         mask |= df["Achievements"].str.lower().str.contains(re.escape(t), na=False)
# #     return df[mask].head(50)

# # @app.route("/")
# # def alumnisearch():
# #     cards = df.sample(min(12, len(df))).to_dict(orient="records")
# #     return render_template("alumnisearch.html", sample_count=len(df), cards=cards)

# # @app.route("/search")
# # def api_search():
# #     q = request.args.get("q", "").strip()
# #     results_df = search_alumni_core(q)
# #     items = []
# #     for _, r in results_df.iterrows():
# #         top_skill = (r["Skills"].split(",")[0].strip()) if r["Skills"] else ""
# #         items.append({
# #             "id": int(r["id"]),
# #             "name": r["Name"],
# #             "domain": r["Domain"],
# #             "domain_emoji": get_domain_emoji(r["Domain"]),
# #             "grad_year": int(r.get("Graduation_Year", 0)),
# #             "exp": int(r.get("Years_of_Experience", 0)),
# #             "company": r.get("Current_Position", ""),
# #             "ach_badges": achievement_badges(r.get("Achievements", "")),
# #             "top_skill": top_skill,
# #             "projects": r.get("Projects", "")[:140]
# #         })
# #     return jsonify({"count": len(items), "results": items})

# # @app.route("/profile/<int:pid>")
# # def profile_page(pid):
# #     row = df[df["id"] == pid]
# #     if row.empty:
# #         return "Profile not found", 404
# #     r = row.iloc[0].to_dict()
# #     prompt = f"Write a short engaging alumni bio for {r.get('Name')}.\nDomain: {r.get('Domain')}\nSkills: {r.get('Skills')}\nAchievements: {r.get('Achievements')}\nCurrent Position: {r.get('Current_Position')}"
# #     bio = query_gemini(prompt)
# #     return render_template("profile.html", alum=r, bio=bio)

# # @app.route("/api/chat", methods=["POST"])
# # def api_chat():
# #     data = request.json or {}
# #     msg = (data.get("message") or "").strip()
# #     pid = data.get("profile_id")
# #     if not msg:
# #         return jsonify({"reply": "Say something 💬"})
# #     if pid is not None:
# #         row = df[df["id"] == int(pid)]
# #         if not row.empty:
# #             r = row.iloc[0].to_dict()
# #             prompt = f"You are alumni {r['Name']}. User says: {msg}. Respond helpfully."
# #             reply = query_gemini(prompt, max_tokens=200)
# #             return jsonify({"reply": reply})
# #     return jsonify({"reply": query_gemini('Answer: ' + msg, max_tokens=200)})

# # @app.route("/download_csv")
# # def download_csv():
# #     return send_from_directory(".", CSV_PATH, as_attachment=True)

# @app.route("/")
# def index():
#     cards = df.sample(min(12, len(df))).to_dict(orient="records")
#     return render_template("index.html", sample_count=len(df), cards=cards)

# @app.route("/search")
# def api_search():
#     q = request.args.get("q", "").strip()
#     results_df = search_alumni_core(q)
#     items = []
#     for _, r in results_df.iterrows():
#         top_skill = (r["Skills"].split(",")[0].strip()) if r["Skills"] else ""
#         items.append({
#             "id": int(r["id"]),
#             "name": r["Name"],
#             "domain": r["Domain"],
#             "domain_emoji": get_domain_emoji(r["Domain"]),
#             "grad_year": int(r.get("Graduation_Year", 0)),
#             "exp": int(r.get("Years_of_Experience", 0)),
#             "company": r.get("Current_Position", ""),
#             "ach_badges": achievement_badges(r.get("Achievements", "")),
#             "top_skill": top_skill,
#             "projects": r.get("Projects", "")[:140]
#         })
#     return jsonify({"count": len(items), "results": items})

# @app.route("/profile/<int:pid>")
# def profile_page(pid):
#     row = df[df["id"] == pid]
#     if row.empty:
#         return "Profile not found", 404
#     r = row.iloc[0].to_dict()
#     prompt = f"Write a short engaging alumni bio for {r.get('Name')}.\nDomain: {r.get('Domain')}\nSkills: {r.get('Skills')}\nAchievements: {r.get('Achievements')}\nCurrent Position: {r.get('Current_Position')}"
#     bio = query_gemini(prompt)
#     return render_template("profile.html", alum=r, bio=bio)

# @app.route("/api/chat", methods=["POST"])
# def api_chat():
#     data = request.json or {}
#     msg = (data.get("message") or "").strip()
#     pid = data.get("profile_id")
#     if not msg:
#         return jsonify({"reply": "Say something 💬"})
#     if pid is not None:
#         row = df[df["id"] == int(pid)]
#         if not row.empty:
#             r = row.iloc[0].to_dict()
#             prompt = f"You are alumni {r['Name']}. User says: {msg}. Respond helpfully."
#             reply = query_gemini(prompt, max_tokens=200)
#             return jsonify({"reply": reply})
#     return jsonify({"reply": query_gemini('Answer: ' + msg, max_tokens=200)})

# @app.route("/download_csv")
# def download_csv():
#     return send_from_directory(".", CSV_PATH, as_attachment=True)
# # make functions available in templates
# app.jinja_env.globals.update(get_domain_emoji=get_domain_emoji, achievement_badges=achievement_badges)

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import os, re, requests, time
from dotenv import load_dotenv
from functools import lru_cache

# ---------------- Init Flask ----------------
app = Flask(__name__)

# ---------------- Load Env ----------------
load_dotenv("hi.env")
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

# ---------------- Emoji Helpers ----------------
DOMAIN_EMOJI = {"Computer Science": "💻", "CS": "💻", "IT": "💻",
                "Electronics": "📡", "Mechanical": "⚙️", "Civil": "🏗️",
                "Biotech": "🧬", "Electrical": "🔌"}

ACHIEV_EMOJI = {"IAS": "🏛️", "Startup": "🚀", "Founder": "🚀",
                "Patent": "📜", "Published": "📚", "Award": "🏆", "Fellowship": "🎓"}

def get_domain_emoji(domain):
    for k,v in DOMAIN_EMOJI.items():
        if k.lower() in domain.lower():
            return v
    return "🔧"

def achievement_badges(ach):
    badges = [v for k,v in ACHIEV_EMOJI.items() if k.lower() in str(ach).lower()]
    if ach and not badges:
        badges.append("🌟")
    return " ".join(badges)

# ---------------- Gemini Query ----------------
@lru_cache(maxsize=128)
def query_gemini(prompt, max_tokens=200):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens}
    }
    try:
        time.sleep(1)  # avoid rate-limit
        resp = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=20)
        resp.raise_for_status()
        out = resp.json()
        return out["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 429:
            return "(Gemini error ❌: Too Many Requests, slow down!)"
        return f"(Gemini error ❌: {e})"
    except Exception as e:
        return f"(Gemini error ❌: {e})"

# ---------------- Search Helper ----------------
def search_alumni(query):
    if not query.strip():
        return df.sample(min(12, len(df)))
    tokens = [t.strip().lower() for t in re.split(r"[\s,;|/]+", query) if t.strip()]
    mask = pd.Series([False]*len(df))
    for t in tokens:
        mask |= df["Name"].str.lower().str.contains(re.escape(t), na=False)
        mask |= df["Domain"].str.lower().str.contains(re.escape(t), na=False)
        mask |= df["Skills"].str.lower().str.contains(re.escape(t), na=False)
        mask |= df["Current_Position"].str.lower().str.contains(re.escape(t), na=False)
    return df[mask].head(12)

# ---------------- Routes ----------------
@app.route("/")
def index():
    cards = df.sample(min(12, len(df))).to_dict(orient="records")
    return render_template("index.html", cards=cards)

@app.route("/search")
def api_search():
    q = request.args.get("q", "")
    results_df = search_alumni(q)
    items = []
    for _, r in results_df.iterrows():
        top_skill = (r["Skills"].split(",")[0].strip()) if r["Skills"] else ""
        items.append({
            "id": int(r["id"]),
            "name": r["Name"],
            "domain": r["Domain"],
            "domain_emoji": get_domain_emoji(r["Domain"]),
            "grad_year": int(r.get("Graduation_Year", 0)),
            "exp": int(r.get("Years_of_Experience", 0)),
            "company": r.get("Current_Position", ""),
            "ach_badges": achievement_badges(r.get("Achievements", "")),
            "top_skill": top_skill,
            "projects": r.get("Projects", "")[:140]
        })
    return jsonify({"count": len(items), "results": items})

@app.route("/profile/<int:pid>")
def profile_page(pid):
    row = df[df["id"] == pid]
    if row.empty:
        return "Profile not found", 404
    r = row.iloc[0].to_dict()
    prompt = f"Write a short engaging alumni bio for {r.get('Name')}.\nDomain: {r.get('Domain')}\nSkills: {r.get('Skills')}\nAchievements: {r.get('Achievements')}\nCurrent Position: {r.get('Current_Position')}"
    bio = query_gemini(prompt)
    return render_template("profile.html", alum=r, bio=bio)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"reply": "Say something 💬"})
    
    relevant_alumni = df[df.apply(lambda r: msg.lower() in r["Name"].lower() or
                                                msg.lower() in r["Domain"].lower(), axis=1)].head(5)
    
    prompt = "You are Lynq, a helpful alumni chatbot.\n"
    for _, r in relevant_alumni.iterrows():
        prompt += f"- {r['Name']} ({r['Domain']}, {r['Current_Position']}), Skills: {r['Skills']}\n"
    prompt += f"\nUser says: {msg}\nRespond helpfully."
    
    reply = query_gemini(prompt)
    return jsonify({"reply": reply})

@app.route("/download_csv")
def download_csv():
    return send_from_directory(".", CSV_PATH, as_attachment=True)

# Make helpers available in Jinja templates
app.jinja_env.globals.update(get_domain_emoji=get_domain_emoji, achievement_badges=achievement_badges)

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)