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
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white" alt="Selenium" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/AsyncPRAW-FF4500?style=for-the-badge&logo=python&logoColor=white" alt="AsyncPRAW" />
  <img src="https://img.shields.io/badge/Asyncio-00599C?style=for-the-badge&logo=python&logoColor=white" alt="Asyncio" />
  <img src="https://img.shields.io/badge/ThreadPoolExecutor-FF7F50?style=for-the-badge&logo=python&logoColor=white" alt="ThreadPoolExecutor" />
</p>

---

## ⚙️ Installation
```bash
git clone https://github.com/YOUR_USERNAME/InternshipFinderBot.git
cd InternshipFinderBot
pip install -r requirements.txt
python internship_bot.py
