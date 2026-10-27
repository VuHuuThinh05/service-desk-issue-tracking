const API_BASE = "/api/v1";
const TOKEN_KEY = "service_desk_access_token";

const $ = (id) => document.getElementById(id);

let currentUser = null;
let currentPage = "overview";
let currentStatusFilter = "";
let ticketCache = [];

function escapeHtml(value = "") {
    return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    })[char]);
}

function formatDate(value) {
    if (!value) return "Chưa có";
    const date = new Date(value);
    return Number.isNaN(date.getTime())
        ? "Chưa có"
        : date.toLocaleString("vi-VN");
}

function statusLabel(status) {
    return ({
        OPEN: "Mới tiếp nhận",
        IN_PROGRESS: "Đang xử lý",
        RESOLVED: "Đã giải quyết",
        CLOSED: "Đã đóng",
    })[status] || status || "Không rõ";
}

function priorityLabel(priority) {
    return ({
        LOW: "Thấp",
        MEDIUM: "Trung bình",
        HIGH: "Cao",
        URGENT: "Khẩn cấp",
    })[priority] || priority || "Không rõ";
}

function roleLabel(role) {
    return ({
        EMPLOYEE: "Nhân viên",
        SUPPORT_AGENT: "Nhân viên hỗ trợ",
        ADMIN: "Quản trị viên",
    })[role] || role || "";
}

function displayError(id, message = "") {
    const element = $(id);
    if (element) element.textContent = message;
}

async function apiRequest(path, options = {}) {
    const token = localStorage.getItem(TOKEN_KEY);
    const headers = {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
    };

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        clearSession();
        throw new Error("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.");
    }

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
        const detail = result.detail;
        throw new Error(
            typeof detail === "string" ? detail : "Yêu cầu thất bại."
        );
    }

    return result;
}

function showLogin() {
    $("login-page").hidden = false;
    $("dashboard-page").hidden = true;
}

function showDashboard() {
    $("login-page").hidden = true;
    $("dashboard-page").hidden = false;
}

function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    currentUser = null;
    showLogin();
}

function renderUser(user) {
    currentUser = user;
    const name = user.full_name || user.email || "Tài khoản";
    if ($("header-name")) $("header-name").textContent = name;

    if ($("users-nav")) {
        $("users-nav").hidden = user.role !== "ADMIN";
    }

    if ($("scope-description")) {
        $("scope-description").textContent = ({
            ADMIN: "Bạn đang xem toàn bộ dữ liệu yêu cầu hỗ trợ.",
            EMPLOYEE: "Bạn đang xem các yêu cầu hỗ trợ do mình tạo.",
            SUPPORT_AGENT: "Bạn đang xem các yêu cầu được phân công cho mình.",
        })[user.role] || "Dữ liệu được giới hạn theo quyền tài khoản.";
    }
}

function setPage(title, eyebrow = "WORKSPACE") {
    currentPage = title;
    const heading = document.querySelector(".main-content .topbar h1");
    const label = document.querySelector(".main-content .topbar .eyebrow");

    if (heading) heading.textContent = title;
    if (label) label.textContent = eyebrow;

    document.querySelectorAll(".sidebar .nav-item").forEach((button) => {
        button.classList.toggle(
            "active",
            (title === "Tổng quan" && button.id === "overview-nav") ||
            (title === "Yêu cầu hỗ trợ" && button.id === "tickets-nav") ||
            (title === "Người dùng" && button.id === "users-nav")
        );
    });
}

async function openDashboard(user) {
    renderUser(user);
    showDashboard();
    setPage("Tổng quan", "WORKSPACE / OVERVIEW");
    await loadDashboard();
}

async function loadDashboard() {
    displayError("dashboard-error");

    try {
        const summary = await apiRequest("/dashboard/summary");
        const values = {
            "total-tickets": summary.total_tickets,
            "open-tickets": summary.open_tickets,
            "progress-tickets": summary.in_progress_tickets,
            "resolved-tickets": summary.resolved_tickets,
            "closed-tickets": summary.closed_tickets,
            "high-tickets": summary.high_priority_tickets,
        };

        for (const [id, value] of Object.entries(values)) {
            if ($(id)) $(id).textContent = value ?? 0;
        }
    } catch (error) {
        displayError("dashboard-error", error.message);
    }
}

