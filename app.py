import streamlit as st
import requests
from datetime import datetime
import statistics

# 🔑 Add your GitHub token here
TOKEN = ""

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 🔹 Fetch commits with pagination
def get_commits(repo):
    commits = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/commits?page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            return None, response.text

        data = response.json()
        if not data:
            break

        commits.extend(data)
        page += 1

    return commits, None


# 🔹 Evaluation Logic
def evaluate_repo(repo):
    commits, error = get_commits(repo)

    if error:
        return {"error": error}

    if not commits:
        return {"error": "No commits found"}

    dates = []
    meaningful_msgs = 0

    for c in commits:
        msg = c['commit']['message']
        date = c['commit']['committer']['date']

        dates.append(datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ"))

        if len(msg.split()) > 3 and msg.lower() not in ["update", "changes"]:
            meaningful_msgs += 1

    total_commits = len(commits)

    # 🔹 Frequency (5)
    if total_commits >= 20:
        freq = 5
    elif total_commits >= 10:
        freq = 3
    else:
        freq = 1

    # 🔹 Message Quality (4)
    ratio = meaningful_msgs / total_commits
    if ratio > 0.8:
        msg_score = 4
    elif ratio > 0.5:
        msg_score = 3
    else:
        msg_score = 1

    # 🔹 Regularity (3)
    if len(dates) > 1:
        gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        avg_gap = statistics.mean(gaps)

        if avg_gap <= 2:
            reg = 3
        elif avg_gap <= 5:
            reg = 2
        else:
            reg = 1
    else:
        reg = 0

    # 🔹 Progress (2)
    progress = 2 if total_commits > 10 else 1

    # 🔹 Hygiene (1)
    hygiene = 1

    total = freq + msg_score + reg + progress + hygiene

    return {
        "commits": total_commits,
        "frequency": freq,
        "message_quality": msg_score,
        "regularity": reg,
        "progress": progress,
        "hygiene": hygiene,
        "total": total
    }


# 🔹 UI
st.title("📊 GitHub Lab Evaluation Tool")

repo = st.text_input("Enter GitHub Repo (username/repo)")

if st.button("Evaluate"):
    if repo:
        result = evaluate_repo(repo)

        if "error" in result:
            st.error(result["error"])
        else:
            st.success(f"✅ Evaluation Complete for {repo}")

            st.write(f"**Total Commits:** {result['commits']}")
            st.write(f"**Frequency:** {result['frequency']} / 5")
            st.write(f"**Message Quality:** {result['message_quality']} / 4")
            st.write(f"**Regularity:** {result['regularity']} / 3")
            st.write(f"**Progress:** {result['progress']} / 2")
            st.write(f"**Hygiene:** {result['hygiene']} / 1")

            st.markdown("---")
            st.subheader(f"🎯 Final Marks: {result['total']} / 15")
    else:
        st.warning("Please enter a repo name")

if max(dates) - min(dates) < timedelta(days=2):
    total -= 2

def has_readme(repo):
    url = f"https://api.github.com/repos/{repo}/readme"
    res = requests.get(url, headers=HEADERS)
    return res.status_code == 200
