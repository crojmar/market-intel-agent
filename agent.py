import os
import requests
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Config from GitHub Secrets
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

CITIES = [
    "Carrollton, GA", "Fayetteville, GA", "Griffin, GA",
    "Fort Walton Beach, FL", "Savannah, GA", "Valdosta, GA"
]

KEYWORDS = [
    "job creation", "new facility", "business opening",
    "company expansion", "layoffs", "plant closing",
    "distribution center", "manufacturing plant", "headquarters"
]

def search_news(city):
    query = f"{city} " + " OR ".join(KEYWORDS)
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Error searching {city}: {response.status_code}")
        return []

def build_email_body(results):
    email_body = "<h2>📊 Daily Market Intelligence Report</h2>"
    email_body += f"<p>{datetime.datetime.now().strftime('%B %d, %Y')}</p><ul>"
    for item in results:
        email_body += f"<li><strong>{item['city']}</strong>: {item['summary']}<br><a href='{item['link']}'>{item['link']}</a></li>"
    email_body += "</ul>"
    return email_body

def send_email(subject, html_body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

def main():
    all_results = []
    for city in CITIES:
        print(f"Searching news for {city}...")
        articles = search_news(city)
        for article in articles[:2]:
            snippet = article.get("snippet", "")
            link = article.get("link", "")
            if not snippet or not link:
                continue
            all_results.append({
                "city": city,
                "summary": snippet,
                "link": link
            })

    if all_results:
        email_body = build_email_body(all_results)
        send_email("📊 Daily Market Growth Report", email_body)
        print("Report sent successfully.")
    else:
        print("No relevant news found today.")

if __name__ == "__main__":
    main()
