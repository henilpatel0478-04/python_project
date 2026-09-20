/**
 * Study Planner - Main Application Logic
 * Integrates with Python recommendation engine via Flask REST API.
 */

// Application State
let appState = {
  availableHours: 6.0,
  startTime: "09:00",
  sessionLength: 50,
  breakLength: 10,
  subjects: [],
  currentPlan: null,
  completedSlots: new Set()
};

// Pomodoro Timer State
let timerState = {
  totalSeconds: 25 * 60,
  remainingSeconds: 25 * 60,
  isRunning: false,
  intervalId: null,
  activeSubject: "Machine Learning",
  activeTask: "Deep Dive: Tackle core formulas and problem sets",
  mode: "work" // "work" | "break"
};

// Colors for visual segments
const PALETTE = [
  "#6366f1", "#06b6d4", "#ec4899", "#8b5cf6", "#f59e0b", 
  "#10b981", "#3b82f6", "#14b8a6", "#f43f5e", "#a855f7"
];

// Document Ready
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initUIEventListeners();
  loadInitialData();
});

// Day / Night Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem("studyPlannerTheme") || "dark";
  applyTheme(savedTheme);
}

function applyTheme(theme) {
  const moonIcon = document.getElementById("themeMoonIcon");
  const sunIcon = document.getElementById("themeSunIcon");
  const themeLabel = document.getElementById("themeLabel");

  if (theme === "light") {
    document.body.setAttribute("data-theme", "light");
    if (moonIcon) moonIcon.style.display = "none";
    if (sunIcon) sunIcon.style.display = "inline-flex";
    if (themeLabel) themeLabel.textContent = "Day";
  } else {
    document.body.removeAttribute("data-theme");
    if (moonIcon) moonIcon.style.display = "inline-flex";
    if (sunIcon) sunIcon.style.display = "none";
    if (themeLabel) themeLabel.textContent = "Night";
  }
  localStorage.setItem("studyPlannerTheme", theme);
}

function toggleTheme() {
  const isCurrentlyLight = document.body.getAttribute("data-theme") === "light";
  const newTheme = isCurrentlyLight ? "dark" : "light";
  applyTheme(newTheme);
  playTickTone(newTheme === "light" ? 750 : 450);
  showToast(`Switched to ${newTheme === "light" ? "☀️ Day (Light)" : "🌙 Night (Dark)"} Mode`);
}

// Setup DOM Event Listeners
function initUIEventListeners() {
  // Day / Night Mode Toggle
  const themeBtn = document.getElementById("themeToggleBtn");
  if (themeBtn) {
    themeBtn.addEventListener("click", toggleTheme);
  }

  // Available Hours Slider
  const hoursSlider = document.getElementById("availableHours");
  const hoursDisplay = document.getElementById("hoursValDisplay");
  hoursSlider.addEventListener("input", (e) => {
    appState.availableHours = parseFloat(e.target.value);
    hoursDisplay.textContent = `${appState.availableHours.toFixed(1)} hrs`;
  });

  // Settings
  document.getElementById("startTime").addEventListener("change", (e) => {
    appState.startTime = e.target.value;
  });
  document.getElementById("sessionLength").addEventListener("change", (e) => {
    appState.sessionLength = parseInt(e.target.value);
  });

  // Add Subject Button
  document.getElementById("addSubjectBtn").addEventListener("click", () => {
    addNewSubject();
  });

  // Generate Plan Button
  document.getElementById("generatePlanBtn").addEventListener("click", () => {
    generatePlan();
  });

  // Presets
  const presetBtns = document.querySelectorAll(".preset-btn");
  presetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      presetBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      loadPreset(btn.dataset.preset);
    });
  });

  // Print / PDF Button
  document.getElementById("printBtn").addEventListener("click", () => {
    window.print();
  });

  // Reset Progress Button
  document.getElementById("resetDoneBtn").addEventListener("click", () => {
    appState.completedSlots.clear();
    saveCompletedSlots();
    renderTimetableProgress();
    showToast("Progress has been reset for today.");
  });

  // Timer Modal Triggers
  const timerModal = document.getElementById("timerModal");
  document.getElementById("openTimerBtn").addEventListener("click", () => {
    timerModal.classList.add("open");
  });
  document.getElementById("closeTimerModalBtn").addEventListener("click", () => {
    timerModal.classList.remove("open");
  });
  timerModal.addEventListener("click", (e) => {
    if (e.target === timerModal) timerModal.classList.remove("open");
  });

  // Timer Controls
  document.getElementById("timerToggleBtn").addEventListener("click", toggleTimer);
  document.getElementById("timerResetBtn").addEventListener("click", resetTimer);
  document.getElementById("timerSkipBtn").addEventListener("click", skipTimerInterval);

  // Timer Quick Presets
  const timerPresetBtns = document.querySelectorAll(".timer-preset-btn");
  timerPresetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      timerPresetBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const mins = parseInt(btn.dataset.time);
      setTimerDuration(mins, mins < 20 ? "break" : "work");
    });
  });
}

