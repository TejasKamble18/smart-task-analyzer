// === CONFIG ===
const API_BASE_URL = "http://127.0.0.1:8000/api";

// We keep current tasks in memory (what you add via form / JSON)
let currentTasks = [];

// Utility: create element with classes
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (typeof text === "string") node.textContent = text;
  return node;
}

// === DOM ELEMENTS ===
const taskForm = document.getElementById("task-form");
const idInput = document.getElementById("task-id-input");
const titleInput = document.getElementById("task-title-input");
const dueDateInput = document.getElementById("task-due-date-input");
const hoursInput = document.getElementById("task-estimated-hours-input");
const importanceInput = document.getElementById("task-importance-input");
const depsInput = document.getElementById("task-dependencies-input");

const addTaskBtn = document.getElementById("add-task-btn");
const clearTasksBtn = document.getElementById("clear-tasks-btn");
const taskListBody = document.getElementById("task-list-body");

const bulkJsonInput = document.getElementById("bulk-json-input");
const loadJsonBtn = document.getElementById("load-json-btn");

const strategySelect = document.getElementById("strategy-select");
const analyzeBtn = document.getElementById("analyze-btn");
const suggestBtn = document.getElementById("suggest-btn");

const statusBar = document.getElementById("status-bar");
const analysisBody = document.getElementById("analysis-body");
const analysisSubtitle = document.getElementById("analysis-subtitle");
const activeStrategyPill = document.getElementById("active-strategy-pill");

const graphSvg = document.getElementById("dependency-graph");
const graphEmptyState = document.getElementById("graph-empty-state");

// === HELPERS ===

function setStatus(message, isError = false) {
  statusBar.innerHTML = message;
  statusBar.style.borderColor = isError
    ? "rgba(248,113,113,0.8)"
    : "rgba(148,163,184,0.35)";
  statusBar.style.color = isError ? "#fecaca" : "#9ca3af";
}

function generateTaskId() {
  // Simple auto ID if user doesn't provide one
  let idx = currentTasks.length + 1;
  let candidate = `T${idx}`;
  const used = new Set(currentTasks.map((t) => String(t.id)));
  while (used.has(candidate)) {
    idx += 1;
    candidate = `T${idx}`;
  }
  return candidate;
}

