import os
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
LOCATION = os.getenv("LOCATION", "Mumbai")
CSV_FILE = "internships.csv"
POLL_INTERVAL = 1800  # 30 minutes

ENABLE_LINKEDIN = False
ENABLE_UNSTOP = True
ENABLE_INTERNSHALA = True


# ✅ Relevant AI/ML-related keywords
RELEVANT_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning", "nlp",
    "natural language processing", "computer vision", "data science",
    "data analyst", "data analytics", "data engineer", "data engineering",
    "big data", "tensorflow", "pytorch", "neural network", "llm"
]

# ✅ Short/abbreviated forms of relevant terms
SHORT_KEYWORDS = ["ai", "ml", "cv", "nlp", "dl"]

# 🚫 Exclusion keywords to filter out irrelevant internships
EXCLUSION_KEYWORDS = [
    "full-stack", "fullstack", "frontend", "front-end", "backend", "back-end",
    "web developer", "ui/ux", "graphic", "marketing", "digital marketing",
    "finance", "financial analyst", "social media", "sales", "hr", "management",
    "business development", "content writer", "copywriter", "ambassador"
]
