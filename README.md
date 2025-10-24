# Internship Finder Bot 🤖💼
Real-time internship monitoring bot that helps students and job seekers find **legitimate opportunities** quickly and safely.

---

## 🌟 Why I Made This
I created this bot to solve a **personal problem**: I used to manually search for internships on LinkedIn, Unstop, and Internshala.  

- Each search took **~20 minutes**, and verifying legitimacy added another **~15 minutes**.
- I encountered **many scams**, where companies asked for money for internships—something that shouldn’t happen.
- I wanted a solution that **automates the search**, **verifies scams**, and **notifies me in real-time**.

This project combines **automation, async programming, and scam detection** to save time and prevent falling for fraudulent postings.

---

## 🚀 Overview
This bot:

- Scrapes multiple internship platforms (Unstop, Internshala, LinkedIn) for relevant postings.
- Filters postings based on chosen domains (AI/ML, Web Development, Data Science).
- Generates **personalized cover messages** for each opportunity.
- Checks Reddit for **scam/fraud reports** about each company.
- Sends **desktop notifications** for new, verified internships.
- Stores all internship data in a CSV to avoid duplicates.

---

## ⚡ Current Functionality

### Scrapers Implemented
- **Unstop:** Scrapes internships using domain-specific search terms.
- **Internshala:** Scrapes internships using Selenium to bypass DDoS protection.
- **LinkedIn:** Can be enabled for future support.

### Filtering & Relevance
- Uses **keyword matching** to find relevant internships.
- Excludes unrelated roles using configurable keywords.

### Reddit Scam Detection
- Asynchronously checks popular subreddits: `r/Scams`, `r/IndiaCareers`, `r/Jobs`.
- Flags posts/comments with keywords like **“scam”, “fraud”, “fake”, “avoid”**.
- Marks suspicious companies with **⚠️ Scam Suspected**.

### Cover Messages
- Automatically generates **ready-to-send cover messages**.

### Data Management
- Stores all internships in a **CSV file** (`internships.csv`).
- Tracks already collected postings to **avoid duplicates**.

### Notifications
- Sends **desktop notifications** for new internships.

### Async & Multi-threading Workflow
- Uses **asyncio** for Reddit checks.
- Uses **ThreadPoolExecutor** for parallel scraping of multiple platforms.

---

## 🛠️ Tech Stack
<p align="left">
  <a href="https://www.python.org/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python" width="40" height="40"/></a>
  <a href="https://www.selenium.dev/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/selenium/selenium-original.svg" alt="Selenium" width="40" height="40"/></a>
  <a href="https://pandas.pydata.org/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pandas/pandas-original.svg" alt="Pandas" width="40" height="40"/></a>
  <a href="https://asyncpraw.readthedocs.io/en/latest/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="AsyncPRAW" width="40" height="40"/></a>
  <a href="https://docs.python.org/3/library/asyncio.html" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Asyncio" width="40" height="40"/></a>
  <a href="https://docs.python.org/3/library/concurrent.futures.html" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="ThreadPoolExecutor" width="40" height="40"/></a>
  <a href="https://pypi.org/project/plyer/" target="_blank"><img src="https://img.icons8.com/ios/50/000000/notification.png" alt="Desktop Notifications" width="40" height="40"/></a>
</p>

---

## ⚙️ Installation
```bash
git clone https://github.com/YOUR_USERNAME/InternshipFinderBot.git
cd InternshipFinderBot
pip install -r requirements.txt
python internship_bot.py