function parseDependencies(value) {
  if (!value) return [];
  return value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function renderTaskList() {
  taskListBody.innerHTML = "";
  if (!currentTasks.length) {
    const row = el("tr");
    const cell = el("td", null, "No tasks yet. Add tasks from the form above.");
    cell.colSpan = 6;
    cell.style.color = "#9ca3af";
    row.appendChild(cell);
    taskListBody.appendChild(row);
    return;
  }

  for (const task of currentTasks) {
    const row = el("tr");
    const depsDisplay = (task.dependencies || []).join(", ");

    const dueText = task.due_date || "–";
    const hoursText =
      task.estimated_hours === null || task.estimated_hours === undefined
        ? "–"
        : String(task.estimated_hours);
    const impText =
      task.importance === null || task.importance === undefined
        ? "–"
        : String(task.importance);

    const cells = [
      task.id || "–",
      task.title || "–",
      dueText,
      hoursText,
      impText,
      depsDisplay || "–",
    ];

    for (const value of cells) {
      row.appendChild(el("td", null, value));
    }

    taskListBody.appendChild(row);
  }
}

// Priority pill HTML
function priorityPill(label) {
  const span = document.createElement("span");
  span.classList.add("priority-pill");
  if (label === "High") {
    span.classList.add("priority-high");
  } else if (label === "Medium") {
    span.classList.add("priority-medium");
  } else {
    span.classList.add("priority-low");
  }
  span.textContent = label;
  return span.outerHTML;
}

// === RENDER ANALYSIS TABLE ===

function renderAnalysis(tasks, strategyName, sourceLabel) {
  analysisBody.innerHTML = "";

  if (!tasks || !tasks.length) {
    analysisSubtitle.textContent = "No analyzed tasks to display yet.";
    activeStrategyPill.textContent = "Strategy: –";
    return;
  }

  analysisSubtitle.textContent =
    sourceLabel || "Sorted by descending priority score.";
  activeStrategyPill.textContent = `Strategy: ${strategyName}`;

  tasks.forEach((task, index) => {
    const row = el("tr");

    const rankCell = el("td", null, String(index + 1));
    const taskCell = el("td");
    const scoreCell = el("td");
    const priorityCell = el("td");
    const dueCell = el("td");
    const hoursCell = el("td");
    const impCell = el("td");
    const whyCell = el("td");

    taskCell.textContent = task.title || task.id || "Untitled task";

    scoreCell.textContent =
      typeof task.score === "number" ? task.score.toFixed(3) : "–";

    const label = task.priority_label || "Low";
    priorityCell.innerHTML = priorityPill(label);

    dueCell.textContent = task.due_date || "–";
    hoursCell.textContent =
      task.estimated_hours === null || task.estimated_hours === undefined
        ? "–"
        : String(task.estimated_hours);
    impCell.textContent =
      task.importance === null || task.importance === undefined
        ? "–"
        : String(task.importance);

    const reasons = Array.isArray(task.reasons) ? task.reasons : [];
    whyCell.textContent =
      reasons.length > 0 ? reasons.join(" • ") : "No explanation available.";

    row.appendChild(rankCell);
    row.appendChild(taskCell);
    row.appendChild(scoreCell);
    row.appendChild(priorityCell);
    row.appendChild(dueCell);
    row.appendChild(hoursCell);
    row.appendChild(impCell);
    row.appendChild(whyCell);

    analysisBody.appendChild(row);
  });
}

// === DEPENDENCY GRAPH RENDERING ===

function clearGraph() {
  while (graphSvg.firstChild) {
    graphSvg.removeChild(graphSvg.firstChild);
  }
}

function renderDependencyGraph(tasks) {
  clearGraph();

  if (!tasks || !tasks.length) {
    graphEmptyState.style.display = "flex";
    return;
  }
  graphEmptyState.style.display = "none";

  const width = 800;
  const height = 400;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 2.6;

  const positions = {};
  const n = tasks.length;

  // Place nodes on a circle
  tasks.forEach((task, index) => {
    const angle = (2 * Math.PI * index) / n - Math.PI / 2;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    positions[task.id] = { x, y };
  });

  // Helper to create SVG elements
  function svgEl(tag, attrs = {}) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [key, value] of Object.entries(attrs)) {
      node.setAttribute(key, value);
    }
    return node;
  }

  // Optional: add arrow marker
  const defs = svgEl("defs");
  const marker = svgEl("marker", {
    id: "arrowhead",
    viewBox: "0 0 10 10",
    refX: "10",
    refY: "5",
    markerWidth: "6",
    markerHeight: "6",
    orient: "auto-start-reverse",
  });
  const markerPath = svgEl("path", {
    d: "M 0 0 L 10 5 L 0 10 z",
    fill: "rgba(148,163,184,0.9)",
  });
  marker.appendChild(markerPath);
  defs.appendChild(marker);
  graphSvg.appendChild(defs);

  // Draw edges (dependency -> task)
  tasks.forEach((task) => {
    const deps = Array.isArray(task.dependencies) ? task.dependencies : [];
    deps.forEach((depId) => {
      const from = positions[depId];
      const to = positions[task.id];
      if (!from || !to) return;

      const line = svgEl("line", {
        x1: from.x,
        y1: from.y,
        x2: to.x,
        y2: to.y,
        stroke: "rgba(148,163,184,0.75)",
        "stroke-width": "1.5",
        "marker-end": "url(#arrowhead)",
      });
      graphSvg.appendChild(line);
    });
  });

  // Draw nodes
  tasks.forEach((task) => {
    const pos = positions[task.id];
    if (!pos) return;

    const group = svgEl("g", {});

    // Node circle color based on priority
    let fill = "rgba(59,130,246,0.85)";
    if (task.priority_label === "High") {
      fill = "rgba(34,197,94,0.85)";
    } else if (task.priority_label === "Medium") {
      fill = "rgba(234,179,8,0.9)";
    } else if (task.priority_label === "Low") {
      fill = "rgba(249,115,22,0.9)";
    }

    const circle = svgEl("circle", {
      cx: pos.x,
      cy: pos.y,
      r: 22,
      fill,
      stroke: "rgba(15,23,42,1)",
      "stroke-width": "2",
    });

    const idLabel = svgEl("text", {
      x: pos.x,
      y: pos.y - 2,
      "text-anchor": "middle",
      "dominant-baseline": "central",
      "font-size": "11",
      "font-weight": "700",
      fill: "#0b1120",
    });
    idLabel.textContent = task.id || "?";

    const titleLabel = svgEl("text", {
      x: pos.x,
      y: pos.y + 24,
      "text-anchor": "middle",
      "font-size": "9",
      fill: "rgba(148,163,184,0.9)",
    });
    const truncatedTitle =
      (task.title || "").length > 18
        ? (task.title || "").slice(0, 16) + "…"
        : task.title || "";
    titleLabel.textContent = truncatedTitle;

    group.appendChild(circle);
    group.appendChild(idLabel);
    group.appendChild(titleLabel);
    graphSvg.appendChild(group);
  });
}

// === EVENT HANDLERS ===