function ensureWorkspace() {
    let workspace = $("workspace-content");

    if (!workspace) {
        workspace = document.createElement("section");
        workspace.id = "workspace-content";
        workspace.className = "info-panel";
        const main = document.querySelector(".main-content");
        const footer = main?.querySelector(".page-footer");
        if (main) main.insertBefore(workspace, footer || null);
    }

    return workspace;
}

function showWorkspace(html) {
    const workspace = ensureWorkspace();
    workspace.innerHTML = html;
    workspace.hidden = false;
}

function hideOverviewSections() {
    const stats = document.querySelector(".stats-grid, .stat-grid, .stats-section");
    const info = document.querySelector(".main-content .info-panel");

    if (stats && stats.id !== "workspace-content") stats.hidden = true;
    if (info && info.id !== "workspace-content") info.hidden = true;

    const workspace = $("workspace-content");
    if (workspace) workspace.hidden = false;
}

function showOverviewSections() {
    const stats = document.querySelector(".stats-grid, .stat-grid, .stats-section");
    const info = document.querySelector(".main-content .info-panel");

    if (stats) stats.hidden = false;
    if (info && info.id !== "workspace-content") info.hidden = false;

    const workspace = $("workspace-content");
    if (workspace) workspace.hidden = true;
}

function ticketRow(ticket) {
    return `
        <tr>
            <td>
                <button class="text-button" data-ticket-id="${escapeHtml(ticket.id)}">
                    ${escapeHtml(ticket.ticket_number)}
                </button>
            </td>
            <td>
                <button class="text-button ticket-title" data-ticket-id="${escapeHtml(ticket.id)}">
                    ${escapeHtml(ticket.title)}
                </button>
                <div class="muted">${escapeHtml(ticket.category)}</div>
            </td>
            <td><span class="status-pill">${escapeHtml(statusLabel(ticket.status))}</span></td>
            <td>${escapeHtml(priorityLabel(ticket.priority))}</td>
            <td>${escapeHtml(formatDate(ticket.created_at))}</td>
        </tr>`;
}

async function openTickets(status = "") {
    currentStatusFilter = status;
    setPage("Yêu cầu hỗ trợ", "WORKSPACE / TICKETS");
    hideOverviewSections();

    showWorkspace(`
        <div class="workspace-heading">
            <div>
                <h2>Danh sách yêu cầu</h2>
                <p class="muted">Dữ liệu thực tế từ hệ thống.</p>
            </div>
            <button id="create-ticket-button" class="primary-button" type="button">
                + Tạo yêu cầu
            </button>
        </div>

        <div class="ticket-filters">
            <input id="ticket-search" type="search" placeholder="Tìm mã hoặc tiêu đề ticket...">
            <select id="ticket-status-filter">
                <option value="">Tất cả trạng thái</option>
                <option value="OPEN">Mới tiếp nhận</option>
                <option value="IN_PROGRESS">Đang xử lý</option>
                <option value="RESOLVED">Đã giải quyết</option>
                <option value="CLOSED">Đã đóng</option>
            </select>
            <button id="reload-tickets" type="button" class="secondary-button">Làm mới</button>
        </div>

        <p id="ticket-list-error" class="error-message" role="alert"></p>
        <div class="table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Mã ticket</th>
                        <th>Tiêu đề</th>
                        <th>Trạng thái</th>
                        <th>Ưu tiên</th>
                        <th>Ngày tạo</th>
                    </tr>
                </thead>
                <tbody id="ticket-table-body">
                    <tr><td colspan="5">Đang tải dữ liệu...</td></tr>
                </tbody>
            </table>
        </div>
        <p id="ticket-count" class="muted"></p>
    `);

    $("ticket-status-filter").value = status;

    $("ticket-status-filter").addEventListener("change", (event) => {
        openTickets(event.target.value);
    });

    $("ticket-search").addEventListener("input", filterTicketRows);
    $("reload-tickets").addEventListener("click", () => loadTickets());
    $("create-ticket-button").addEventListener("click", showCreateTicketForm);

    await loadTickets();
}

