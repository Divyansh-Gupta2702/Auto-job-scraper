import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Multiple LinkedIn Job Search Feeds
SEARCH_URLS = {
    "DevOps Fresher India": "https://rss2json.com/api.json?rss_url=https://www.linkedin.com/jobs/devops-fresher-jobs/?currentJobId=4291641440&originalSubdomain=in",
    "Junior Cloud Engineer Remote":  "https://rss2json.com/api.json?rss_url=https://www.linkedin.com/jobs/devops-fresher-jobs/?currentJobId=4291641440&originalSubdomain=in",
    "Site Reliability Engineer Graduate":  "https://rss2json.com/api.json?rss_url=https://www.linkedin.com/jobs/devops-fresher-jobs/?currentJobId=4291641440&originalSubdomain=in",
    "AWS DevOps Associate": "https://rss2json.com/api.json?rss_url=https://www.linkedin.com/jobs/devops-fresher-jobs/?currentJobId=4291641440&originalSubdomain=in",
    "Kubernetes Engineer Fresher": "https://rss2json.com/api.json?rss_url=https://www.linkedin.com/jobs/devops-fresher-jobs/?currentJobId=4291641440&originalSubdomain=in",
}

def fetch_jobs():
    jobs = []
    for query, url in SEARCH_URLS.items():
        try:
            r = requests.get(url)
            data = r.json()
            for item in data.get("items", []):
                jobs.append({
                    "query": query,
                    "title": item["title"],
                    "link": item["link"]
                })
        except Exception as e:
            print(f"Error fetching {query}: {e}")
    return jobs

def send_email(jobs):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("EMAIL_RECEIVER")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Daily LinkedIn DevOps Job Listings"
    msg["From"] = sender
    msg["To"] = receiver

    if not jobs:
        body = "No new jobs found today."
    else:
        body = "<h3>Daily LinkedIn DevOps Job Listings</h3><ul>"
        for job in jobs:
            body += f"<li><b>{job['query']}</b>: <a href='{job['link']}'>{job['title']}</a></li>"
        body += "</ul>"

    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