function getFallbackPresets() {
  const today = new Date();
  const addDays = (d) => {
    const target = new Date();
    target.setDate(today.getDate() + d);
    return target.toISOString().split("T")[0];
  };

  return {
    aiml: {
      title: "🤖 AIML Semester Exam Prep",
      available_hours: 6.0,
      start_time: "09:00",
      session_length: 50,
      break_length: 10,
      subjects: [
        { name: "Machine Learning", exam_date: addDays(4), current_marks: 52, difficulty: "weak" },
        { name: "Linear Algebra & Vectors", exam_date: addDays(8), current_marks: 64, difficulty: "neutral" },
        { name: "Python for Data Science", exam_date: addDays(14), current_marks: 88, difficulty: "strong" },
        { name: "Deep Learning & Neural Nets", exam_date: addDays(6), current_marks: 45, difficulty: "weak" },
        { name: "Probability & Statistics", exam_date: addDays(12), current_marks: 72, difficulty: "neutral" }
      ]
    },
    cs_core: {
      title: "⚡ CS Core Crunch Week",
      available_hours: 5.0,
      start_time: "10:00",
      session_length: 45,
      break_length: 10,
      subjects: [
        { name: "Data Structures & Algorithms", exam_date: addDays(3), current_marks: 58, difficulty: "weak" },
        { name: "Operating Systems", exam_date: addDays(7), current_marks: 70, difficulty: "neutral" },
        { name: "Database Management (SQL)", exam_date: addDays(11), current_marks: 85, difficulty: "strong" }
      ]
    },
    python_essentials: {
      title: "🐍 Python Essentials Bootcamp",
      available_hours: 4.0,
      start_time: "08:30",
      session_length: 50,
      break_length: 10,
      subjects: [
        { name: "Functions & Modular Code", exam_date: addDays(3), current_marks: 60, difficulty: "neutral" },
        { name: "OOP & Data Structures", exam_date: addDays(5), current_marks: 48, difficulty: "weak" },
        { name: "File Handling & Regex", exam_date: addDays(9), current_marks: 82, difficulty: "strong" }
      ]
    }
  };
}

// Load Initial Data from Server or Defaults
async function loadInitialData() {
  window.cachedPresets = getFallbackPresets();
  try {
    const res = await fetch("/api/presets");
    if (res.ok) {
      const data = await res.json();
      if (data.success && data.presets) {
        window.cachedPresets = data.presets;
      }
    }
  } catch (err) {
    console.warn("Server presets unavailable, using client-side defaults.");
  }
  loadPreset("aiml");
}

// Load a specific preset
function loadPreset(presetKey) {
  if (!window.cachedPresets) {
    window.cachedPresets = getFallbackPresets();
  }
  const p = window.cachedPresets[presetKey] || window.cachedPresets["aiml"];
  if (!p) return;

  appState.availableHours = p.available_hours || 6.0;
  appState.startTime = p.start_time || "09:00";
  appState.sessionLength = p.session_length || 50;
  appState.breakLength = p.break_length || 10;
  appState.subjects = JSON.parse(JSON.stringify(p.subjects));

  // Sync inputs
  const hoursSlider = document.getElementById("availableHours");
  if (hoursSlider) hoursSlider.value = appState.availableHours;
  const hoursDisplay = document.getElementById("hoursValDisplay");
  if (hoursDisplay) hoursDisplay.textContent = `${appState.availableHours.toFixed(1)} hrs`;
  const startTimeInput = document.getElementById("startTime");
  if (startTimeInput) startTimeInput.value = appState.startTime;
  const sessionLengthInput = document.getElementById("sessionLength");
  if (sessionLengthInput) sessionLengthInput.value = appState.sessionLength;

  renderSubjectCards();
  generatePlan();
  showToast(`Loaded ${p.title}`);
}

