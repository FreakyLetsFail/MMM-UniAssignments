Module.register("MMM-UniAssignments", {
  defaults: {
    backendUrl: "http://localhost:5000",
    updateInterval: 5 * 60 * 1000, // 5 Minuten
    animationSpeed: 500,
    maxAssignments: 10,
    showProgress: true,
    dateFormat: "DD.MM.YYYY"
  },

  currentView: "hidden", // hidden, week, module
  assignments: [],
  modules: [],
  selectedModuleId: null,
  updateTimer: null,

  start() {
    Log.info(`Starting module: ${this.name}`);
    this.loadAssignments();
    this.scheduleUpdate();
  },

  getDom() {
    const wrapper = document.createElement("div");
    wrapper.className = "uni-assignments-wrapper";

    if (this.currentView === "hidden") {
      wrapper.style.display = "none";
      return wrapper;
    }

    if (this.currentView === "week") {
      wrapper.appendChild(this.createWeekView());
    } else if (this.currentView === "module") {
      wrapper.appendChild(this.createModuleView());
    }

    return wrapper;
  },

  createWeekView() {
    const container = document.createElement("div");
    container.className = "week-view";

    const header = document.createElement("div");
    header.className = "view-header";
    header.innerHTML = `
      <h2>📚 Abgaben diese Woche</h2>
      <span class="week-subtitle">${this.assignments.length} Aufgaben</span>
    `;
    container.appendChild(header);

    const list = document.createElement("div");
    list.className = "assignments-list";

    if (this.assignments.length === 0) {
      list.innerHTML = '<div class="empty-state">🎉 Keine Abgaben diese Woche!</div>';
    } else {
      this.assignments.slice(0, this.config.maxAssignments).forEach(assignment => {
        list.appendChild(this.createAssignmentItem(assignment));
      });
    }

    container.appendChild(list);
    return container;
  },

  createModuleView() {
    const container = document.createElement("div");
    container.className = "module-view";

    const header = document.createElement("div");
    header.className = "view-header";
    header.innerHTML = '<h2>📊 Module Übersicht</h2>';
    container.appendChild(header);

    const grid = document.createElement("div");
    grid.className = "modules-grid";

    this.modules.forEach(module => {
      grid.appendChild(this.createModuleCard(module));
    });

    container.appendChild(grid);
    return container;
  },

  createAssignmentItem(assignment) {
    const item = document.createElement("div");
    item.className = "assignment-item";

    const daysUntil = this.getDaysUntilDue(assignment.due_date);
    const urgencyClass = daysUntil <= 2 ? "urgent" : daysUntil <= 5 ? "warning" : "normal";

    item.innerHTML = `
      <div class="assignment-header">
        <span class="module-badge" style="background: ${this.getModuleColor(assignment.module_id)}">${assignment.module_name}</span>
        <span class="due-date ${urgencyClass}">${this.formatDaysUntil(daysUntil)}</span>
      </div>
      <div class="assignment-title">${assignment.title}</div>
      <div class="assignment-meta">
        <span>📅 ${this.formatDate(assignment.due_date)}</span>
        ${assignment.description ? `<span>📝 ${assignment.description}</span>` : ''}
      </div>
    `;

    return item;
  },

  createModuleCard(module) {
    const card = document.createElement("div");
    card.className = "module-card";

    const progress = module.completed / module.total * 100;
    const progressClass = progress === 100 ? "complete" : progress >= 50 ? "good" : "needs-work";

    card.innerHTML = `
      <div class="module-card-header" style="background: ${this.getModuleColor(module.id)}">
        <h3>${module.name}</h3>
      </div>
      <div class="module-card-body">
        <div class="progress-section">
          <div class="progress-bar ${progressClass}">
            <div class="progress-fill" style="width: ${progress}%"></div>
          </div>
          <div class="progress-text">${module.completed}/${module.total} erledigt</div>
        </div>
        <div class="upcoming-count">
          ${module.upcoming} anstehend
        </div>
      </div>
    `;

    return card;
  },

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric"
    });
  },

  getDaysUntilDue(dueDate) {
    const now = new Date();
    const due = new Date(dueDate);
    const diffTime = due - now;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  },

  formatDaysUntil(days) {
    if (days === 0) return "Heute!";
    if (days === 1) return "Morgen";
    if (days < 0) return "Überfällig";
    return `in ${days} Tagen`;
  },

  getModuleColor(moduleId) {
    const colors = [
      "#667eea", "#764ba2", "#f093fb", "#4facfe",
      "#43e97b", "#fa709a", "#30cfd0", "#a8edea"
    ];
    const hash = moduleId?.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) || 0;
    return colors[hash % colors.length];
  },

  getStyles() {
    return ["MMM-UniAssignments.css"];
  },

  async loadAssignments() {
    try {
      const endpoint = this.currentView === "week" ? "/api/assignments/week" : "/api/assignments";
      const response = await fetch(`${this.config.backendUrl}${endpoint}`);
      const data = await response.json();

      if (data.success) {
        this.assignments = data.assignments || [];
        this.modules = data.modules || [];
        this.updateDom(this.config.animationSpeed);
      }
    } catch (error) {
      Log.error(`${this.name}: Error loading assignments:`, error);
    }
  },

  scheduleUpdate() {
    this.updateTimer = setInterval(() => {
      if (this.currentView !== "hidden") {
        this.loadAssignments();
      }
    }, this.config.updateInterval);
  },

  notificationReceived(notification, payload) {
    switch (notification) {
      case "UNI_SHOW_WEEK":
        this.currentView = "week";
        this.loadAssignments();
        this.updateDom(this.config.animationSpeed);
        break;

      case "UNI_SHOW_MODULE":
        this.currentView = "module";
        this.selectedModuleId = payload?.params?.id || null;
        this.loadAssignments();
        this.updateDom(this.config.animationSpeed);
        break;

      case "HIDE_ALL_MODULES":
      case "HIDE_MODULES":
        this.currentView = "hidden";
        this.updateDom(this.config.animationSpeed);
        break;
    }
  },

  suspend() {
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
    }
  },

  resume() {
    this.scheduleUpdate();
  }
});
