from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Set


# ---------- Strategy Configuration ----------

DEFAULT_STRATEGY = "smart_balance"

STRATEGIES: Dict[str, Dict[str, float]] = {
    # Favors low-effort "quick wins"
    "fastest_wins": {
        "urgency": 0.2,
        "importance": 0.3,
        "effort": 0.4,
        "dependencies": 0.1,
    },
    # Favors high-impact / high-importance tasks
    "high_impact": {
        "urgency": 0.2,
        "importance": 0.5,
        "effort": 0.1,
        "dependencies": 0.2,
    },
    # Favors deadlines above other concerns
    "deadline_driven": {
        "urgency": 0.6,
        "importance": 0.2,
        "effort": 0.1,
        "dependencies": 0.1,
    },
    # Balanced view across all dimensions
    "smart_balance": {
        "urgency": 0.35,
        "importance": 0.35,
        "effort": 0.15,
        "dependencies": 0.15,
    },
}


@dataclass
class TaskInternal:
    raw: dict
    id: str
    title: str
    due_date: Optional[date]
    estimated_hours: Optional[float]
    importance: Optional[int]
    dependencies: List[str]
    urgency_score: float = 0.0
    importance_score: float = 0.0
    effort_score: float = 0.0
    dependency_score: float = 0.0
    score: float = 0.0
    reasons: List[str] = field(default_factory=list)
    priority_label: str = "Low"


# ---------- Helper functions ----------

def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        # Accept "YYYY-MM-DD" or ISO-like formats
        return datetime.fromisoformat(value).date()
    except Exception:
        return None


def _normalize_importance(importance: Optional[int], reasons: List[str]) -> float:
    if importance is None:
        reasons.append("Importance not provided; using neutral value.")
        return 0.5
    try:
        importance = int(importance)
    except Exception:
        reasons.append("Importance invalid; using neutral value.")
        return 0.5
    if importance < 1 or importance > 10:
        reasons.append("Importance out of 1–10 range; clamped and normalized.")
        importance = max(1, min(importance, 10))
    norm = importance / 10.0
    if importance >= 8:
        reasons.append("Marked as very important.")
    elif importance <= 3:
        reasons.append("Task has relatively low importance.")
    return norm


def _compute_priority_label(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.5:
        return "Medium"
    return "Low"


def _detect_cycles(tasks_by_id: Dict[str, TaskInternal]) -> Set[str]:
    """
    Detect circular dependencies using DFS with coloring.
    Returns a set of task IDs that are part of at least one cycle.
    """
    graph = {tid: t.dependencies for tid, t in tasks_by_id.items()}
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {tid: WHITE for tid in graph}
    cycle_nodes: Set[str] = set()
    stack: List[str] = []

    def dfs(node: str):
        if color[node] != WHITE:
            return
        color[node] = GRAY
        stack.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in graph:
                # Dependency to a non-existent task – ignore for cycle purposes
                continue
            if color[neighbor] == WHITE:
                dfs(neighbor)
            elif color[neighbor] == GRAY:
                # Found a back edge → cycle
                if neighbor in stack:
                    idx = stack.index(neighbor)
                    cycle_nodes.update(stack[idx:])
        stack.pop()
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node)

    return cycle_nodes


# ---------- Core scoring function ----------