async function loadTickets() {
    const body = $("ticket-table-body");
    if (!body) return;

    body.innerHTML = `<tr><td colspan="5">Đang tải dữ liệu...</td></tr>`;
    displayError("ticket-list-error");

    try {
        const query = new URLSearchParams({ limit: "100", offset: "0" });
        if (currentStatusFilter) query.set("status", currentStatusFilter);

        ticketCache = await apiRequest(`/tickets?${query.toString()}`);

        body.innerHTML = ticketCache.length
            ? ticketCache.map(ticketRow).join("")
            : `<tr><td colspan="5">Không có ticket phù hợp.</td></tr>`;

        $("ticket-count").textContent = `Hiển thị ${ticketCache.length} yêu cầu`;
        filterTicketRows();
    } catch (error) {
        body.innerHTML = "";
        displayError("ticket-list-error", error.message);
    }
}

function filterTicketRows() {
    const search = ($("ticket-search")?.value || "").trim().toLowerCase();
    const filtered = ticketCache.filter((ticket) =>
        `${ticket.ticket_number} ${ticket.title} ${ticket.category}`
            .toLowerCase()
            .includes(search)
    );

    const body = $("ticket-table-body");
    if (!body) return;

    body.innerHTML = filtered.length
        ? filtered.map(ticketRow).join("")
        : `<tr><td colspan="5">Không tìm thấy ticket phù hợp.</td></tr>`;

    $("ticket-count").textContent = `Hiển thị ${filtered.length}/${ticketCache.length} yêu cầu`;
}

