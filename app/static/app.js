const state = {
  map: null,
  marker: null,
};

function qs(id) {
  return document.getElementById(id);
}

function setFeedback(message, isError = false) {
  const banner = qs("admin-feedback");
  if (!banner) return;
  banner.textContent = message;
  banner.classList.remove("hidden");
  banner.classList.toggle("error-banner", isError);
  banner.classList.toggle("feedback-banner", !isError);
}

function buildPayload(form) {
  const categories = form.preferred_categories.value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return {
    query: form.query.value.trim(),
    model: form.model.value,
    geo_context: {
      location_name: form.location_name.value.trim(),
      coordinates: {
        lat: form.lat.value ? Number(form.lat.value) : null,
        lng: form.lng.value ? Number(form.lng.value) : null,
      },
      coordinate_system: form.coordinate_system.value,
    },
    user_profile: {
      preferred_categories: categories,
    },
    context_signals: {
      weather: form.weather.value.trim(),
      time_of_day: form.time_of_day.value,
      event: form.event.value.trim(),
    },
  };
}

function ensureMap(lat, lng, locationName) {
  if (lat == null || lng == null || !window.L || !qs("map")) {
    return;
  }

  if (!state.map) {
    state.map = L.map("map", { zoomControl: true }).setView([lat, lng], 12);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(state.map);
  } else {
    state.map.setView([lat, lng], 12);
  }

  if (state.marker) {
    state.marker.remove();
  }

  state.marker = L.marker([lat, lng]).addTo(state.map);
  state.marker.bindPopup(locationName || "GEO 分析位置").openPopup();

  setTimeout(() => state.map.invalidateSize(), 150);
}

function renderRecommendations(items) {
  return (items || [])
    .map(
      (item) => `
        <article class="recommendation-item">
          <h4>${item.title}</h4>
          <p>${item.reason}</p>
          <p>关注类别：${item.focus_category}</p>
        </article>
      `
    )
    .join("");
}

function renderHistoryItems(items) {
  if (!items.length) {
    return "<div class='history-item'><p>还没有历史记录。</p></div>";
  }

  return items
    .map(
      (item) => `
        <article class="history-item">
          <h4>${item.query}</h4>
          <div class="history-meta">
            <span class="chip">模型：${item.model}</span>
            <span class="chip">地点：${item.location_name || "未填写"}</span>
            <span class="chip">时间：${new Date(item.created_at).toLocaleString()}</span>
          </div>
          <p>坐标：${item.latitude ?? "-"}, ${item.longitude ?? "-"}</p>
          <div class="action-row">
            <a class="secondary-button" href="/history/${item.id}">查看详情</a>
            <a class="secondary-button" href="/api/v1/geo/analyses/${item.id}/export?format=json">JSON</a>
            <a class="secondary-button" href="/api/v1/geo/analyses/${item.id}/export?format=xlsx">Excel</a>
            <a class="secondary-button" href="/api/v1/geo/analyses/${item.id}/export?format=pdf">PDF</a>
          </div>
        </article>
      `
    )
    .join("");
}

async function loadHistory() {
  const container = qs("history-list");
  if (!container) {
    return;
  }

  container.innerHTML = "<div class='history-item'><p>正在加载历史记录...</p></div>";
  const response = await fetch("/api/v1/geo/analyses?limit=20");
  const payload = await response.json();
  container.innerHTML = renderHistoryItems(payload.items || []);
}

async function loadProviders() {
  const container = qs("provider-list");
  if (!container) {
    return;
  }

  container.innerHTML = "<div class='provider-card'><p>正在加载供应商状态...</p></div>";
  const response = await fetch("/api/v1/geo/providers");
  const payload = await response.json();
  const items = payload.items || [];
  container.innerHTML = items
    .map(
      (item) => `
        <article class="provider-card">
          <h4>${item.provider}</h4>
          <p>模型名：${item.model_name}</p>
          <ul>
            <li>Mock 模式：${item.use_mock ? "开启" : "关闭"}</li>
            <li>Base URL：${item.base_url || "未设置"}</li>
            <li>API URL：${item.api_url || "未设置"}</li>
            <li>API Key：${item.has_api_key ? "已配置" : "未配置"}</li>
          </ul>
        </article>
      `
    )
    .join("");
}

