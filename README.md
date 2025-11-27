# Smart Task Analyzer  
A full-stack task prioritization system that scores, sorts, and visualizes tasks using a balanced algorithm based on urgency, importance, effort, and dependencies.  


- Algorithm design  
- Backend development (Python + Django REST Framework)  
- Frontend engineering (HTML/CSS/JavaScript)  
- Critical thinking & problem-solving  
- API design & testing  
- Data visualization (SVG dependency graph)

---

# 🚀 Features

### ✅ **Backend (Django + DRF)**
- Custom scoring algorithm (Smart Balance)
- Multiple prioritization strategies:
  - Smart Balance  
  - Deadline Driven  
  - High Impact  
  - Fastest Wins  
- Circular dependency detection  
- Human-readable explanations for every task  
- Top 3 task suggestions  
- Automated tests for algorithm correctness  
- CORS-enabled for frontend communication  

### ✅ **Frontend (HTML + CSS + JavaScript)**
- Add tasks via form
- Bulk JSON import
- Strategy selection dropdown
- Ranked task table with scores + explanations
- **Dependency graph visualization using pure SVG**
- Error handling, validation & status messages
- Responsive, clean UI

---

# 🧱 Project Structure

task-analyzer/
├── backend/
│ ├── manage.py
│ ├── task_analyzer/
│ │ ├── settings.py
│ │ ├── urls.py
│ │ └── wsgi.py
│ ├── tasks/
│ │ ├── scoring.py
│ │ ├── views.py
│ │ ├── urls.py
│ │ ├── tests.py
│ │ ├── models.py
│ │ └── serializers.py
│ └── requirements.txt
├── frontend/
│ ├── index.html
│ ├── styles.css
│ └── script.js
└── README.md

yaml
Copy code

---

# ⚙️ Setup Instructions

## **1️⃣ Backend Setup**
Run these commands inside:

task-analyzer/backend/

shell
Copy code

### Install dependencies
pip install -r requirements.txt

shell
Copy code

### Run migrations
python manage.py migrate

shell
Copy code

### Run backend server
python manage.py runserver

yaml
Copy code

Backend runs at:

http://127.0.0.1:8000/

yaml
Copy code

---

## **2️⃣ Frontend Setup**

No build tools needed.

Open the frontend using **Live Server** (VS Code):

Right-click → **Open with Live Server**

It will run at:

http://127.0.0.1:5500/frontend/index.html

yaml
Copy code

---

# 🔥 Core API Endpoints

### **POST /api/tasks/analyze/**
Input:

```json
{
  "strategy": "smart_balance",
  "tasks": [
    {
      "id": "T1",
      "title": "Fix Login Bug",
      "due_date": "2025-11-30",
      "estimated_hours": 2,
      "importance": 9,
      "dependencies": []
    }
  ]
}
Output:

json
Copy code
{
  "strategy": "smart_balance",
  "tasks": [
    {
      "id": "T1",
      "score": 0.72,
      "priority_label": "Medium",
      "reasons": [
        "Due soon (within X days).",
        "Marked as very important.",
        "Quick win based on low estimated effort."
      ]
    }
  ]
}
GET /api/tasks/suggest/
Returns the top 3 tasks with explanations.

🧠 Algorithm Explanation

The Smart Task Analyzer algorithm calculates a composite priority score using four key dimensions: urgency, importance, effort, and dependencies.

Urgency

Derived from the task’s due date.

Overdue tasks receive the highest urgency boost because they represent immediate risk.

Tasks closer to their deadline get progressively higher scores.

Missing or invalid due dates are treated as neutral urgency rather than causing errors.

Importance

A direct user-provided score from 1–10.

Reflects business or functional impact.

Strongly influences the priority score.

Higher importance directly increases ranking.

Effort

Based on the estimated number of hours required.

The algorithm favors quick wins.

Lower-effort tasks receive a bonus, helping users build momentum by completing small tasks early.

Dependencies

Dependencies introduce a structural layer to prioritization.

A task that unblocks other tasks is treated as more valuable to complete early.

A dependency graph is constructed, counting how many tasks depend on a given task.

Tasks that unlock multiple others receive a multiplier bonus.

Circular dependencies are detected via depth-first search (DFS); tasks inside cycles are flagged without breaking processing.

Weighting & Scoring

All four factors are normalized to a 0–1 scale.
A weighted formula combines the components:

Urgency and importance hold slightly higher weight.

Effort contributes as a quick-win modifier.

Dependency multiplier is applied last to emphasize high-leverage tasks.

Supported Strategies

Smart Balance (Default): Blends urgency, importance, effort, and dependencies.

Deadline Driven: Focuses primarily on urgency.

High Impact: Prioritizes importance above everything else.

Fastest Wins: Ranks based on least effort first.

This multi-strategy system ensures flexibility across different workflows and user preferences.

🕸 Dependency Graph Visualization (SVG)

After task analysis, the frontend generates a real-time SVG graph where:

Each node represents a task

Arrows represent dependencies

Node color reflects priority level

Layout adjusts dynamically based on the number of tasks

This visualization instantly highlights:

Bottleneck tasks

Unblockers

Circular dependency issues

Task clusters

🧪 Running Tests
python manage.py test tasks


Tests include:

Score validation

Strategy accuracy

Circular dependency detection

Edge-case handling

🕒 Time Breakdown
Component	Time Spent
Backend (API + scoring engine)	2 hours
Frontend (UI + fetch + graph)	1.5 hours
Testing	30 minutes
CORS, debugging & integration	30 minutes
README preparation & polishing	30 minutes
🔮 Future Improvements

User-configurable weighting for scoring algorithm

Database persistence (store tasks per user)

Swagger/OpenAPI documentation

Kanban/Eisenhower Matrix view

AI-based learning mode (adjust scoring based on user habits)

Weekend/holiday-aware urgency calculations
Draggable Kanban / Eisenhower board
Machine learning “Learning Mode”
Holiday/weekend-aware urgency
Swagger API documentation

