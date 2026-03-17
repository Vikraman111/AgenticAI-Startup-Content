# Agentic AI Content Pipeline 🚀

A semi-automated content curation and publishing system that crawls tech news, drafts LinkedIn posts using AI, and uses a Telegram bot for final human approval before publishing to Google Sheets.

---

## 🛠️ System Overview
1.  **Crawl**: Scans RSS feeds and Gmail (The Hustle) for the latest tech news.
2.  **Draft**: AI analyzes news and writes high-quality strategic business case studies.
3.  **Review**: The best posts are pushed to your **Telegram** with Approve/Skip buttons.
4.  **Publish**: Approved posts are automatically appended to a **Google Sheet**.

---

## 🚦 Order of Execution

### 1. The Daily Setup (Background Listeners)
Keep these running in separate terminal windows (or use a multiplexer like Screen/TMUX):

```bash
# Start the Telegram Brain (Handles your button clicks)
python telegram_approval/approval_bot.py

# Start the Sheet Factory (Uploads approved posts to Google Sheets)
python google_sheets_publisher/gspread_publisher.py
```

### 2. The Content Loop
Run these in order to generate and push new content:

| Step | Command | Description |
| :--- | :--- | :--- |
| **1** | `python run_monitoring.py` | Crawls RSS & Gmail for new articles. |
| **2** | `python run_writer.py` | AI drafts the actual LinkedIn posts. |
| **3** | `python telegram_approval/push_daily_review.py` | Pushes the #1 best post to your phone. |

---

## 🧰 Utility Tools

*   **`tools/reset_pipeline.py`**: The "Nuke" button. Purges everything (Local DB + Firebase) if you want a fresh start.
*   **`.env`**: Stores your private tokens (Telegram, Firebase, Google Sheets). **Never share this!**
*   **`data/agent_registry.db`**: Local SQLite database storing all article history.

---

## 🏗️ Folder Structure
- `monitoring/`: Crawlers for RSS and Email.
- `agents/`: AI logic for scoring and writing.
- `telegram_approval/`: Bot logic and push notifications.
- `google_sheets_publisher/`: Automation for gspread integration.
- `firebase_publishing/`: Cloud syncing logic.