async function loadUsers() {
  const container = qs("user-list");
  if (!container) return;
  container.innerHTML = "<div class='provider-card'><p>正在加载用户...</p></div>";
  const response = await fetch("/api/v1/admin/users");
  const payload = await response.json();
  const items = payload.items || [];
  container.innerHTML = items
    .map(
      (item) => `
        <article class="provider-card">
          <h4>${item.username}</h4>
          <p>角色：${item.role}</p>
          <p>状态：${item.status}</p>
          <p>创建时间：${new Date(item.created_at).toLocaleString()}</p>
          <div class="action-row">
            <button class="secondary-button" data-user-role="${item.id}" data-role="${item.role === "admin" ? "analyst" : "admin"}">
              切换为${item.role === "admin" ? "analyst" : "admin"}
            </button>
            <button class="secondary-button" data-user-status="${item.id}" data-status="${item.status === "active" ? "disabled" : "active"}">
              ${item.status === "active" ? "禁用" : "启用"}
            </button>
            <button class="secondary-button" data-user-password="${item.id}" data-username="${item.username}">
              重置密码
            </button>
          </div>
        </article>
      `
    )
    .join("");
}

async function loadJobs() {
  const container = qs("job-list");
  if (!container) return;
  container.innerHTML = "<div class='history-item'><p>正在加载任务...</p></div>";
  const response = await fetch("/api/v1/admin/jobs");
  const payload = await response.json();
  const items = payload.items || [];
  container.innerHTML = items.length
    ? items
        .map(
          (item) => `
            <article class="history-item">
              <h4>${item.id}</h4>
              <div class="history-meta">
                <span class="chip">状态：${item.status}</span>
                <span class="chip">重试：${item.retries}/${item.max_retries}</span>
                <span class="chip">创建人：${item.created_by || "system"}</span>
              </div>
              <p>创建时间：${new Date(item.created_at).toLocaleString()}</p>
              <p>更新时间：${new Date(item.updated_at).toLocaleString()}</p>
              <div class="action-row">
                <a class="secondary-button" href="/jobs/${item.id}">查看详情</a>
                ${item.status === "failed" ? `<button class="secondary-button" data-retry-job="${item.id}">重跑任务</button>` : ""}
              </div>
            </article>
          `
        )
        .join("")
    : "<div class='history-item'><p>还没有任务记录。</p></div>";
}

async function loadAudit(filters = {}) {
  const container = qs("audit-list");
  if (!container) return;
  container.innerHTML = "<div class='history-item'><p>正在加载审计日志...</p></div>";
  const query = new URLSearchParams();
  if (filters.actor) query.set("actor", filters.actor);
  if (filters.action) query.set("action", filters.action);
  const response = await fetch(`/api/v1/admin/audit?${query.toString()}`);
  const payload = await response.json();
  const items = payload.items || [];
  container.innerHTML = items.length
    ? items
        .map(
          (item) => `
            <article class="history-item">
              <h4>${item.action}</h4>
              <div class="history-meta">
                <span class="chip">操作者：${item.actor}</span>
                <span class="chip">目标：${item.target_type || "-"} / ${item.target_id || "-"}</span>
              </div>
              <p>时间：${new Date(item.created_at).toLocaleString()}</p>
              <p>详情：${JSON.stringify(item.detail)}</p>
            </article>
          `
        )
        .join("")
    : "<div class='history-item'><p>还没有审计日志。</p></div>";
}

async function createUser(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = {
    username: form.username.value.trim(),
    password: form.password.value.trim(),
    role: form.role.value,
  };
  const response = await fetch("/api/v1/admin/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) {
    setFeedback(result.error || "创建用户失败", true);
    return;
  }
  form.reset();
  setFeedback(`已创建用户 ${result.username}`);
  await loadUsers();
}

