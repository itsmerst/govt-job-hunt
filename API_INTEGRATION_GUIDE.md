# 🌐 API Integration & Auto-Update Guide

Complete guide to set up automatic job updates using APIs and external data sources.

---

## 📡 Overview

The advanced version supports:
- ✅ Real-time API fetching
- ✅ Automatic job expiration (removes past deadlines)
- ✅ Specific dates (not "usually July")
- ✅ Days remaining calculator
- ✅ Urgency indicators (Apply NOW / Apply Soon)

---

## 🔧 Current Status

### **Available APIs**

| Source | Type | Status |
|--------|------|--------|
| SSC (ssc.nic.in) | Government | No public API |
| UPSC (upsc.gov.in) | Government | No public API |
| IBPS (ibps.in) | Banking | No public API |
| Railways (rrbapply.gov.in) | Government | No public API |
| GATE (gate.iitkgp.ac.in) | Education | Limited API |
| Sarkari Result | Aggregator | Unofficial |

### **Challenge**
Most Indian government portals don't provide public REST APIs. They use:
- Web portals (manual updates needed)
- Email notifications (manual tracking)
- Mobile apps (official notifications)

---

## 📱 Recommended Solutions

### **Option 1: Web Scraping (Advanced)**

Use Beautiful Soup to scrape government websites:

```python
import requests
from bs4 import BeautifulSoup

def scrape_ssc_notifications():
    url = "https://ssc.nic.in/notifications"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract job notifications
    jobs = []
    for item in soup.find_all('div', class_='notification'):
        job = {
            'name': item.find('h3').text,
            'deadline': item.find('span', class_='deadline').text,
            'link': item.find('a')['href']
        }
        jobs.append(job)
    
    return jobs
```

**Pros:** Real-time data
**Cons:** Brittle (breaks if website changes), Slow, Resource intensive

---

### **Option 2: RSS Feeds (Easy)**

Many government sites have RSS feeds:

```python
import feedparser

def fetch_rss_jobs():
    feeds = [
        "https://ssc.nic.in/rss",
        "https://upsc.gov.in/rss",
    ]
    
    for feed_url in feeds:
        d = feedparser.parse(feed_url)
        for entry in d.entries:
            print(entry.title)
            print(entry.published)
```

**Pros:** Easy, Official source
**Cons:** Not all sites provide RSS

---

### **Option 3: Webhook Integration (Best)**

Set up webhooks to receive notifications:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/job-update', methods=['POST'])
def receive_job_update():
    data = request.json
    
    # Add new job to database
    new_job = {
        "id": max([j['id'] for j in jobs]) + 1,
        "name": data['name'],
        "organization": data['organization'],
        "application_deadline": data['deadline'],
        "notification_link": data['link'],
        # ... other fields
    }
    
    jobs.append(new_job)
    save_jobs_to_database(jobs)
    
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(port=5000)
```

**Pros:** Real-time, Automatic
**Cons:** Requires server, Webhook configuration

---

### **Option 4: Google Forms → Apps Script (Easiest)**

Create a Google Form for community updates:

```javascript
// Apps Script code
function onFormSubmit(e) {
  const response = e.response;
  const itemResponses = response.getItemResponses();
  
  const job = {
    name: itemResponses[0].getResponse(),
    organization: itemResponses[1].getResponse(),
    deadline: itemResponses[2].getResponse(),
    link: itemResponses[3].getResponse()
  };
  
  // Save to Google Sheet
  const sheet = SpreadsheetApp.getActiveSheet();
  sheet.appendRow([
    job.name,
    job.organization,
    job.deadline,
    job.link,
    new Date()
  ]);
}
```

**Pros:** Easiest, Community-driven
**Cons:** Manual submissions, Verification needed

---

### **Option 5: Scheduled Scraping (Recommended)**

Automatic daily scraping with error handling:

```python
import schedule
import time
from datetime import datetime