// Render dynamic Subject cards in left panel
function renderSubjectCards() {
  const container = document.getElementById("subjectsList");
  container.innerHTML = "";
  document.getElementById("subjectCountBadge").textContent = appState.subjects.length;

  appState.subjects.forEach((subj, idx) => {
    const card = document.createElement("div");
    card.className = `subject-card is-${subj.difficulty}`;
    card.id = `subject_card_${idx}`;

    // Days left calculation preview
    const daysLeft = getDaysLeftPreview(subj.exam_date);

    card.innerHTML = `
      <div class="card-top-row">
        <input type="text" class="custom-input subject-name-input" value="${escapeHtml(subj.name)}" placeholder="Subject Name" data-idx="${idx}" data-field="name">
        <button type="button" class="delete-card-btn" title="Remove Subject" data-idx="${idx}">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </div>

      <div class="card-details-row">
        <div>
          <div class="sub-label">
            <span>Exam Date</span>
            <span class="sub-label-val">${daysLeft}</span>
          </div>
          <input type="date" class="custom-input" value="${subj.exam_date}" data-idx="${idx}" data-field="exam_date">
        </div>
        <div>
          <div class="sub-label">
            <span>Current Marks</span>
            <span class="sub-label-val" id="marksVal_${idx}">${subj.current_marks}%</span>
          </div>
          <input type="range" class="custom-range" min="0" max="100" value="${subj.current_marks}" data-idx="${idx}" data-field="current_marks">
        </div>
      </div>

      <div>
        <div class="sub-label">Grasp / Difficulty Level</div>
        <div class="grasp-selector">
          <button type="button" class="grasp-btn ${subj.difficulty === 'weak' ? 'active weak' : ''}" data-idx="${idx}" data-level="weak">Weak / Tough</button>
          <button type="button" class="grasp-btn ${subj.difficulty === 'neutral' ? 'active neutral' : ''}" data-idx="${idx}" data-level="neutral">Neutral</button>
          <button type="button" class="grasp-btn ${subj.difficulty === 'strong' ? 'active strong' : ''}" data-idx="${idx}" data-level="strong">Strong / Mastered</button>
        </div>
      </div>
    `;

    container.appendChild(card);
  });

  // Attach card event listeners
  container.querySelectorAll("input[data-field]").forEach(input => {
    input.addEventListener("input", handleSubjectFieldChange);
  });

  container.querySelectorAll(".delete-card-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const idx = parseInt(btn.dataset.idx);
      deleteSubject(idx);
    });
  });

  container.querySelectorAll(".grasp-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.dataset.idx);
      const level = btn.dataset.level;
      setSubjectDifficulty(idx, level);
    });
  });
}

function handleSubjectFieldChange(e) {
  const idx = parseInt(e.target.dataset.idx);
  const field = e.target.dataset.field;
  let val = e.target.value;

  if (field === "current_marks") {
    val = parseFloat(val);
    const marksDisplay = document.getElementById(`marksVal_${idx}`);
    if (marksDisplay) marksDisplay.textContent = `${val}%`;
  }

  appState.subjects[idx][field] = val;
}

function setSubjectDifficulty(idx, level) {
  appState.subjects[idx].difficulty = level;
  const card = document.getElementById(`subject_card_${idx}`);
  if (card) {
    card.className = `subject-card is-${level}`;
    const buttons = card.querySelectorAll(".grasp-btn");
    buttons.forEach(b => {
      b.className = `grasp-btn ${b.dataset.level === level ? `active ${level}` : ''}`;
    });
  }
}

function addNewSubject() {
  const today = new Date();
  today.setDate(today.getDate() + 7);
  const nextWeekStr = today.toISOString().split("T")[0];

  appState.subjects.push({
    name: `New Subject ${appState.subjects.length + 1}`,
    exam_date: nextWeekStr,
    current_marks: 50,
    difficulty: "neutral"
  });

  renderSubjectCards();
  showToast("Added new subject card. Adjust marks and exam date!");
}

