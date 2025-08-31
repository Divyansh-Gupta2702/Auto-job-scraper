# Job Search Automation (Daily @ 12:00 IST)

This kit searches the web for **entry-level Software Engineer** roles on popular startup ATS boards and **emails you the results** every day at **12:00 PM IST**.

## What it does
- Uses DuckDuckGo to query sites like Lever, Greenhouse, Ashby, Wellfound, and Workable.
- De-duplicates links and sends a clean HTML email.
- Easy to customize via `queries.yaml` (add/remove keywords and sites).

---

## Quick Start (local Windows, via Task Scheduler)

1. **Install Python 3.10+** and ensure `python` is in PATH.
2. Open **PowerShell** in this folder and run:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Set **environment variables** (replace with your values):
   ```powershell
   setx RECIPIENT_EMAIL "you@example.com"
   setx GMAIL_USER "yourgmail@gmail.com"
   setx GMAIL_APP_PASSWORD "your_app_password"
   ```
   > For Gmail, create an **App Password** (Google Account → Security → App passwords).

4. **Test run**:
   ```powershell
   .\.venv\Scripts\python.exe .\job_search.py
   ```
   You should receive a test email.

5. **Schedule daily at 12:00 PM IST** using Windows Task Scheduler:
   - Open *Task Scheduler* → *Create Task...*
   - **General**: Name `Job Search Email (12:00 IST)`
   - **Triggers**: *New...* → Daily → Start `12:00:00` → Enabled
   - **Actions**: *New...* → Program/script:
     ```
     C:\full\path\to\.venv\Scripts\python.exe
     ```
     **Add arguments**:
     ```
     C:\full\path\to\job_search.py
     ```
     **Start in**: the folder containing these files.
   - **Conditions**: Uncheck "Start the task only if the computer is on AC power" (optional).
   - **OK** to save.

> Tip: If environment variables set with `setx` don't appear, log out/in or set them in the task **Action → Start in** using a wrapper `.cmd` file that `set` variables then runs Python.

---

## Option B: GitHub Actions (runs in the cloud)

1. Push these files to a new GitHub repo.
2. In **Repository → Settings → Secrets and variables → Actions → New repository secret**, add:
   - `RECIPIENT_EMAIL`
   - `GMAIL_USER`
   - `GMAIL_APP_PASSWORD`
3. The provided workflow is already set to run daily at **06:30 UTC** (== **12:00 IST**). You can also trigger manually via *Actions → Run workflow*.

---

## Customize your search

Edit `queries.yaml`:
- Add/remove lines under `queries:`
- Common patterns:
  - `"entry level" "software engineer" site:lever.co`
  - `"new grad" "software engineer" site:greenhouse.io`
  - `"junior" "software engineer" site:ashbyhq.com`

You can also narrow by location keywords (e.g., `"Bengaluru"` or `"Remote"`).

---

## Notes & Tips
- DuckDuckGo results vary by day; consider expanding keywords for broader coverage.
- For richer control, swap DuckDuckGo with a commercial search API (e.g., SerpAPI, Google CSE) — the code is structured to modify easily.
- Email uses Gmail SMTP. If you prefer, switch to **SendGrid** (free tier) by replacing the `send_email` function.

---

## Troubleshooting
- **No email arrives**: Check spam, verify env vars, and try a manual run.
- **Gmail blocks sign-in**: Use an **App Password** (required for 2FA accounts).
- **Task runs but fails**: Inspect Task Scheduler *History* and run the script manually in the same environment to see errors.

Happy hunting!