def job_scraper():
    """Scrape jobs daily at 9 AM"""
    try:
        print(f"[{datetime.now()}] Scraping government job sites...")
        
        # Scrape multiple sources
        ssc_jobs = scrape_ssc()
        upsc_jobs = scrape_upsc()
        bank_jobs = scrape_ibps()
        
        # Merge and update database
        all_jobs = ssc_jobs + upsc_jobs + bank_jobs
        
        # Remove duplicates
        unique_jobs = list({j['notification_link']: j for j in all_jobs}.values())
        
        # Update database
        save_jobs(unique_jobs)
        print(f"✓ Updated {len(unique_jobs)} jobs")
        
    except Exception as e:
        print(f"✗ Scraping error: {e}")

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(job_scraper)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

**Pros:** Automatic, Reliable
**Cons:** Website maintenance may break scraper

---

## 🔄 Auto-Update Implementation

### **Step 1: Install Required Libraries**

```bash
pip install requests beautifulsoup4 feedparser schedule
```

### **Step 2: Create update_jobs.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatic Job Updater - Scheduled job scraping and database updates
"""

import json
import schedule
import time
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

class AutoJobUpdater:
    def __init__(self, database_file='jobs_database.json'):
        self.database_file = Path(database_file)
        self.jobs = self.load_jobs()
    
    def load_jobs(self):
        if self.database_file.exists():
            with open(self.database_file, 'r', encoding='utf-8') as f:
                return json.load(f).get('jobs', [])
        return []
    
    def save_jobs(self):
        data = {
            'last_updated': datetime.now().isoformat(),
            'jobs': self.jobs
        }
        with open(self.database_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def scrape_ssc_jobs(self):
        """Scrape SSC notifications"""
        try:
            print("📍 Scraping SSC notifications...")
            url = "https://ssc.nic.in/notifications"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse and extract jobs
                print("✓ SSC notifications fetched")
                return []
            else:
                print(f"✗ SSC returned {response.status_code}")
                return []
        except Exception as e:
            print(f"✗ SSC error: {e}")
            return []
    
    def remove_expired_jobs(self):
        """Remove jobs with passed deadlines"""
        before = len(self.jobs)
        
        self.jobs = [j for j in self.jobs if 
                    not self.is_expired(j.get('application_deadline'))]
        
        removed = before - len(self.jobs)
        if removed > 0:
            print(f"🗑️  Removed {removed} expired jobs")
    
    def is_expired(self, deadline_str):
        """Check if deadline has passed"""
        if not deadline_str:
            return False
        
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            return deadline < datetime.now()
        except:
            return False
    
    def update(self):
        """Run full update"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting job update...")
        
        # Remove expired jobs
        self.remove_expired_jobs()
        
        # Scrape new jobs
        new_jobs = []
        new_jobs.extend(self.scrape_ssc_jobs())
        # Add more scrapers here
        
        # Merge with existing
        if new_jobs:
            self.jobs.extend(new_jobs)
            self.jobs = self.deduplicate_jobs()
        
        # Save to database
        self.save_jobs()
        print(f"✓ Update complete. Total jobs: {len(self.jobs)}\n")
    
    def deduplicate_jobs(self):
        """Remove duplicate jobs"""
        seen = {}
        unique = []
        
        for job in self.jobs:
            link = job.get('notification_link', '')
            if link not in seen:
                seen[link] = True
                unique.append(job)
        
        return unique

def main():
    updater = AutoJobUpdater()
    
    # Schedule updates
    schedule.every().day.at("09:00").do(updater.update)  # 9 AM daily
    schedule.every().day.at("14:00").do(updater.update)  # 2 PM daily
    schedule.every().day.at("18:00").do(updater.update)  # 6 PM daily
    
    print("✓ Job updater scheduled (9 AM, 2 PM, 6 PM daily)")
    print("  Press Ctrl+C to stop\n")
    
    # Initial update
    updater.update()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
```

### **Step 3: Run Auto-Updater**

```bash
python update_jobs.py
```

---

## 📊 Database Format for API Data

### **When adding jobs via API:**

```json
{
  "id": 11,
  "name": "Job Name",
  "organization": "Organization",
  "requires_gate": false,
  "notification_date": "2026-07-19",
  "application_deadline": "2026-09-17",
  "exam_date": "2026-10-15",
  "source": "api_ssc",
  "source_url": "https://...",
  "verified": true,
  "eligibility": {...},
  "salary": "...",
  "steps": [...],
  "documents": [...]
}
```

---

## 🔐 API Keys & Authentication

For services that require authentication:

```python
# Create .env file
SSC_API_KEY=your_key_here
UPSC_API_KEY=your_key_here

