#!/usr/bin/env python3
import os
import sys
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta

try:
    import yaml
except Exception:
    print("Missing dependency: pyyaml. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

try:
    from duckduckgo_search import DDGS
except Exception:
    print("Missing dependency: duckduckgo-search. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

IST = timezone(timedelta(hours=5, minutes=30))

def load_queries(path="queries.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    queries = data.get("queries", [])
    max_per_query = int(data.get("max_per_query", 10))
    timelimit = data.get("timelimit", "d7")  # last 7 days by default
    region = data.get("region", "in-en")
    return queries, max_per_query, timelimit, region

def search_jobs(queries, max_per_query, timelimit, region):
    results = []
    with DDGS() as ddgs:
        for q in queries:
            # Use "news" and "text" search mix; prefer text with timelimit for freshness.
            try:
                for r in ddgs.text(q, max_results=max_per_query, region=region, safesearch="moderate", timelimit=timelimit):
                    # Normalize keys
                    results.append({
                        "query": q,
                        "title": r.get("title"),
                        "href": r.get("href"),
                        "body": r.get("body"),
                        "source": r.get("source"),
                    })
            except Exception as e:
                results.append({"query": q, "title": f"[ERROR searching: {q}]", "href": "", "body": str(e), "source": ""})
    # Deduplicate by href
    seen = set()
    deduped = []
    for r in results:
        href = r.get("href") or ""
        if href and href not in seen:
            seen.add(href)
            deduped.append(r)
    return deduped

def build_email_html(results):
    now_ist = datetime.now(IST).strftime("%Y-%m-%d %H:%M")
    header = f"<h2>Entry-level SWE roles — auto-search at {now_ist} IST</h2>"
    if not results:
        return header + "<p>No results found today based on the current queries.</p>"
    rows = []
    for r in results:
        title = (r.get("title") or "Untitled").strip()
        href = r.get("href") or "#"
        body = (r.get("body") or "").strip()
        source = (r.get("source") or "").strip()
        query = (r.get("query") or "").strip()
        snippet = body[:200] + ("..." if len(body) > 200 else "")
        rows.append(f"""
        <tr>
            <td style='padding:8px;border-bottom:1px solid #eee;'>{query}</td>
            <td style='padding:8px;border-bottom:1px solid #eee;'><a href="{href}">{title}</a><br><small>{snippet}</small></td>
            <td style='padding:8px;border-bottom:1px solid #eee;'>{source}</td>
        </tr>
        """)
    table = f"""
    <table style='border-collapse:collapse;width:100%;font-family:Segoe UI,Arial,sans-serif;font-size:14px;'>
        <thead>
            <tr style='text-align:left;background:#f7f7f7'>
                <th style='padding:8px;border-bottom:2px solid #ddd;'>Query</th>
                <th style='padding:8px;border-bottom:2px solid #ddd;'>Result</th>
                <th style='padding:8px;border-bottom:2px solid #ddd;'>Source</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """
    footer = "<p style='color:#666;font-size:12px'>Tip: Edit <code>queries.yaml</code> to refine sources/keywords.</p>"
    return header + table + footer

def send_email(html_body):
    recipient = os.environ.get("RECIPIENT_EMAIL")
    user = os.environ.get("GMAIL_USER")
    app_pw = os.environ.get("GMAIL_APP_PASSWORD")
    if not all([recipient, user, app_pw]):
        print("Missing env vars. Set RECIPIENT_EMAIL, GMAIL_USER, GMAIL_APP_PASSWORD.", file=sys.stderr)
        sys.exit(2)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Daily: Entry-level SWE roles (auto-search)"
    msg["From"] = user
    msg["To"] = recipient
    msg.attach(MIMEText("HTML email required. If you see this, enable HTML.", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, app_pw)
        server.send_message(msg)

def main():
    queries, max_per_query, timelimit, region = load_queries()
    results = search_jobs(queries, max_per_query, timelimit, region)
    html = build_email_html(results)
    send_email(html)
    print(f"Sent {len(results)} unique results.")

if __name__ == "__main__":
    main()
