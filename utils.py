import os
import re
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from plyer import notification
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import config

def get_fast_headless_chrome():
    """Optimized headless Chrome driver"""
    print("[INFO] Starting headless Chrome...")
    chrome_options = Options()
    
    chrome_options.add_argument("--headless")  # stable headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    # Block images for faster loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(5)
    
    print("[SUCCESS] Chrome ready")
    return driver

def is_relevant(text):
    """
    Check if a string (title, label, or card text) matches relevant AI/ML keywords.
    - Substring match is used for both RELEVANT_KEYWORDS and SHORT_KEYWORDS.
    - Exclusion keywords are respected.
    """
    text_lower = text.lower()

    # Check exclusions first
    for exclusion in config.EXCLUSION_KEYWORDS:
        if exclusion.lower() in text_lower:
            return False

    # Check full keywords
    for keyword in config.RELEVANT_KEYWORDS:
        if keyword.lower() in text_lower:  # substring match
            return True

    # Check short keywords
    for keyword in config.SHORT_KEYWORDS:
        if keyword.lower() in text_lower:  # substring match
            return True

    return False


def generate_cover_message(company, role):
    """Generate a professional cover message for AI/ML internships"""
    return f"""Dear {company} HR Team,

I am a 3rd-year Computer Engineering student at FCRIT, Vashi, with a strong interest in Artificial Intelligence and Machine Learning. I have experience in AI/ML projects and practical applications, and I am eager to contribute to {company} as a {role} intern. I am confident that my skills and enthusiasm will allow me to make a meaningful impact on your team.

Looking forward to the opportunity to discuss how I can contribute.

Best regards,
Siddhen P"""

def load_existing_data():
    """Load existing internships CSV or create a new DataFrame if file not found"""
    if os.path.exists(config.CSV_FILE):
        return pd.read_csv(config.CSV_FILE)
    return pd.DataFrame(columns=['Company','Role','Platform','PostingDate','Deadline','Link','Status','ScamStatus','CoverMessage'])

def save_data(df):
    """Save the DataFrame to CSV"""
    df.to_csv(config.CSV_FILE, index=False)

def send_email_alert(sender, pwd, recipient, subject, body):
    """Send an email notification for a new internship"""
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, pwd)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"[✖] Email failed: {e}")

def send_desktop_alert(title, message):
    """Send a desktop notification"""
    try:
        notification.notify(title=title, message=message, timeout=10)
    except:
        pass