def analyze_tasks(
    tasks: List[dict],
    strategy_name: str = DEFAULT_STRATEGY,
    today: Optional[date] = None,
) -> List[dict]:
    """
    Main scoring function.
    - Accepts a list of task dicts.
    - Applies the chosen strategy weights.
    - Returns a *sorted* list of enriched task dicts with scores & reasons.
    """
    if today is None:
        today = date.today()

    strategy = STRATEGIES.get(strategy_name, STRATEGIES[DEFAULT_STRATEGY])

    # 1) Preprocess tasks into internal structure
    internal_tasks: List[TaskInternal] = []
    for idx, raw in enumerate(tasks):
        tid = str(raw.get("id") or f"T{idx + 1}")
        title = str(raw.get("title") or f"Task {tid}")
        due_date = _parse_date(raw.get("due_date"))
        estimated_hours = raw.get("estimated_hours")
        try:
            if estimated_hours is not None:
                estimated_hours = float(estimated_hours)
        except Exception:
            estimated_hours = None

        importance = raw.get("importance")
        try:
            if importance is not None:
                importance = int(importance)
        except Exception:
            importance = None

        dependencies = raw.get("dependencies") or []
        if not isinstance(dependencies, list):
            dependencies = []

        internal_tasks.append(
            TaskInternal(
                raw=raw,
                id=tid,
                title=title,
                due_date=due_date,
                estimated_hours=estimated_hours,
                importance=importance,
                dependencies=[str(d) for d in dependencies],
            )
        )

    tasks_by_id: Dict[str, TaskInternal] = {t.id: t for t in internal_tasks}

    # 2) Urgency scores
    for t in internal_tasks:
        if t.due_date is None:
            t.urgency_score = 0.3
            t.reasons.append("No valid due date; treated as moderately urgent.")
        else:
            delta = (t.due_date - today).days
            if delta < 0:
                t.urgency_score = 1.0
                t.reasons.append("Task is overdue.")
            elif delta == 0:
                t.urgency_score = 0.95
                t.reasons.append("Task is due today.")
            elif delta <= 3:
                t.urgency_score = 0.85
                t.reasons.append("Task is due within 3 days.")
            elif delta <= 7:
                t.urgency_score = 0.7
                t.reasons.append("Task is due within a week.")
            elif delta <= 14:
                t.urgency_score = 0.5
            elif delta <= 30:
                t.urgency_score = 0.35
            else:
                t.urgency_score = 0.2

    # 3) Importance scores
    for t in internal_tasks:
        t.importance_score = _normalize_importance(t.importance, t.reasons)

    # 4) Effort scores (quick wins → higher score for lower hours)
    valid_hours = [t.estimated_hours for t in internal_tasks if t.estimated_hours is not None]
    if valid_hours:
        min_h = min(valid_hours)
        max_h = max(valid_hours)
        span = max_h - min_h if max_h != min_h else 0.0

        for t in internal_tasks:
            if t.estimated_hours is None:
                t.effort_score = 0.5
                t.reasons.append("No estimated hours; treating effort as medium.")
            else:
                if span == 0:
                    t.effort_score = 0.6  # all similar
                else:
                    # normalize to [0,1] then invert so lower hours → higher score
                    norm = (t.estimated_hours - min_h) / span
                    t.effort_score = 1.0 - norm
                if t.effort_score >= 0.8:
                    t.reasons.append("Quick win based on low estimated effort.")
    else:
        # No effort info at all
        for t in internal_tasks:
            t.effort_score = 0.5
            t.reasons.append("No effort estimates available; using neutral effort score.")

    # 5) Dependency score (tasks that many others depend on)
    dependents_count: Dict[str, int] = {t.id: 0 for t in internal_tasks}
    for t in internal_tasks:
        for dep in t.dependencies:
            if dep in dependents_count:
                dependents_count[dep] += 1

    max_dep = max(dependents_count.values()) if dependents_count else 0
    for t in internal_tasks:
        count = dependents_count.get(t.id, 0)
        if max_dep > 0:
            t.dependency_score = count / max_dep
        else:
            t.dependency_score = 0.0
        if count > 0:
            t.reasons.append(
                f"Blocks {count} other task(s), so prioritized higher."
            )

    # 6) Circular dependency detection
    cycle_task_ids = _detect_cycles(tasks_by_id)
    if cycle_task_ids:
        for tid in cycle_task_ids:
            if tid in tasks_by_id:
                tasks_by_id[tid].reasons.append(
                    "Warning: Task is part of a circular dependency."
                )

    # 7) Final score aggregation
    wu = strategy["urgency"]
    wi = strategy["importance"]
    we = strategy["effort"]
    wd = strategy["dependencies"]

    for t in internal_tasks:
        t.score = (
            wu * t.urgency_score
            + wi * t.importance_score
            + we * t.effort_score
            + wd * t.dependency_score
        )
        t.priority_label = _compute_priority_label(t.score)

    # 8) Sort by score (descending)
    internal_tasks.sort(key=lambda t: t.score, reverse=True)

    # 9) Build external response dicts
    result: List[dict] = []
    for t in internal_tasks:
        out = {
            "id": t.id,
            "title": t.title,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "estimated_hours": t.estimated_hours,
            "importance": t.importance,
            "dependencies": t.dependencies,
            "urgency_score": round(t.urgency_score, 4),
            "importance_score": round(t.importance_score, 4),
            "effort_score": round(t.effort_score, 4),
            "dependency_score": round(t.dependency_score, 4),
            "score": round(t.score, 4),
            "priority_label": t.priority_label,
            "reasons": t.reasons,
        }
        result.append(out)

    return result