async function openTicketDetail(ticketId) {
    setPage("Chi tiết yêu cầu", "WORKSPACE / TICKET DETAIL");
    hideOverviewSections();

    showWorkspace(`<p>Đang tải chi tiết ticket...</p>`);

    try {
        const [ticket, comments, events] = await Promise.all([
            apiRequest(`/tickets/${ticketId}`),
            apiRequest(`/tickets/${ticketId}/comments`),
            apiRequest(`/tickets/${ticketId}/events`),
        ]);

        const isAdmin = currentUser?.role === "ADMIN";
        const canComment = ticket.status !== "CLOSED";
        const canTransition = ["ADMIN", "SUPPORT_AGENT"].includes(currentUser?.role);

        showWorkspace(`
            <div class="workspace-heading">
                <div>
                    <button id="back-to-tickets" class="text-button" type="button">← Quay lại danh sách</button>
                    <h2>${escapeHtml(ticket.ticket_number)} — ${escapeHtml(ticket.title)}</h2>
                    <p class="muted">Tạo lúc ${escapeHtml(formatDate(ticket.created_at))}</p>
                </div>
                <span class="status-pill">${escapeHtml(statusLabel(ticket.status))}</span>
            </div>

            <div class="detail-grid">
                <section class="detail-card">
                    <h3>Thông tin yêu cầu</h3>
                    <p><strong>Danh mục:</strong> ${escapeHtml(ticket.category)}</p>
                    <p><strong>Mức ưu tiên:</strong> ${escapeHtml(priorityLabel(ticket.priority))}</p>
                    <p><strong>Trạng thái:</strong> ${escapeHtml(statusLabel(ticket.status))}</p>
                    <p><strong>Người yêu cầu (ID):</strong> ${escapeHtml(ticket.requester_id)}</p>
                    <p><strong>Người phụ trách (ID):</strong> ${escapeHtml(ticket.assignee_id || "Chưa phân công")}</p>
                    <p><strong>Ngày cập nhật:</strong> ${escapeHtml(formatDate(ticket.updated_at))}</p>
                    <p><strong>Ngày giải quyết:</strong> ${escapeHtml(formatDate(ticket.resolved_at))}</p>
                    <p><strong>Ngày đóng:</strong> ${escapeHtml(formatDate(ticket.closed_at))}</p>
                </section>
                <section class="detail-card">
                    <h3>Mô tả</h3>
                    <p class="preserve-lines">${escapeHtml(ticket.description)}</p>
                </section>
            </div>

            ${isAdmin ? `
                <section class="detail-card">
                    <h3>Phân công xử lý</h3>
                    <form id="assign-ticket-form">
                        <label for="assignee-id">ID tài khoản nhân viên hỗ trợ</label>
                        <input id="assignee-id" type="text" required placeholder="Nhập UUID của SUPPORT_AGENT">
                        <button class="primary-button" type="submit">Phân công</button>
                    </form>
                    <p id="assign-error" class="error-message" role="alert"></p>
                </section>
            ` : ""}

            ${canTransition ? `
                <section class="detail-card">
                    <h3>Cập nhật trạng thái</h3>
                    <form id="transition-ticket-form">
                        <label for="next-status">Trạng thái mới</label>
                        <select id="next-status">
                            ${nextStatuses(ticket.status).map((status) =>
                                `<option value="${status}">${escapeHtml(statusLabel(status))}</option>`
                            ).join("")}
                        </select>
                        <button class="primary-button" type="submit" ${nextStatuses(ticket.status).length ? "" : "disabled"}>
                            Cập nhật
                        </button>
                    </form>
                    <p id="transition-error" class="error-message" role="alert"></p>
                </section>
            ` : ""}

            <section class="detail-card">
                <h3>Bình luận (${comments.length})</h3>
                <div class="comment-list">
                    ${comments.length ? comments.map((comment) => `
                        <article class="comment-item">
                            <p>${escapeHtml(comment.body)}</p>
                            <small>Người viết ID: ${escapeHtml(comment.author_id)} · ${escapeHtml(formatDate(comment.created_at))}</small>
                        </article>
                    `).join("") : `<p class="muted">Chưa có bình luận.</p>`}
                </div>
                ${canComment ? `
                    <form id="comment-form">
                        <label for="comment-body">Thêm bình luận</label>
                        <textarea id="comment-body" rows="3" minlength="1" maxlength="5000" required></textarea>
                        <button class="primary-button" type="submit">Gửi bình luận</button>
                    </form>
                    <p id="comment-error" class="error-message" role="alert"></p>
                ` : `<p class="muted">Ticket đã đóng, không thể thêm bình luận.</p>`}
            </section>

            <section class="detail-card">
                <h3>Lịch sử hoạt động (${events.length})</h3>
                <div class="event-list">
                    ${events.length ? events.map((event) => `
                        <article class="event-item">
                            <strong>${escapeHtml(event.event_type)}</strong>
                            <p>Người thực hiện ID: ${escapeHtml(event.actor_id)}</p>
                            <small>${escapeHtml(formatDate(event.created_at))}</small>
                            ${event.old_value ? `<pre>${escapeHtml(JSON.stringify(event.old_value, null, 2))}</pre>` : ""}
                            ${event.new_value ? `<pre>${escapeHtml(JSON.stringify(event.new_value, null, 2))}</pre>` : ""}
                        </article>
                    `).join("") : `<p class="muted">Chưa có lịch sử.</p>`}
                </div>
            </section>
        `);

        $("back-to-tickets").addEventListener("click", () => openTickets(currentStatusFilter));

        if (canComment) {
            $("comment-form").addEventListener("submit", async (event) => {
                event.preventDefault();
                const button = event.currentTarget.querySelector("button");
                button.disabled = true;

                try {
                    await apiRequest(`/tickets/${ticketId}/comments`, {
                        method: "POST",
                        body: JSON.stringify({ body: $("comment-body").value.trim() }),
                    });
                    await openTicketDetail(ticketId);
                } catch (error) {
                    displayError("comment-error", error.message);
                    button.disabled = false;
                }
            });
        }

        if (isAdmin) {
            $("assign-ticket-form").addEventListener("submit", async (event) => {
                event.preventDefault();
                const button = event.currentTarget.querySelector("button");
                button.disabled = true;

                try {
                    await apiRequest(`/tickets/${ticketId}/assign`, {
                        method: "POST",
                        body: JSON.stringify({ assignee_id: $("assignee-id").value.trim() }),
                    });
                    await openTicketDetail(ticketId);
                } catch (error) {
                    displayError("assign-error", error.message);
                    button.disabled = false;
                }
            });
        }

        if (canTransition && nextStatuses(ticket.status).length) {
            $("transition-ticket-form").addEventListener("submit", async (event) => {
                event.preventDefault();
                const button = event.currentTarget.querySelector("button");
                button.disabled = true;

                try {
                    await apiRequest(`/tickets/${ticketId}/transitions`, {
                        method: "POST",
                        body: JSON.stringify({ status: $("next-status").value }),
                    });
                    await openTicketDetail(ticketId);
                } catch (error) {
                    displayError("transition-error", error.message);
                    button.disabled = false;
                }
            });
        }
    } catch (error) {
        showWorkspace(`
            <p class="error-message">${escapeHtml(error.message)}</p>
            <button id="detail-back-button" class="secondary-button" type="button">Quay lại danh sách</button>
        `);
        $("detail-back-button").addEventListener("click", () => openTickets(currentStatusFilter));
    }
}