# Load in Python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SSC_API_KEY')
```

---

## 📈 Monitoring & Logging

### **Add logging to track updates:**

```python
import logging

logging.basicConfig(
    filename='job_updates.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def update_with_logging():
    logger.info("Starting job update")
    try:
        # Update logic
        logger.info(f"Updated {count} jobs")
    except Exception as e:
        logger.error(f"Update failed: {e}")
```

---

## 🚀 Cloud Deployment

### **Option 1: GitHub Actions (Free)**

Create `.github/workflows/update-jobs.yml`:

```yaml
name: Update Government Jobs

on:
  schedule:
    - cron: '0 9,14,18 * * *'  # 9 AM, 2 PM, 6 PM daily

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python job_finder_advanced.py
      - run: git add jobs_database.json
      - run: git commit -m "Auto-update jobs $(date)" || true
      - run: git push
```

### **Option 2: AWS Lambda (Pay-per-use)**

```python
import json
from job_finder_advanced import AdvancedJobsFinder

def lambda_handler(event, context):
    finder = AdvancedJobsFinder()
    finder.fetch_from_api()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Jobs updated successfully')
    }
```

### **Option 3: Google Cloud Scheduler**

```bash
gcloud scheduler jobs create app-engine job-updater \
  --schedule="0 9 * * *" \
  --http-method=POST \
  --uri="https://your-app.appspot.com/update-jobs"
```

---

## ⚙️ Configuration

### **Update Frequency**

```python
# Fast updates (every 6 hours)
schedule.every(6).hours.do(update)

# Moderate (3 times daily)
schedule.every().day.at("09:00").do(update)
schedule.every().day.at("14:00").do(update)
schedule.every().day.at("18:00").do(update)

# Slow (once daily)
schedule.every().day.at("09:00").do(update)
```

### **API Timeout**

```python
response = requests.get(url, timeout=10)  # 10 seconds
```

### **Error Handling**

```python
try:
    update_jobs()
except requests.Timeout:
    logger.error("Request timed out")
except requests.ConnectionError:
    logger.error("Connection failed")
except Exception as e:
    logger.error(f"Update failed: {e}")
```

---

## 📱 Manual Updates via Google Sheet

### **Simple Community-Driven Approach**

1. Create Google Sheet with columns:
   - Job Name
   - Organization
   - Deadline
   - Official Link
   - Salary

2. Share link with community
3. Use Google Apps Script to sync:

```javascript
function syncJobsFromSheet() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  const jobs = data.slice(1).map(row => ({
    name: row[0],
    organization: row[1],
    deadline: row[2],
    link: row[3],
    salary: row[4]
  }));
  
  // Upload to database
  uploadToDatabase(jobs);
}
```

---

## 🔍 Verification & Quality

### **Always Verify:**
- ✓ Deadline dates are correct
- ✓ Links are still active
- ✓ No duplicate entries
- ✓ All required fields populated
- ✓ Organization name matches

### **Validation Script**

```python
def validate_job(job):
    required_fields = ['name', 'organization', 'notification_link', 
                      'application_deadline', 'salary', 'eligibility']
    
    for field in required_fields:
        if not job.get(field):
            return False, f"Missing: {field}"
    
    if not job.get('application_deadline').match(r'\d{4}-\d{2}-\d{2}'):
        return False, "Invalid date format"
    
    return True, "Valid"
```

---

## 📞 Troubleshooting API Issues

| Problem | Solution |
|---------|----------|
| No API available | Use web scraping or manual updates |
| Slow responses | Increase timeout, use caching |
| Website changes | Update CSS selectors in scraper |
| Rate limiting | Add delays between requests |
| SSL errors | Use `verify=False` (with caution) |

---

## 🎯 Next Steps

1. **Start with manual database updates** (edit JSON)
2. **Graduate to scheduled scraping** (if needed)
3. **Deploy to cloud** (for 24/7 updates)
4. **Community contributions** (Google Forms)

---

**Remember:** Most reliable approach is **community-driven updates** where users contribute new jobs they find!

---
