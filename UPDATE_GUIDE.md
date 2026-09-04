# 📝 Jobs Database Update Guide

Complete step-by-step guide to add, edit, and update government jobs in the database.

---

## 🎯 Quick Links

1. [Adding a New Job](#adding-a-new-job)
2. [Editing Existing Job](#editing-existing-job)
3. [Database Structure](#database-structure)
4. [Common Updates](#common-updates)
5. [JSON Format Tips](#json-format-tips)
6. [Backup & Recovery](#backup--recovery)

---

## ➕ Adding a New Job

### **Step 1: Open the Database**

1. Navigate to your project folder: `Government_Jobs/`
2. Right-click on `jobs_database.json`
3. Select "Open with" → Choose a text editor:
   - **Windows:** Notepad, VS Code, Notepad++
   - **Mac:** TextEdit, VS Code, Sublime Text
   - **Linux:** gedit, nano, VS Code

⚠️ **DO NOT USE:** MS Word, Google Docs (they corrupt JSON format)

### **Step 2: Understand the Structure**

```json
{
  "last_updated": "2026-07-19",
  "jobs": [
    {
      "id": 1,
      "name": "Job Name",
      "organization": "Organization",
      ...
    },
    {
      "id": 2,
      "name": "Another Job",
      ...
    }
  ]
}
```

### **Step 3: Locate the End of Jobs Array**

Find the last job entry (usually job with highest ID):

```json
    {
      "id": 10,
      "name": "Patent Office - Examiner Recruitment",
      ...
      "deadline_info": "30 days from notification"
    }
  ]
}
```

### **Step 4: Add New Job Before Closing Bracket**

Place your cursor after the last `}` of the last job:

```json
    {
      "id": 10,
      "name": "Patent Office - Examiner Recruitment",
      ...
      "deadline_info": "30 days from notification"
    },
    {
      "id": 11,
      "name": "YOUR NEW JOB",
      ...
    }
  ]
}
```

### **Step 5: Use This Template**

Copy and paste this complete template for a new job:

```json
{
  "id": 11,
  "name": "Job Full Name",
  "organization": "Organization Name",
  "requires_gate": false,
  "positions": [
    "Position 1",
    "Position 2",
    "Position 3"
  ],
  "eligibility": {
    "qualification": "Bachelor's Degree/Engineering",
    "class_requirement": "First class with distinction preferred",
    "age": "18-30 years",
    "nationality": "Indian citizen"
  },
  "salary": "₹XXXXX-XXXXXX per month + benefits",
  "posts": "List of available positions",
  "application_fee": "₹XXX",
  "notification_link": "https://official-website.com",
  "steps": [
    "Step 1: Description",
    "Step 2: Description",
    "Step 3: Description",
    "Step 4: Description",
    "Step 5: Description"
  ],
  "documents": [
    "Document 1",
    "Document 2",
    "Document 3",
    "Document 4",
    "Document 5"
  ],
  "exam_pattern": "Description of exam pattern and marks",
  "notification_date": "Usually Month-Month",
  "deadline_info": "XX days from notification date"
}
```

### **Step 6: Fill in Your Information**

Replace placeholders with actual job details:

- **id**: Next number (if last was 10, use 11)
- **name**: Full name of the exam/job
- **organization**: Government body conducting it
- **requires_gate**: `true` if GATE score needed, `false` otherwise
- **positions**: Array of available positions
- **salary**: Monthly salary range
- **application_fee**: Cost to apply
- **notification_link**: Official website URL
- **steps**: 15-25 detailed application steps (numbered automatically in HTML)
- **documents**: Required documents checklist
- **exam_pattern**: How the exam is structured
- **notification_date**: When is it usually announced?
- **deadline_info**: How many days to apply?

### **Step 7: Validate JSON Format**

Before saving, check syntax:

1. **Online Validator:**
   - Go to https://jsonlint.com/
   - Paste your entire file
   - Click "Validate JSON"
   - Should see ✓ Valid JSON

2. **Common Errors:**
   ```
   ✗ Missing comma after }
   ✗ Missing quotes around strings
   ✗ Unmatched brackets or braces
   ✗ Single quotes instead of double quotes
   ```

### **Step 8: Save File**

1. After validation passes, save the file
2. File format must remain: `jobs_database.json`
3. Do NOT change filename
4. Encoding: UTF-8

### **Step 9: Regenerate Dashboard**

```bash
python job_finder_v2.py
```

Output should show:
```
Total jobs in database: 11
Jobs without GATE requirement: 10
Jobs with GATE requirement: 1
✓ Dashboard created successfully!
```

Your new job is now in the dashboard! ✓

---

## ✏️ Editing Existing Job

### **Scenario 1: Update Salary**

Find the job and update salary field:

```json
// Before:
"salary": "₹5,200-20,200 per month + benefits",

// After:
"salary": "₹5,500-21,000 per month + benefits",
```

### **Scenario 2: Change Age Limit**

```json
// Before:
"age": "18-32 years",

// After:
"age": "18-35 years",
```

### **Scenario 3: Add New Application Step**

In the steps array, add new step:

```json
"steps": [
  "Step 1: Visit website",
  "Step 2: Register account",
  "Step 3: Fill form",
  "Step 4: Upload documents",
  "Step 5: Pay fee",
  "Step 6: NEW STEP: Download admit card one week before",
  "Step 7: Appear for exam"
]
```

### **Scenario 4: Update Notification Date**

```json
// Before:
"notification_date": "Usually July-August",

// After:
"notification_date": "Usually July-September",
```

### **Scenario 5: Change Requirement (Mark as GATE Required)**

```json
// Before:
"requires_gate": false,

// After:
"requires_gate": true,
```

### **After Any Edit:**

1. Validate JSON using jsonlint.com
2. Save the file
3. Run: `python job_finder_v2.py`
4. Dashboard automatically updates

---

## 🏗️ Database Structure Details

### **Top Level**
```json
{
  "last_updated": "YYYY-MM-DD",
  "jobs": [ ... ]
}
```

### **Each Job Object**

| Field | Type | Example | Required |
|-------|------|---------|----------|
| id | Number | 1, 2, 3 | ✓ Yes |
| name | String | "SSC CGL" | ✓ Yes |
| organization | String | "SSC" | ✓ Yes |
| requires_gate | Boolean | true/false | ✓ Yes |
| positions | Array | ["Post 1", "Post 2"] | ✓ Yes |
| eligibility | Object | {qualification, age, ...} | ✓ Yes |
| salary | String | "₹5,200-20,200" | ✓ Yes |
| posts | String | "Assistant, Clerk" | ✓ Yes |
| application_fee | String | "₹100" | ✓ Yes |
| notification_link | String | "https://..." | ✓ Yes |
| steps | Array | ["Step 1", "Step 2"] | ✓ Yes |
| documents | Array | ["Doc 1", "Doc 2"] | ✓ Yes |
| exam_pattern | String | "Tier-I, Tier-II..." | ✓ Yes |
| notification_date | String | "Usually July" | ✓ Yes |
| deadline_info | String | "30 days" | ✓ Yes |

### **Eligibility Object**
```json
{
  "qualification": "Bachelor's Degree",
  "class_requirement": "Any class",
  "age": "18-32 years",
  "nationality": "Indian citizen"
}
```

---

## 📋 Common Updates

### **Update 1: Add New Bank Recruitment**

```json
{
  "id": 12,
  "name": "ICICI Bank Probationary Officer",
  "organization": "ICICI Bank",
  "requires_gate": false,
  "positions": ["Probationary Officer", "Junior Manager"],
  "eligibility": {
    "qualification": "Bachelor's Degree",
    "class_requirement": "First class preferred",
    "age": "21-28 years",
    "nationality": "Indian citizen"
  },
  "salary": "₹25,000-50,000 per month",
  "posts": "Probationary Officer, Junior Manager",
  "application_fee": "₹900",
  "notification_link": "https://icicibank.com/careers",
  "steps": [
    "Visit ICICI Bank careers page",
    "Look for PO recruitment notification",
    "Register with email ID",
    "Fill online application",
    "Upload degree certificate",
    "Upload mark sheets",
    "Upload photo and signature",
    "Pay application fee",
    "Get reference number",
    "Appear for online exam",
    "Clear mains if shortlisted",
    "Attend group discussion",
    "Participate in personal interview"
  ],
  "documents": [
    "Bachelor's degree certificate",
    "All year mark sheets",
    "Birth certificate",
    "Passport/Aadhar",
    "Character certificate",
    "Colored passport photo",
    "Signature sample"
  ],
  "exam_pattern": "Online Prelim (100 marks) + Online Mains (200 marks) + Interview (50 marks)",
  "notification_date": "Usually April-May",
  "deadline_info": "30 days from notification"
}
```

### **Update 2: Add State-Level Exam**

```json
{
  "id": 13,
  "name": "Maharashtra PSC Recruitment",
  "organization": "Maharashtra Public Service Commission",
  "requires_gate": false,
  "positions": ["PSI", "ASI", "Various Posts"],
  "eligibility": {
    "qualification": "Bachelor's Degree",
    "class_requirement": "Any class",
    "age": "18-38 years",
    "nationality": "Indian citizen / MH Domicile"
  },
  "salary": "₹9,300-34,800 per month",
  "posts": "Police Sub-Inspector, Assistant Sub-Inspector",
  "application_fee": "₹524",
  "notification_link": "https://mahapsc.mahaonline.gov.in",
  "steps": [
    "Visit MPSC official website",
    "Check recruitment notifications",
    "Register/Login to application",
    "Fill application form",
    "Enter personal details",
    "Select post preference",
    "Upload required documents",
    "Upload color photo",
    "Upload signature",
    "Upload scanned admit cards",
    "Pay application fee online",
    "Get acknowledgement",
    "Prepare for written exam",
    "Appear for PSI exam",
    "Clear prelims for mains",
    "Attend interview"
  ],
  "documents": [
    "Bachelor's degree certificate",
    "10th and 12th certificates",
    "Birth certificate",
    "Domicile certificate",
    "Caste certificate if applicable",
    "Character certificate",
    "Passport/Aadhar/PAN",
    "Medical fitness certificate"
  ],
  "exam_pattern": "Prelims (150 marks) + Mains (400 marks) + Interview (100 marks)",
  "notification_date": "Usually August-September",
  "deadline_info": "30-45 days from notification"
}
```

### **Update 3: Modify Existing Salary**

Find job and update:
```json
// Before
"salary": "₹5,200-20,200 per month + benefits",

// After (if there's a pay hike)
"salary": "₹5,500-21,500 per month + benefits",
```

---

## 💡 JSON Format Tips

### **Correct Format**
```json
{
  "name": "SSC CGL",
  "salary": "₹5,200-20,200",
  "age": 32,
  "active": true,
  "documents": ["Doc1", "Doc2"],
  "eligibility": {
    "qualification": "Bachelor's"
  }
}
```

### **Common Mistakes to Avoid**

❌ **Wrong - Single quotes:**
```json
{
  'name': 'SSC CGL'
}
```

✓ **Correct - Double quotes:**
```json
{
  "name": "SSC CGL"
}
```

---

❌ **Wrong - Missing comma:**
```json
{
  "name": "SSC CGL"
  "salary": "₹5,200"
}
```

✓ **Correct - Comma between fields:**
```json
{
  "name": "SSC CGL",
  "salary": "₹5,200"
}
```

---

❌ **Wrong - Trailing comma:**
```json
{
  "documents": ["Doc1", "Doc2",]
}
```

✓ **Correct - No trailing comma:**
```json
{
  "documents": ["Doc1", "Doc2"]
}
```

---

❌ **Wrong - Unescaped quotes:**
```json
{
  "name": "SSC "CGL" Exam"
}
```

✓ **Correct - Escaped quotes:**
```json
{
  "name": "SSC \"CGL\" Exam"
}
```

---

## 💾 Backup & Recovery

### **Create Backup**

Before making major updates:

1. Copy `jobs_database.json`
2. Rename to `jobs_database_backup_2026-07-19.json`
3. Keep in same folder
4. Never edit backup (for recovery only)

### **Backup Strategy**

```
Government_Jobs/
├── jobs_database.json                    (Current)
├── jobs_database_backup_2026-07-19.json  (Daily backup)
├── jobs_database_backup_2026-07-18.json  (Previous)
└── jobs_database_backup_2026-07-17.json  (Older)
```

### **Recovery Process**

If you corrupt the database:

1. Delete corrupted `jobs_database.json`
2. Copy `jobs_database_backup_YYYY-MM-DD.json`
3. Rename it to `jobs_database.json`
4. Regenerate dashboard: `python job_finder_v2.py`

### **Update Tracking**

Keep notes of updates:

```
2026-07-19: Added ICICI Bank PO (ID 12)
2026-07-18: Updated SSC CGL salary
2026-07-17: Added Maharashtra PSC (ID 13)
```

---

## ✅ Validation Checklist

Before saving changes:

- [ ] All jobs have unique ID numbers
- [ ] All required fields are filled
- [ ] JSON format is valid (use jsonlint.com)
- [ ] No typos in organization names
- [ ] URLs start with `https://`
- [ ] Salary format includes currency (₹)
- [ ] Steps and documents are detailed enough (15+ items)
- [ ] Special characters are properly encoded
- [ ] File saved as `.json` (not .txt, .doc, etc.)
- [ ] Backup created before major changes

---

## 🚀 After Updates

### **Always Follow This Process:**

1. **Edit** `jobs_database.json`
2. **Validate** using jsonlint.com
3. **Save** the file (Ctrl+S)
4. **Run script:** `python job_finder_v2.py`
5. **Verify** dashboard opens correctly
6. **Test** filters and search work
7. **Create backup** of updated database

---

## 📞 Troubleshooting Updates

### **Problem: Dashboard not updating**

Solution:
1. Ensure you saved `jobs_database.json`
2. Delete old `Government_Jobs_Dashboard_v2.html`
3. Run script again: `python job_finder_v2.py`

### **Problem: JSON validation fails**

Solution:
1. Copy your content to jsonlint.com
2. Follow error messages carefully
3. Check for missing commas or quotes
4. Restore from backup if too confused

### **Problem: Can't find the field to edit**

Solution:
1. Use browser's Find function (Ctrl+F)
2. Search for field name
3. Remember structure: jobs → job object → field

### **Problem: New job doesn't appear**

Solution:
1. Verify ID is unique and incremented
2. Ensure proper JSON formatting
3. Check that job is inside "jobs" array
4. Regenerate dashboard

---

## 📊 Maintaining Database Quality

### **Regular Maintenance Tasks**

**Weekly:**
- Check official websites for new notifications
- Update notification dates if found

**Monthly:**
- Review salaries for any changes
- Update eligibility criteria if changed
- Add new exams announced
- Remove outdated jobs

**Quarterly:**
- Full database audit
- Verify all links still work
- Update application fees if changed
- Add new organizations

### **Database Statistics**

After each update, note:
- Total jobs: _____
- GATE required: _____
- GATE not required: _____
- Organizations covered: _____
- Last updated: _____

---

## ✨ Best Practices

1. **Be Detailed:** More information = better user experience
2. **Keep Updated:** Set reminder to check official sites
3. **Verify Information:** Always confirm from official sources
4. **Test Changes:** Run script after every update
5. **Document Updates:** Keep changelog of what changed
6. **Backup Regularly:** Never lose your work
7. **Stay Organized:** Keep folder structure clean
8. **Communicate Changes:** Tell others about new jobs

---

## 🎓 Example: Complete Update Workflow

### **Scenario: New GATE Job Announced**

1. **Research:** Find details from official GATE website
2. **Backup:** Copy current `jobs_database.json`
3. **Edit:** Add new job entry with ID 14
4. **Validate:** Use jsonlint.com to verify
5. **Save:** Save the updated file
6. **Generate:** Run `python job_finder_v2.py`
7. **Test:** Open dashboard and search for new job
8. **Verify:** Ensure all details are correct
9. **Document:** Note update in changelog
10. **Share:** Inform others about new opportunity

---

**Remember:** The database is only as good as the information you put in it. 

Quality > Quantity ✨

---

**Happy Updating!** 🎉