function nextStatuses(status) {
    return ({
        OPEN: ["IN_PROGRESS"],
        IN_PROGRESS: ["RESOLVED"],
        RESOLVED: ["IN_PROGRESS", "CLOSED"],
        CLOSED: [],
    })[status] || [];
}

function showCreateTicketForm() {
    if (!["EMPLOYEE", "ADMIN"].includes(currentUser?.role)) {
        showWorkspace(`
            <p>Tài khoản nhân viên hỗ trợ không có quyền tạo ticket theo quy tắc backend hiện tại.</p>
            <button id="create-back-button" class="secondary-button" type="button">Quay lại</button>
        `);
        $("create-back-button").addEventListener("click", () => openTickets(currentStatusFilter));
        return;
    }

    showWorkspace(`
        <div class="workspace-heading">
            <div>
                <button id="create-back-button" class="text-button" type="button">← Quay lại danh sách</button>
                <h2>Tạo yêu cầu hỗ trợ</h2>
            </div>
        </div>
        <form id="create-ticket-form" class="ticket-form">
            <label for="new-ticket-title">Tiêu đề</label>
            <input id="new-ticket-title" minlength="5" maxlength="200" required>
            <label for="new-ticket-description">Mô tả chi tiết</label>
            <textarea id="new-ticket-description" minlength="10" maxlength="10000" rows="5" required></textarea>
            <label for="new-ticket-category">Danh mục</label>
            <input id="new-ticket-category" minlength="2" maxlength="50" required placeholder="Ví dụ: Phần cứng, Phần mềm, Mạng">
            <label for="new-ticket-priority">Mức ưu tiên</label>
            <select id="new-ticket-priority">
                <option value="LOW">Thấp</option>
                <option value="MEDIUM" selected>Trung bình</option>
                <option value="HIGH">Cao</option>
                <option value="URGENT">Khẩn cấp</option>
            </select>
            <p id="create-ticket-error" class="error-message" role="alert"></p>
            <button class="primary-button" type="submit">Tạo yêu cầu</button>
        </form>
    `);

    $("create-back-button").addEventListener("click", () => openTickets(currentStatusFilter));

    $("create-ticket-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = event.currentTarget.querySelector("button");
        button.disabled = true;

        try {
            const ticket = await apiRequest("/tickets", {
                method: "POST",
                body: JSON.stringify({
                    title: $("new-ticket-title").value.trim(),
                    description: $("new-ticket-description").value.trim(),
                    category: $("new-ticket-category").value.trim(),
                    priority: $("new-ticket-priority").value,
                }),
            });
            await openTicketDetail(ticket.id);
            await loadDashboard();
        } catch (error) {
            displayError("create-ticket-error", error.message);
            button.disabled = false;
        }
    });
}


