# SmartAgriculture Backend API

## Setup Guide (for hardware team)

### Step 1: Clone the repository
```bash
git clone https://github.com/your-team/smartagriculture.git
cd smartagriculture
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install PostgreSQL
Download from: https://www.postgresql.org/download/

### Step 4: Create the database
```bash
createdb -U postgres smartagriculture
```

### Step 5: Update config.py
```python
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/smartagriculture"
```

### Step 6: Run the server
```bash
python app.py
```

You should see:
```
Database tables created.
Diseases seeded successfully.
Running on http://0.0.0.0:5000
```

---

## API Reference

### Base URL
```
http://<laptop-ip>:5000
```
Replace `<laptop-ip>` with the IP address of the laptop running the server.
Both the laptop and Arduino must be on the same WiFi network.

To find the laptop IP, run:
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
```
Look for something like `192.168.1.X`

---

## API 1 — Submit a Scan

**The most important endpoint. Robot calls this after scanning each plant.**

```
POST /api/v1/scans
```

**Request format:** `multipart/form-data`

| Key | Type | Required | Example | Description |
|---|---|---|---|---|
| image | File | Yes | leaf.jpg | Photo of the plant leaf |
| latitude | Text | Yes | 21.1458 | GPS latitude of the plant |
| longitude | Text | Yes | 79.0882 | GPS longitude of the plant |
| timestamp | Text | Yes | 2026-06-25T10:15:00 | When the scan happened (ISO format) |

**Success Response (201):**
```json
{
  "scan_id": 1,
  "plant_id": 1,
  "disease": "early_blight",
  "confidence": 0.91,
  "pesticide": "Chlorothalonil",
  "dosage": "2 g/L",
  "spray_interval_days": 7,
  "task_created": true,
  "status": "task_created"
}
```

**If plant is healthy, response will be:**
```json
{
  "scan_id": 2,
  "plant_id": 2,
  "disease": "healthy",
  "confidence": 0.95,
  "pesticide": null,
  "dosage": null,
  "spray_interval_days": null,
  "task_created": false,
  "status": "no_action_needed"
}
```

**Error Responses (400):**
```json
{ "error": "No image sent. Use key 'image'." }
{ "error": "No latitude sent. Use key 'latitude'." }
{ "error": "No longitude sent. Use key 'longitude'." }
{ "error": "No timestamp sent. Use key 'timestamp'." }
```

---

## API 2 — Get Pending Tasks

**Robot calls this to get its list of plants that need pesticide sprayed.**

```
GET /api/v1/tasks/pending
```

**No request body needed.**

**Success Response (200):**
```json
[
  {
    "task_id": 1,
    "plant_id": 1,
    "latitude": 21.1458,
    "longitude": 79.0882,
    "disease": "early_blight",
    "pesticide": "Chlorothalonil",
    "dosage": "2 g/L",
    "spray_interval_days": 7,
    "status": "pending"
  },
  {
    "task_id": 2,
    "plant_id": 3,
    "latitude": 21.1461,
    "longitude": 79.0885,
    "disease": "late_blight",
    "pesticide": "Mancozeb",
    "dosage": "2 g/L",
    "spray_interval_days": 5,
    "status": "pending"
  }
]
```

**If no pending tasks:**
```json
[]
```

---

## API 3 — Mark Task as Complete

**Robot calls this after it has finished spraying a plant.**

```
PATCH /api/v1/tasks/<task_id>/complete
```

Replace `<task_id>` with the actual task ID received from API 2.

**No request body needed.**

**Example:**
```
PATCH /api/v1/tasks/1/complete
```

**Success Response (200):**
```json
{
  "task_id": 1,
  "status": "completed",
  "message": "Task marked as completed successfully."
}
```

**If task not found (404):**
```json
{ "error": "Task not found." }
```

---

## API 4 — Get All Scans (Dashboard)

**For the farmer dashboard — shows full history of all scans.**

```
GET /api/v1/scans
```

**No request body needed.**

**Success Response (200):**
```json
[
  {
    "scan_id": 1,
    "plant_id": 1,
    "latitude": 21.1458,
    "longitude": 79.0882,
    "timestamp": "2026-06-25T10:15:00",
    "disease": "early_blight",
    "pesticide": "Chlorothalonil",
    "dosage": "2 g/L",
    "confidence": 0.91
  }
]
```

---

## API 5 — Get All Tasks (Dashboard)

**For the farmer dashboard — shows all tasks, both pending and completed.**

```
GET /api/v1/tasks
```

**No request body needed.**

**Success Response (200):**
```json
[
  {
    "task_id": 1,
    "plant_id": 1,
    "latitude": 21.1458,
    "longitude": 79.0882,
    "disease": "early_blight",
    "pesticide": "Chlorothalonil",
    "dosage": "2 g/L",
    "spray_interval_days": 7,
    "status": "completed",
    "created_at": "2026-06-25T10:15:00",
    "completed_at": "2026-06-25T11:00:00"
  }
]
```

---

## Disease Reference Table

| Disease | Pesticide | Dosage | Spray Interval |
|---|---|---|---|
| healthy | None | N/A | N/A |
| early_blight | Chlorothalonil | 2 g/L | Every 7 days |
| late_blight | Mancozeb | 2 g/L | Every 5 days |
| leaf_mold | Chlorothalonil | 2 g/L | Every 7 days |
| mosaic_virus | Remove plant | N/A | N/A |

---

## Complete Robot Workflow

```
1. Robot starts scanning row by row
         ↓
2. For each plant: capture image + get GPS location + get timestamp
         ↓
3. POST /api/v1/scans  (send image + latitude + longitude + timestamp)
         ↓
4. Check response:
   - "status": "task_created"    → plant is diseased, task created
   - "status": "no_action_needed" → plant is healthy, move to next plant
         ↓
5. After scanning all plants:
   GET /api/v1/tasks/pending  → get list of all plants to spray
         ↓
6. For each task: go to latitude/longitude, spray the pesticide
         ↓
7. After spraying each plant:
   PATCH /api/v1/tasks/<task_id>/complete
         ↓
8. Repeat for next scan round
```

---

## Testing with Postman

If you don't have the hardware ready yet, you can test the API using Postman:

**POST /api/v1/scans:**
- Method: POST
- URL: http://127.0.0.1:5000/api/v1/scans
- Body: form-data
  - image (File): any .jpg image
  - latitude (Text): 21.1458
  - longitude (Text): 79.0882
  - timestamp (Text): 2026-06-25T10:15:00

**GET /api/v1/tasks/pending:**
- Method: GET
- URL: http://127.0.0.1:5000/api/v1/tasks/pending

**PATCH /api/v1/tasks/1/complete:**
- Method: PATCH
- URL: http://127.0.0.1:5000/api/v1/tasks/1/complete

---

## Contact

For API questions or issues, contact: **Nitin (Portfolio 2 — Backend Lead)**