function deleteSubject(idx) {
  if (appState.subjects.length <= 1) {
    showToast("You need at least one subject in your study plan.");
    return;
  }
  const removed = appState.subjects.splice(idx, 1);
  renderSubjectCards();
  showToast(`Removed "${removed[0].name}"`);
}

function getDaysLeftPreview(dateStr) {
  if (!dateStr) return "N/A";
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const target = new Date(dateStr);
  target.setHours(0, 0, 0, 0);
  const diffDays = Math.round((target - now) / (1000 * 60 * 60 * 24));
  if (diffDays <= 0) return "Exam Today / Past";
  if (diffDays === 1) return "Exam Tomorrow!";
  return `in ${diffDays} days`;
}

// Generate Plan via Python Backend API (with automatic client-side fallback)
async function generatePlan() {
  const btn = document.getElementById("generatePlanBtn");
  btn.innerHTML = `<span class="pulse-indicator"></span> Calculating optimal schedule...`;
  btn.disabled = true;

  const payload = {
    subjects: appState.subjects,
    available_hours: appState.availableHours,
    start_time: appState.startTime,
    session_length: appState.sessionLength,
    break_length: appState.breakLength
  };

  try {
    let data = null;
    // Check if running on HTTP server
    if (window.location.protocol.startsWith("http")) {
      try {
        const res = await fetch("/api/generate-plan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          data = await res.json();
        }
      } catch (networkErr) {
        console.warn("Server fetch failed, falling back to local Python-equivalent engine:", networkErr);
      }
    }

    // Client-side Python-equivalent fallback
    if (!data || !data.success) {
      data = generatePlanLocally(payload);
    }

    if (!data || !data.success) {
      showToast(data?.error || "Failed to generate plan");
      return;
    }

    appState.currentPlan = data;
    renderPlanResults(data);
    showToast("Plan generated successfully!");
  } catch (err) {
    console.error("Calculation error:", err);
    showToast("Error computing study recommendations.");
  } finally {
    btn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
      </svg>
      Generate Study Plan
    `;
    btn.disabled = false;
  }
}

// Client-side implementation of planner_engine.py algorithms
function generatePlanLocally(payload) {
  const rawSubjects = payload.subjects || [];
  const availableHours = parseFloat(payload.available_hours || 4.0);
  const startTime = payload.start_time || "09:00";
  const sessionLength = parseInt(payload.session_length || 50);
  const breakLength = parseInt(payload.break_length || 10);

  if (!rawSubjects || rawSubjects.length === 0) {
    return { success: false, error: "No subjects provided." };
  }

  const now = new Date();
  now.setHours(0,0,0,0);

  // 1. Calculate Priority Scores
  const scoredSubjects = rawSubjects.map(s => {
    let daysLeft = 14;
    if (s.exam_date) {
      const examDate = new Date(s.exam_date);
      examDate.setHours(0,0,0,0);
      daysLeft = Math.max(0, Math.round((examDate - now) / (1000 * 60 * 60 * 24)));
    }

    let urgency = 10.0;
    if (daysLeft <= 1) urgency = 100.0;
    else if (daysLeft <= 3) urgency = 90.0;
    else if (daysLeft <= 7) urgency = 75.0;
    else if (daysLeft <= 14) urgency = 55.0;
    else if (daysLeft <= 30) urgency = 35.0;

    const currentMarks = parseFloat(s.current_marks || 50);
    const markGap = Math.max(5.0, 95.0 - currentMarks);

    let mult = 1.0;
    const diff = (s.difficulty || "neutral").toLowerCase();
    if (diff === "weak") mult = 1.55;
    else if (diff === "strong") mult = 0.70;

    const rawPriority = Math.round(((urgency * 0.5) + (markGap * 0.5)) * mult * 100) / 100;

    let priorityLevel = "Maintenance";
    let badgeColor = "success";
    let strategy = "Quick Practice Drills & Flashcard Review";

    if (rawPriority >= 95 || (daysLeft <= 2 && currentMarks < 60)) {
      priorityLevel = "Critical";
      badgeColor = "danger";
      strategy = "Active Recall & High-yield Exam Questions";
    } else if (rawPriority >= 70) {
      priorityLevel = "High";
      badgeColor = "warning";
      strategy = "Core Concepts & Deep Problem Solving";
    } else if (rawPriority >= 45) {
      priorityLevel = "Moderate";
      badgeColor = "primary";
      strategy = "Structured Revision & Note Condensation";
    }

    return {
      name: s.name,
      days_left: daysLeft,
      exam_date: s.exam_date,
      current_marks: currentMarks,
      difficulty: diff,
      raw_priority: rawPriority,
      priority_level: priorityLevel,
      badge_color: badgeColor,
      study_strategy: strategy
    };
  });

  // Sort descending by priority
  scoredSubjects.sort((a, b) => b.raw_priority - a.raw_priority);

  // 2. Allocate Hours
  const totalPriority = scoredSubjects.reduce((acc, s) => acc + s.raw_priority, 0) || 1.0;
  let accumulated = 0;
  const allocated = scoredSubjects.map(s => {
    const rawH = (s.raw_priority / totalPriority) * availableHours;
    let roundedH = Math.round(rawH * 2) / 2;
    if (roundedH < 0.5 && availableHours >= scoredSubjects.length * 0.5) roundedH = 0.5;
    accumulated += roundedH;
    return {
      ...s,
      recommended_hours: roundedH,
      hours_percent: availableHours > 0 ? Math.round((roundedH / availableHours) * 1000) / 10 : 0
    };
  });

  const diff = Math.round((availableHours - accumulated) * 10) / 10;
  if (Math.abs(diff) >= 0.25 && allocated.length > 0) {
    allocated[0].recommended_hours = Math.max(0.5, Math.round((allocated[0].recommended_hours + diff) * 2) / 2);
    allocated[0].hours_percent = Math.round((allocated[0].recommended_hours / availableHours) * 1000) / 10;
  }

  // 3. Timetable Generation
  const [sh, sm] = (startTime.split(":").map(Number));
  let currentMin = (sh || 9) * 60 + (sm || 0);
  const timetable = [];
  let slotCount = 1;

  allocated.forEach((subject, sIdx) => {
    let remaining = Math.round(subject.recommended_hours * 60);
    let part = 1;
    while (remaining > 0) {
      const curSession = Math.min(sessionLength, remaining);
      if (curSession < 25 && timetable.length > 0) {
        timetable[timetable.length - 1].duration_min += curSession;
        break;
      }
      const endMin = currentMin + curSession;
      const startStr = `${String(Math.floor(currentMin / 60)).padStart(2, '0')}:${String(currentMin % 60).padStart(2, '0')}`;
      const endStr = `${String(Math.floor(endMin / 60)).padStart(2, '0')}:${String(endMin % 60).padStart(2, '0')}`;

      let taskFocus = `Mastery Practice Part ${part}: High-yield textbook questions & derivations.`;
      if (subject.difficulty === "weak") taskFocus = `Deep Dive Part ${part}: Core formulas & challenging practice problems.`;
      else if (subject.current_marks < 50) taskFocus = `Foundations Part ${part}: Lecture slide revision & concept flashcards.`;
      else if (subject.days_left <= 3) taskFocus = `Exam Sprint Part ${part}: Timed past-paper drill & error checks.`;

      timetable.push({
        slot_id: `slot_${slotCount}`,
        slot_number: slotCount,
        start_time: startStr,
        end_time: endStr,
        duration_min: curSession,
        subject: subject.name,
        difficulty: subject.difficulty,
        priority_level: subject.priority_level,
        badge_color: subject.badge_color,
        strategy: subject.study_strategy,
        task_focus: taskFocus,
        is_break: false
      });
      slotCount++;
      remaining -= curSession;
      currentMin = endMin;
      part++;

      if (remaining > 0 || sIdx < allocated.length - 1) {
        const bEndMin = currentMin + breakLength;
        timetable.push({
          slot_id: `break_${slotCount}`,
          slot_number: slotCount,
          start_time: `${String(Math.floor(currentMin / 60)).padStart(2, '0')}:${String(currentMin % 60).padStart(2, '0')}`,
          end_time: `${String(Math.floor(bEndMin / 60)).padStart(2, '0')}:${String(bEndMin % 60).padStart(2, '0')}`,
          duration_min: breakLength,
          subject: "Mind Refresh & Rest",
          difficulty: "none",
          priority_level: "Rest",
          badge_color: "secondary",
          strategy: "Hydration, light stretching, or eye rest",
          task_focus: "Take 5 deep breaths, drink water, relax your neck.",
          is_break: true
        });
        slotCount++;
        currentMin = bEndMin;
      }
    }
  });

  const criticalCount = allocated.filter(s => s.priority_level === "Critical").length;
  const weakCount = allocated.filter(s => s.difficulty === "weak").length;
  const avgMarks = Math.round(allocated.reduce((a, b) => a + b.current_marks, 0) / allocated.length * 10) / 10;

  const tips = [];
  if (criticalCount > 0) tips.push("⚠️ You have critical exams approaching with score gaps. Focus your prime morning hours on these topics!");
  if (weakCount > 0) tips.push("🧠 Practice the Feynman Technique: Explain complex concepts from your weak subjects in simple terms out loud.");
  tips.push("⏱️ Use the embedded Pomodoro timer for each study block to maintain peak dopamine and focus.");
  tips.push("📝 Review the day's timetable entries before bed for 10 minutes to trigger memory consolidation during sleep.");

  return {
    success: true,
    summary: {
      total_subjects: allocated.length,
      available_hours: availableHours,
      critical_count: criticalCount,
      weak_count: weakCount,
      average_marks: avgMarks,
      total_sessions: timetable.filter(t => !t.is_break).length,
      total_breaks: timetable.filter(t => t.is_break).length,
      study_tips: tips
    },
    priority_subjects: allocated,
    timetable: timetable
  };
}

// Render generated outputs
function renderPlanResults(plan) {
  const summary = plan.summary;
  const subjects = plan.priority_subjects;
  const timetable = plan.timetable;

  // 1. Metrics Grid
  document.getElementById("metricTotalHours").innerHTML = `${summary.available_hours.toFixed(1)} <span class="metric-unit">hrs/day</span>`;
  document.getElementById("metricSessions").textContent = `${summary.total_sessions} Study Blocks + ${summary.total_breaks} Breaks`;
  document.getElementById("metricCritical").innerHTML = `${summary.critical_count} <span class="metric-unit">high priority</span>`;
  document.getElementById("metricAvgMarks").textContent = `${summary.average_marks}%`;

  // 2. Allocation Visual Multi-segment Bar
  const allocBar = document.getElementById("allocationBar");
  allocBar.innerHTML = "";
  subjects.forEach((s, idx) => {
    const seg = document.createElement("div");
    seg.className = "allocation-segment";
    seg.style.width = `${s.hours_percent}%`;
    const color = PALETTE[idx % PALETTE.length];
    seg.style.backgroundColor = color;
    seg.setAttribute("data-tooltip", `${s.name}: ${s.recommended_hours}h (${s.hours_percent}%)`);
    allocBar.appendChild(seg);
  });

  // 3. Priority Cards
  const cardsGrid = document.getElementById("priorityCardsGrid");
  cardsGrid.innerHTML = "";
  subjects.forEach((s, idx) => {
    const color = PALETTE[idx % PALETTE.length];
    const card = document.createElement("div");
    card.className = "priority-card";
    card.style.borderTop = `3px solid ${color}`;

    card.innerHTML = `
      <div>
        <div class="p-header">
          <span class="p-badge ${s.badge_color}">${s.priority_level} Priority</span>
          <span class="math-badge" title="Algorithmic Priority Score">Score: ${s.raw_priority}</span>
        </div>
        <div class="p-name" title="${escapeHtml(s.name)}">${escapeHtml(s.name)}</div>
      </div>

      <div class="p-stats">
        <span>Exam: ${s.days_left === 0 ? "Today" : `${s.days_left}d left`}</span>
        <span>Current: ${s.current_marks}%</span>
        <span>Diff: ${s.difficulty.toUpperCase()}</span>
      </div>

      <div class="p-hours-box">
        <span style="font-size:0.75rem; color:var(--text-muted);">Recommended Time</span>
        <span class="p-hours-val" style="color:${color}">${s.recommended_hours} hrs</span>
      </div>
    `;
    cardsGrid.appendChild(card);
  });

  // 4. Daily Timetable
  const timetableList = document.getElementById("timetableList");
  timetableList.innerHTML = "";

  loadCompletedSlots();

  timetable.forEach((slot) => {
    const item = document.createElement("div");
    const isCompleted = appState.completedSlots.has(slot.slot_id);
    item.className = `timetable-item ${slot.is_break ? "is-break" : ""} ${isCompleted ? "completed" : ""}`;
    item.id = `item_${slot.slot_id}`;

    if (slot.is_break) {
      item.innerHTML = `
        <div class="t-check-wrap">
          <input type="checkbox" data-slot="${slot.slot_id}" ${isCompleted ? "checked" : ""}>
        </div>
        <div class="t-time-col">
          <span class="t-time-span">${slot.start_time} - ${slot.end_time}</span>
          <span class="t-duration">${slot.duration_min} min rest</span>
        </div>
        <div class="t-content-col">
          <div class="t-subj-row">
            <span class="t-subj-name" style="color:var(--text-dim)">☕ ${slot.subject}</span>
          </div>
          <div class="t-task">${slot.task_focus}</div>
        </div>
      `;
    } else {
      item.innerHTML = `
        <div class="t-check-wrap">
          <input type="checkbox" data-slot="${slot.slot_id}" ${isCompleted ? "checked" : ""}>
        </div>
        <div class="t-time-col">
          <span class="t-time-span">${slot.start_time} - ${slot.end_time}</span>
          <span class="t-duration">${slot.duration_min} min session</span>
        </div>
        <div class="t-content-col">
          <div class="t-subj-row">
            <span class="t-subj-name">${escapeHtml(slot.subject)}</span>
            <span class="p-badge ${slot.badge_color}" style="font-size:0.6rem; padding:0.1rem 0.4rem;">${slot.priority_level}</span>
          </div>
          <div class="t-task">${escapeHtml(slot.task_focus)}</div>
        </div>
        <div class="t-action-col">
          <button type="button" class="t-timer-trigger" data-subject="${escapeHtml(slot.subject)}" data-task="${escapeHtml(slot.task_focus)}" data-duration="${slot.duration_min}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            Focus
          </button>
        </div>
      `;
    }

    timetableList.appendChild(item);
  });

  // Attach completion listeners
  timetableList.querySelectorAll("input[type='checkbox']").forEach(cb => {
    cb.addEventListener("change", (e) => {
      const slotId = e.target.dataset.slot;
      const card = document.getElementById(`item_${slotId}`);
      if (e.target.checked) {
        appState.completedSlots.add(slotId);
        if (card) card.classList.add("completed");
        playTickTone(660); // pleasant confirmation chime
      } else {
        appState.completedSlots.delete(slotId);
        if (card) card.classList.remove("completed");
      }
      saveCompletedSlots();
      renderTimetableProgress();
    });
  });

  // Attach trigger to open timer modal with prefilled subject
  timetableList.querySelectorAll(".t-timer-trigger").forEach(btn => {
    btn.addEventListener("click", () => {
      const subject = btn.dataset.subject;
      const task = btn.dataset.task;
      const duration = parseInt(btn.dataset.duration) || 25;

      timerState.activeSubject = subject;
      timerState.activeTask = task;
      document.getElementById("timerActiveSubject").textContent = subject;
      document.getElementById("timerActiveTask").textContent = task;

      setTimerDuration(duration, "work");
      document.getElementById("timerModal").classList.add("open");
    });
  });

  // 5. Strategy Insights
  const insightsList = document.getElementById("insightsList");
  insightsList.innerHTML = "";
  if (summary.study_tips && summary.study_tips.length > 0) {
    summary.study_tips.forEach(tip => {
      const li = document.createElement("li");
      li.textContent = tip;
      insightsList.appendChild(li);
    });
  }

  renderTimetableProgress();
}

// Progress calculation
function renderTimetableProgress() {
  if (!appState.currentPlan || !appState.currentPlan.timetable) return;
  const studySlots = appState.currentPlan.timetable.filter(s => !s.is_break);
  const total = studySlots.length;
  let done = 0;
  studySlots.forEach(s => {
    if (appState.completedSlots.has(s.slot_id)) done++;
  });

  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  document.getElementById("metricProgress").textContent = `${pct}%`;
  document.getElementById("metricCompletedCount").textContent = `${done} of ${total} study blocks completed`;
}

function saveCompletedSlots() {
  try {
    localStorage.setItem("studyPlannerCompleted", JSON.stringify(Array.from(appState.completedSlots)));
  } catch (e) {}
}

function loadCompletedSlots() {
  try {
    const raw = localStorage.getItem("studyPlannerCompleted");
    if (raw) {
      const arr = JSON.parse(raw);
      appState.completedSlots = new Set(arr);
    }
  } catch (e) {}
}

/* ==========================================================================
   Pomodoro Focus Timer & Web Audio Synthesizer
   ========================================================================== */

function toggleTimer() {
  if (timerState.isRunning) {
    pauseTimer();
  } else {
    startTimer();
  }
}

function startTimer() {
  if (timerState.isRunning) return;
  timerState.isRunning = true;
  document.getElementById("timerToggleBtn").textContent = "Pause Focus";
  document.getElementById("timerToggleBtn").classList.add("btn-secondary");

  timerState.intervalId = setInterval(() => {
    if (timerState.remainingSeconds > 0) {
      timerState.remainingSeconds--;
      updateTimerDisplay();
    } else {
      handleTimerComplete();
    }
  }, 1000);
}

function pauseTimer() {
  timerState.isRunning = false;
  if (timerState.intervalId) clearInterval(timerState.intervalId);
  document.getElementById("timerToggleBtn").textContent = "Resume Focus";
  document.getElementById("timerToggleBtn").classList.remove("btn-secondary");
}

function resetTimer() {
  pauseTimer();
  timerState.remainingSeconds = timerState.totalSeconds;
  document.getElementById("timerToggleBtn").textContent = "Start Focus";
  updateTimerDisplay();
}

function skipTimerInterval() {
  pauseTimer();
  if (timerState.mode === "work") {
    setTimerDuration(5, "break");
    showToast("Transitioned to 5m Rest Interval");
  } else {
    setTimerDuration(25, "work");
    showToast("Transitioned to 25m Focus Block");
  }
}

function setTimerDuration(mins, mode) {
  pauseTimer();
  timerState.mode = mode;
  timerState.totalSeconds = mins * 60;
  timerState.remainingSeconds = mins * 60;
  document.getElementById("timerModeTag").textContent = mode === "work" ? "POMODORO WORK" : "REST BREAK";
  document.getElementById("timerToggleBtn").textContent = "Start Focus";
  updateTimerDisplay();
}

function updateTimerDisplay() {
  const mins = Math.floor(timerState.remainingSeconds / 60);
  const secs = timerState.remainingSeconds % 60;
  const formatted = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

  document.getElementById("timerClock").textContent = formatted;
  document.getElementById("timerPreview").textContent = formatted;
}

function handleTimerComplete() {
  pauseTimer();
  playAlarmChime();
  if (timerState.mode === "work") {
    showToast("🎉 Great focus session! Time for a well-deserved break.");
    setTimerDuration(5, "break");
  } else {
    showToast("🔔 Break time over! Ready for the next study sprint?");
    setTimerDuration(25, "work");
  }
}

// Built-in Synthesizer with Web Audio API (Zero external MP3 dependencies!)
let audioCtx = null;
function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) audioCtx = new AudioContextClass();
  }
  if (audioCtx && audioCtx.state === "suspended") {
    audioCtx.resume();
  }
  return audioCtx;
}

function playTickTone(freq = 520) {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.12);
  } catch (e) {}
}

function playAlarmChime() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6 arpeggio
    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq, ctx.currentTime + idx * 0.15);
      gain.gain.setValueAtTime(0.2, ctx.currentTime + idx * 0.15);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.15 + 0.4);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(ctx.currentTime + idx * 0.15);
      osc.stop(ctx.currentTime + idx * 0.15 + 0.4);
    });
  } catch (e) {}
}

/* Helper Utilities */
function showToast(message) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
    <span>${escapeHtml(message)}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