async function handleUserAction(button) {
  const userId = button.dataset.userRole || button.dataset.userStatus || button.dataset.userPassword;
  const payload = {};
  if (button.dataset.userRole) payload.role = button.dataset.role;
  if (button.dataset.userStatus) payload.status = button.dataset.status;
  if (button.dataset.userPassword) {
    const nextPassword = window.prompt(`为用户 ${button.dataset.username} 输入新密码`);
    if (!nextPassword) return;
    payload.password = nextPassword.trim();
    if (!payload.password) return;
  }
  const response = await fetch(`/api/v1/admin/users/${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) {
    setFeedback(result.error || "更新用户失败", true);
    return;
  }
  setFeedback(`已更新用户 ${result.username}`);
  await loadUsers();
}

async function retryJob(jobId) {
  const response = await fetch(`/api/v1/admin/jobs/${jobId}/retry`, {
    method: "POST",
  });
  const result = await response.json();
  if (!response.ok) {
    window.alert(result.error || "重跑任务失败");
    return;
  }
  setFeedback(`任务 ${jobId} 已重新排队`);
  await Promise.all([loadJobs(), loadAudit()]);
  if (qs("job-status-badge")) {
    qs("job-status-badge").textContent = `任务状态：${result.status}`;
    qs("job-status-badge").classList.remove("hidden");
  }
}

function renderResult(result) {
  qs("result-empty")?.classList.add("hidden");
  qs("result-content")?.classList.remove("hidden");

  if (qs("result-model")) qs("result-model").textContent = `模型：${result.model}`;
  if (qs("result-confidence")) qs("result-confidence").textContent = `置信度：${result.confidence}`;
  if (qs("result-record-id")) qs("result-record-id").textContent = `记录 ID：${result.record_id}`;
  if (qs("analysis-text")) qs("analysis-text").textContent = result.analysis;
  if (qs("tag-list")) {
    qs("tag-list").innerHTML = (result.enriched_tags || [])
      .map((tag) => `<span class="chip">${tag}</span>`)
      .join("");
  }
  if (qs("recommendation-list")) {
    qs("recommendation-list").innerHTML = renderRecommendations(result.recommendations || []);
  }

  const mapCenter = result.visualization?.map_center || {};
  ensureMap(mapCenter.lat, mapCenter.lng, result.normalized_geo_context?.location_name || "");
}

async function submitForm(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = buildPayload(form);
  const statusBadge = qs("job-status-badge");
  if (statusBadge) {
    statusBadge.textContent = "任务已排队";
    statusBadge.classList.remove("hidden");
  }

  const response = await fetch("/api/v1/geo/analyze/async", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) {
    window.alert(result.error || "请求失败");
    return;
  }

  await pollJob(result.job_id);
}

async function pollJob(jobId) {
  const statusBadge = qs("job-status-badge");
  let attempts = 0;
  while (attempts < 60) {
    attempts += 1;
    const response = await fetch(`/api/v1/geo/jobs/${jobId}`);
    const job = await response.json();
    if (!response.ok) {
      window.alert(job.error || "任务查询失败");
      return;
    }
    if (statusBadge) {
      statusBadge.textContent = `任务状态：${job.status}`;
    }
    if (job.status === "completed") {
      renderResult(job.result);
      await loadHistory();
      return;
    }
    if (job.status === "failed") {
      window.alert(job.error?.message || "任务执行失败");
      return;
    }
    await new Promise((resolve) => window.setTimeout(resolve, 1000));
  }
  window.alert("任务仍在执行中，请稍后刷新查看。");
}

function initDashboard() {
  const form = qs("geo-form");
  if (form) {
    form.addEventListener("submit", submitForm);
  }

  const userForm = qs("user-form");
  if (userForm) {
    userForm.addEventListener("submit", createUser);
  }

  const auditForm = qs("audit-filter-form");
  if (auditForm) {
    auditForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      await loadAudit({
        actor: auditForm.actor.value.trim(),
        action: auditForm.action.value.trim(),
      });
    });
  }

  document.addEventListener("click", async (event) => {
    const target = event.target.closest("[data-user-role], [data-user-status], [data-user-password], [data-retry-job]");
    if (!target) return;
    if (target.dataset.retryJob) {
      await retryJob(target.dataset.retryJob);
      return;
    }
    await handleUserAction(target);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  initDashboard();
  await Promise.all([loadHistory(), loadProviders(), loadUsers(), loadJobs(), loadAudit()]);
});