async function openUsers() {
    if (currentUser?.role !== "ADMIN") return;

    setPage("Người dùng", "WORKSPACE / USERS");
    hideOverviewSections();
    showWorkspace(`<p>Đang tải danh sách người dùng...</p>`);

    try {
        const users = await apiRequest("/users");

        showWorkspace(`
            <div class="workspace-heading">
                <div>
                    <h2>Quản lý người dùng</h2>
                    <p class="muted">Danh sách tài khoản trong hệ thống.</p>
                </div>
                <button id="add-user-button" class="primary-button" type="button">
                    + Thêm người dùng
                </button>
            </div>

            <p id="users-error" class="error-message" role="alert"></p>

            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Họ tên</th>
                            <th>Email</th>
                            <th>Vai trò</th>
                            <th>Trạng thái</th>
                            <th>Thao tác</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${users.map((user) => `
                            <tr>
                                <td>${escapeHtml(user.id)}</td>
                                <td>${escapeHtml(user.full_name)}</td>
                                <td>${escapeHtml(user.email)}</td>
                                <td>${escapeHtml(roleLabel(user.role))}</td>
                                <td>${user.is_active ? "Đang hoạt động" : "Đã vô hiệu hóa"}</td>
                                <td>
                                    ${user.id !== currentUser.id ? `
                                        <button
                                            class="secondary-button"
                                            data-user-id="${escapeHtml(user.id)}"
                                            data-active="${user.is_active}"
                                        >
                                            ${user.is_active ? "Vô hiệu hóa" : "Kích hoạt"}
                                        </button>
                                    ` : "Tài khoản của bạn"}
                                </td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `);

        $("add-user-button").addEventListener("click", showCreateUserForm);

        document.querySelectorAll("[data-user-id]").forEach((button) => {
            button.addEventListener("click", async () => {
                button.disabled = true;

                try {
                    await apiRequest(`/users/${button.dataset.userId}/status`, {
                        method: "PATCH",
                        body: JSON.stringify({
                            is_active: button.dataset.active !== "true",
                        }),
                    });

                    await openUsers();
                } catch (error) {
                    displayError("users-error", error.message);
                    button.disabled = false;
                }
            });
        });
    } catch (error) {
        showWorkspace(`
            <p class="error-message">${escapeHtml(error.message)}</p>
            <button id="retry-users-button" class="secondary-button" type="button">
                Thử lại
            </button>
        `);

        $("retry-users-button").addEventListener("click", openUsers);
    }
}

function showCreateUserForm() {
    showWorkspace(`
        <div class="workspace-heading">
            <div>
                <button id="create-user-back" class="text-button" type="button">
                    ← Quay lại danh sách
                </button>
                <h2>Thêm người dùng</h2>
                <p class="muted">ID sẽ được hệ thống tự động tạo.</p>
            </div>
        </div>

        <form id="create-user-form" class="ticket-form">
            <label for="new-user-name">Họ và tên</label>
            <input
                id="new-user-name"
                type="text"
                maxlength="120"
                required
            >

            <label for="new-user-email">Email</label>
            <input
                id="new-user-email"
                type="email"
                maxlength="255"
                required
            >

            <label for="new-user-password">Mật khẩu</label>
            <input
                id="new-user-password"
                type="password"
                minlength="8"
                required
                autocomplete="new-password"
            >

            <label for="new-user-role">Vai trò</label>
            <select id="new-user-role" required>
                <option value="EMPLOYEE">Nhân viên</option>
                <option value="SUPPORT_AGENT">Nhân viên hỗ trợ</option>
                <option value="ADMIN">Quản trị viên</option>
            </select>

            <p id="create-user-error" class="error-message" role="alert"></p>

            <button class="primary-button" type="submit">
                Tạo người dùng
            </button>
        </form>
    `);

    $("create-user-back").addEventListener("click", openUsers);

    $("create-user-form").addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = event.currentTarget.querySelector(
            'button[type="submit"]'
        );
        button.disabled = true;
        displayError("create-user-error");

        try {
            await apiRequest("/users", {
                method: "POST",
                body: JSON.stringify({
                    full_name: $("new-user-name").value.trim(),
                    email: $("new-user-email").value.trim(),
                    password: $("new-user-password").value,
                    role: $("new-user-role").value,
                }),
            });

            await openUsers();
        } catch (error) {
            displayError("create-user-error", error.message);
            button.disabled = false;
        }
    });
}


$("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const button = $("login-button");
    button.disabled = true;
    button.textContent = "Đang đăng nhập...";
    displayError("login-error");

    try {
        const result = await apiRequest("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                email: $("email").value.trim(),
                password: $("password").value,
            }),
        });

        localStorage.setItem(TOKEN_KEY, result.access_token);
        await openDashboard(result.user);
    } catch (error) {
        displayError("login-error", error.message);
    } finally {
        button.disabled = false;
        button.textContent = "Đăng nhập";
    }
});

$("logout-button")?.addEventListener("click", () => {
    clearSession();
    $("password").value = "";
    displayError("login-error");
});

$("refresh-button")?.addEventListener("click", loadDashboard);

$("tickets-nav")?.addEventListener("click", () => openTickets());
$("users-nav")?.addEventListener("click", openUsers);

$("overview-nav")?.addEventListener("click", async () => {
    showOverviewSections();
    setPage("Tổng quan", "WORKSPACE / OVERVIEW");
    await loadDashboard();
});

document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-ticket-id]");
    if (button) openTicketDetail(button.dataset.ticketId);
});

document.addEventListener("click", (event) => {
    const card = event.target.closest("[data-ticket-status]");
    if (card) openTickets(card.dataset.ticketStatus || "");
});

async function restoreSession() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
        showLogin();
        return;
    }

    try {
        const user = await apiRequest("/auth/me");
        await openDashboard(user);
    } catch {
        clearSession();
    }
}

restoreSession();
