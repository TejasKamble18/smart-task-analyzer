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

🧠 Algorithm Explanation (300–400 words)
The Smart Task Analyzer algorithm calculates a composite priority score based on four dimensions: urgency, importance, effort, and dependencies.

Urgency is derived from the due date. Tasks that are overdue receive the highest urgency boost since they represent immediate risk. Tasks closer to their deadline also score higher. Missing or invalid due dates are handled gracefully by treating them as neutral urgency instead of generating errors.

Importance is a direct user-provided score ranging from 1 to 10. This reflects business impact and contributes strongly to the final score. Higher importance naturally increases ranking.

Effort uses the estimated number of hours required. The algorithm favors “quick wins,” meaning that tasks requiring fewer hours gain a slight bonus. This helps users complete small tasks rapidly and maintain momentum.

Dependencies add an intelligent layer to prioritization. A task that unblocks others is considered more valuable to complete early. The system constructs a dependency graph and counts how many tasks depend on each task. Tasks that unlock multiple others receive a multiplier bonus. Circular dependencies are detected via depth-first search; tasks inside cycles are marked with warnings rather than breaking the algorithm.

All four components are normalized to a 0–1 scale. A weighted scoring formula combines them, with urgency and importance weighted slightly more than effort. The dependency multiplier is applied at the end to reward unblockers.

The system supports multiple strategies:

Smart Balance (default) blends all factors.

Deadline Driven prioritizes urgency.

High Impact focuses purely on importance.

Fastest Wins favors low-effort tasks.

This ensures flexibility across different work styles.

🕸 Dependency Graph Visualization (SVG)
After task analysis, the frontend draws a circular graph where:

Each node represents a task

Arrows represent dependencies

Node color shows priority level

Layout adjusts dynamically based on task count

This visualization helps identify bottleneck tasks and circular dependencies instantly.

🧪 Running Tests
bash
Copy code
python manage.py test tasks
Tests cover:

Score comparisons

Strategy behaviors

Circular dependency detection

🕒 Time Breakdown
Backend (API + scoring algorithm): 2 hours

Frontend (UI + table + fetch + graph): 1.5 hours

Testing: 30 minutes

CORS, debugging, integration: 30 minutes

README + polishing: 30 minutes

🔮 Future Improvements
User-configurable algorithm weight settings
Database persistence for tasks
Draggable Kanban / Eisenhower board
Machine learning “Learning Mode”
Holiday/weekend-aware urgency
Swagger API documentation