// Add single task
addTaskBtn.addEventListener("click", () => {
  const title = titleInput.value.trim();
  if (!title) {
    setStatus("Please provide at least a task title.", true);
    return;
  }

  let id = idInput.value.trim();
  if (!id) {
    id = generateTaskId();
  }

  const dueDate = dueDateInput.value ? dueDateInput.value : null;

  let estimatedHours = null;
  if (hoursInput.value.trim() !== "") {
    const parsed = Number(hoursInput.value);
    if (Number.isNaN(parsed) || parsed < 0) {
      setStatus("Estimated hours must be a non-negative number.", true);
      return;
    }
    estimatedHours = parsed;
  }

  let importance = null;
  if (importanceInput.value.trim() !== "") {
    const parsedImp = Number(importanceInput.value);
    if (
      Number.isNaN(parsedImp) ||
      parsedImp < 1 ||
      parsedImp > 10 ||
      !Number.isInteger(parsedImp)
    ) {
      setStatus("Importance must be an integer between 1 and 10.", true);
      return;
    }
    importance = parsedImp;
  }

  const dependencies = parseDependencies(depsInput.value);

  const task = {
    id,
    title,
    due_date: dueDate,
    estimated_hours: estimatedHours,
    importance,
    dependencies,
  };

  currentTasks.push(task);
  renderTaskList();
  setStatus(`Task "${title}" added to the list.`);
});

// Clear all tasks
clearTasksBtn.addEventListener("click", () => {
  currentTasks = [];
  renderTaskList();
  analysisBody.innerHTML = "";
  clearGraph();
  graphEmptyState.style.display = "flex";
  setStatus("All tasks cleared.");
});

// Load JSON as tasks
loadJsonBtn.addEventListener("click", () => {
  const raw = bulkJsonInput.value.trim();
  if (!raw) {
    setStatus("Please paste a JSON array of tasks first.", true);
    return;
  }

  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      setStatus("JSON must be an array of task objects.", true);
      return;
    }

    // Basic normalization
    currentTasks = parsed.map((t, idx) => {
      const id = String(t.id || `T${idx + 1}`);
      const deps = Array.isArray(t.dependencies)
        ? t.dependencies.map((d) => String(d))
        : [];
      return {
        id,
        title: t.title || `Task ${id}`,
        due_date: t.due_date || null,
        estimated_hours:
          typeof t.estimated_hours === "number"
            ? t.estimated_hours
            : t.estimated_hours
            ? Number(t.estimated_hours)
            : null,
        importance:
          typeof t.importance === "number"
            ? t.importance
            : t.importance
            ? Number(t.importance)
            : null,
        dependencies: deps,
      };
    });

    renderTaskList();
    setStatus(
      `Loaded ${currentTasks.length} task(s) from JSON into the current list.`
    );
  } catch (err) {
    console.error(err);
    setStatus("Invalid JSON. Please check your syntax.", true);
  }
});

// Analyze tasks
analyzeBtn.addEventListener("click", async () => {
  if (!currentTasks.length) {
    setStatus("Add at least one task before analyzing.", true);
    return;
  }

  const strategy = strategySelect.value || "smart_balance";

  analyzeBtn.disabled = true;
  suggestBtn.disabled = true;
  setStatus("Analyzing tasks with current strategy…");

  try {
    const payload = {
      strategy,
      tasks: currentTasks,
    };

    const response = await fetch(`${API_BASE_URL}/tasks/analyze/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const data = await response.json();
    const tasks = data.tasks || data || [];
    renderAnalysis(tasks, data.strategy || strategy, "Sorted by priority score.");
    renderDependencyGraph(tasks);
    setStatus("Analysis complete. Tasks are sorted by priority.");
  } catch (err) {
    console.error(err);
    setStatus("Failed to analyze tasks. Check console for details.", true);
  } finally {
    analyzeBtn.disabled = false;
    suggestBtn.disabled = false;
  }
});

// Suggest top 3 tasks
suggestBtn.addEventListener("click", async () => {
  analyzeBtn.disabled = true;
  suggestBtn.disabled = true;
  setStatus("Requesting top 3 suggestions from backend…");

  try {
    const response = await fetch(`${API_BASE_URL}/tasks/suggest/`);
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }
    const data = await response.json();
    const tasks = data.tasks || data || [];
    renderAnalysis(
      tasks,
      data.strategy || "smart_balance",
      "Top 3 tasks recommended for today."
    );
    // Use suggestion tasks for a local mini-graph
    renderDependencyGraph(tasks);
    setStatus("Suggestions loaded successfully.");
  } catch (err) {
    console.error(err);
    setStatus("Failed to load suggestions. Check console for details.", true);
  } finally {
    analyzeBtn.disabled = false;
    suggestBtn.disabled = false;
  }
});

// Initial render
renderTaskList();
clearGraph();
graphEmptyState.style.display = "flex";
setStatus("Ready. Add tasks and choose a strategy to analyze.");
