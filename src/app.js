// 可爱便签 - 前端应用逻辑

const { invoke } = window.__TAURI__.core;
const { appWindow } = window.__TAURI__.window;

// 应用状态
const state = {
    config: null,
    currentDate: new Date().toISOString().split('T')[0],
    isExpanded: true,
    isLocked: false,
    currentView: 'todo', // 'todo' or 'calendar'
    selectedFilterTagIds: new Set(),
    currentCalendarMonth: new Date(),
    urgentCount: 0,
};

// DOM元素
const elements = {
    expandedView: document.getElementById('expanded-view'),
    collapsedView: document.getElementById('collapsed-view'),
    lockedView: document.getElementById('locked-view'),
    titleBar: document.getElementById('title-bar'),
    lockBtn: document.getElementById('lock-btn'),
    settingsBtn: document.getElementById('settings-btn'),
    collapseBtn: document.getElementById('collapse-btn'),
    closeBtn: document.getElementById('close-btn'),
    searchInput: document.getElementById('search-input'),
    tagFilterBtn: document.getElementById('tag-filter-btn'),
    todayBtn: document.getElementById('today-btn'),
    calendarBtn: document.getElementById('calendar-btn'),
    tagManagerBtn: document.getElementById('tag-manager-btn'),
    dateDisplay: document.getElementById('date-display'),
    todoListView: document.getElementById('todo-list-view'),
    calendarView: document.getElementById('calendar-view'),
    todoList: document.getElementById('todo-list'),
    calendar: document.getElementById('calendar'),
    newTodoInput: document.getElementById('new-todo-input'),
    addBtn: document.getElementById('add-btn'),
    collapsedIcon: document.getElementById('collapsed-icon'),
    urgentBadge: document.getElementById('urgent-badge'),
    lockedIcon: document.getElementById('locked-icon'),
    modalOverlay: document.getElementById('modal-overlay'),
    modalContent: document.getElementById('modal-content'),
};

// 初始化应用
async function init() {
    await loadConfig();
    applyTheme();
    await generateRepeatTodos();
    await updateUrgentBadge();
    refreshTodos();
    updateDateDisplay();
    setupEventListeners();
    startUrgentTimer();
}

// 加载配置
async function loadConfig() {
    state.config = await invoke('get_config');
    state.isLocked = state.config.is_locked;
    updateLockButton();
    applyViewState();
}

// 应用主题
function applyTheme() {
    const theme = state.config?.theme || 'light';
    const isTransparent = state.config?.is_transparent || false;
    
    document.body.className = `theme-${theme}${isTransparent ? ' transparent' : ''}`;
}

// 更新锁定按钮
function updateLockButton() {
    elements.lockBtn.textContent = state.isLocked ? '🔒' : '🔓';
}

// 应用视图状态
function applyViewState() {
    elements.expandedView.classList.add('hidden');
    elements.collapsedView.classList.add('hidden');
    elements.lockedView.classList.add('hidden');
    
    if (state.isLocked) {
        elements.lockedView.classList.remove('hidden');
    } else if (state.isExpanded) {
        elements.expandedView.classList.remove('hidden');
    } else {
        elements.collapsedView.classList.remove('hidden');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 窗口拖动
    elements.titleBar.addEventListener('mousedown', async (e) => {
        if (e.target === elements.titleBar || e.target.classList.contains('title')) {
            await appWindow.startDragging();
        }
    });

    // 标题栏按钮
    elements.lockBtn.addEventListener('click', toggleLock);
    elements.settingsBtn.addEventListener('click', showSettingsModal);
    elements.collapseBtn.addEventListener('click', toggleExpand);
    elements.closeBtn.addEventListener('click', closeWindow);

    // 搜索
    elements.searchInput.addEventListener('input', handleSearch);

    // 标签筛选
    elements.tagFilterBtn.addEventListener('click', showTagFilterModal);

    // 模式切换
    elements.todayBtn.addEventListener('click', showTodoView);
    elements.calendarBtn.addEventListener('click', showCalendarView);
    elements.tagManagerBtn.addEventListener('click', showTagManagerModal);

    // 添加待办
    elements.newTodoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTodo();
    });
    elements.addBtn.addEventListener('click', addTodo);

    // 收起模式
    elements.collapsedIcon.addEventListener('click', handleCollapsedClick);
    elements.collapsedIcon.addEventListener('contextmenu', showCollapsedMenu);

    // 锁定模式
    elements.lockedIcon.addEventListener('click', handleLockedClick);
    elements.lockedIcon.addEventListener('contextmenu', showLockedMenu);

    // 模态框
    elements.modalOverlay.addEventListener('click', (e) => {
        if (e.target === elements.modalOverlay) {
            closeModal();
        }
    });

    // 窗口大小变化时保存位置
    window.addEventListener('resize', debounce(saveWindowGeometry, 500));
    window.addEventListener('move', debounce(saveWindowGeometry, 500));
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 保存窗口位置和大小
async function saveWindowGeometry() {
    try {
        const position = await appWindow.outerPosition();
        const size = await appWindow.outerSize();
        await invoke('set_window_geometry', {
            x: position.x,
            y: position.y,
            width: size.width,
            height: size.height,
        });
    } catch (e) {
        console.error('Failed to save window geometry:', e);
    }
}

// 切换展开/收起
function toggleExpand() {
    state.isExpanded = !state.isExpanded;
    applyViewState();
}

// 切换锁定
async function toggleLock() {
    if (state.isLocked) {
        showPasswordModal('unlock');
    } else {
        const hasPassword = await invoke('has_password');
        if (hasPassword) {
            state.isLocked = true;
            await invoke('set_locked', { isLocked: true });
            updateLockButton();
            applyViewState();
        } else {
            showSetPasswordModal();
        }
    }
}

// 关闭窗口
async function closeWindow() {
    await saveWindowGeometry();
    await appWindow.close();
}

// 处理收起模式点击
function handleCollapsedClick(e) {
    if (state.urgentCount > 0) {
        showUrgentTodosModal();
    } else {
        toggleExpand();
    }
}

// 处理锁定模式点击
function handleLockedClick() {
    showPasswordModal('unlock');
}

// 显示收起模式右键菜单
function showCollapsedMenu(e) {
    e.preventDefault();
    showContextMenu(e.clientX, e.clientY, [
        { label: '展开', action: () => { state.isExpanded = true; applyViewState(); } },
        { label: '关闭', action: closeWindow },
    ]);
}

// 显示锁定模式右键菜单
function showLockedMenu(e) {
    e.preventDefault();
    showContextMenu(e.clientX, e.clientY, [
        { label: '解锁', action: () => showPasswordModal('unlock') },
        { label: '关闭', action: closeWindow },
    ]);
}

// 显示右键菜单
function showContextMenu(x, y, items) {
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();

    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;

    items.forEach(item => {
        const menuItem = document.createElement('div');
        menuItem.className = 'context-menu-item';
        menuItem.textContent = item.label;
        menuItem.addEventListener('click', () => {
            item.action();
            menu.remove();
        });
        menu.appendChild(menuItem);
    });

    document.body.appendChild(menu);

    const closeMenu = () => {
        menu.remove();
        document.removeEventListener('click', closeMenu);
    };
    setTimeout(() => document.addEventListener('click', closeMenu), 0);
}

// 更新日期显示
function updateDateDisplay() {
    const date = new Date(state.currentDate);
    const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    const weekday = weekdays[date.getDay() === 0 ? 6 : date.getDay() - 1];
    elements.dateDisplay.textContent = `${state.currentDate} ${weekday}`;
}

// 显示待办视图
function showTodoView() {
    state.currentView = 'todo';
    elements.todayBtn.classList.add('active');
    elements.calendarBtn.classList.remove('active');
    elements.todoListView.classList.remove('hidden');
    elements.calendarView.classList.add('hidden');
}

// 显示日历视图
function showCalendarView() {
    state.currentView = 'calendar';
    elements.todayBtn.classList.remove('active');
    elements.calendarBtn.classList.add('active');
    elements.todoListView.classList.add('hidden');
    elements.calendarView.classList.remove('hidden');
    renderCalendar();
}

// 渲染日历
async function renderCalendar() {
    const year = state.currentCalendarMonth.getFullYear();
    const month = state.currentCalendarMonth.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const firstDayWeekday = firstDay.getDay(); // 0=周日
    
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    
    const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
    
    let html = `
        <div class="calendar-header">
            <button class="calendar-nav" onclick="prevMonth()">◀</button>
            <span class="calendar-title">${year}年${month + 1}月</span>
            <button class="calendar-nav" onclick="nextMonth()">▶</button>
        </div>
        <div class="calendar-weekdays">
    `;
    
    weekdays.forEach(day => {
        html += `<div class="calendar-weekday">${day}</div>`;
    });
    
    html += `</div><div class="calendar-days">`;
    
    // 上个月的日期
    const startDay = firstDayWeekday === 0 ? 6 : firstDayWeekday - 1;
    for (let i = startDay - 1; i >= 0; i--) {
        html += `<div class="calendar-day other-month">${prevMonthLastDay - i}</div>`;
    }
    
    // 当月的日期
    const today = new Date().toISOString().split('T')[0];
    
    for (let day = 1; day <= lastDay.getDate(); day++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const todos = await invoke('get_todos', { dateStr });
        
        let classes = ['calendar-day'];
        if (dateStr === today) classes.push('today');
        
        let indicatorHtml = '';
        if (todos.length > 0) {
            const allCompleted = todos.every(t => t.completed);
            const anyIncomplete = todos.some(t => !t.completed);
            
            if (allCompleted) {
                classes.push('has-todos', 'all-completed');
                indicatorHtml = `<div class="calendar-day-indicator completed"></div>`;
            } else if (anyIncomplete) {
                classes.push('has-todos');
                indicatorHtml = `<div class="calendar-day-indicator incomplete"></div>`;
            }
        }
        
        html += `
            <div class="${classes.join(' ')}" onclick="selectCalendarDate('${dateStr}')">
                ${day}
                ${indicatorHtml}
            </div>
        `;
    }
    
    // 下个月的日期
    const totalDays = startDay + lastDay.getDate();
    const remainingDays = 42 - totalDays;
    for (let day = 1; day <= remainingDays; day++) {
        html += `<div class="calendar-day other-month">${day}</div>`;
    }
    
    html += `</div>`;
    elements.calendar.innerHTML = html;
}

// 上个月
function prevMonth() {
    state.currentCalendarMonth.setMonth(state.currentCalendarMonth.getMonth() - 1);
    renderCalendar();
}

// 下个月
function nextMonth() {
    state.currentCalendarMonth.setMonth(state.currentCalendarMonth.getMonth() + 1);
    renderCalendar();
}

// 选择日历日期
function selectCalendarDate(dateStr) {
    state.currentDate = dateStr;
    updateDateDisplay();
    showTodoView();
    elements.searchInput.value = '';
    state.selectedFilterTagIds.clear();
    refreshTodos();
}

// 刷新待办列表
async function refreshTodos() {
    const keyword = elements.searchInput.value.trim();
    const hasKeyword = keyword.length > 0;
    const hasTags = state.selectedFilterTagIds.size > 0;
    
    if (hasKeyword || hasTags) {
        await searchTodos(keyword || null, hasTags ? Array.from(state.selectedFilterTagIds) : null);
        return;
    }
    
    const todos = await invoke('get_todos', { dateStr: state.currentDate });
    
    // 排序：未完成且有截止时间的在前，然后是未完成无截止时间，最后是已完成
    const sortedTodos = todos.sort((a, b) => {
        if (a.completed !== b.completed) {
            return a.completed ? 1 : -1;
        }
        if (a.deadline && b.deadline) {
            return a.deadline.localeCompare(b.deadline);
        }
        return a.deadline ? -1 : (b.deadline ? 1 : 0);
    });
    
    if (sortedTodos.length === 0) {
        elements.todoList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">✨</div>
                <div class="empty-state-text">今天还没有待办事项哦~</div>
            </div>
        `;
        return;
    }
    
    elements.todoList.innerHTML = sortedTodos.map(todo => renderTodoItem(todo)).join('');
}

// 渲染待办项
function renderTodoItem(todo) {
    const completedClass = todo.completed ? 'completed' : '';
    const tags = todo.tag_ids || [];
    const hasDeadline = todo.deadline !== null;
    const hasRepeat = todo.repeat_rule !== null;
    
    let urgentClass = '';
    if (hasDeadline && !todo.completed) {
        const deadline = new Date(todo.deadline);
        const now = new Date();
        const diffHours = (deadline - now) / (1000 * 60 * 60);
        if (diffHours > 0 && diffHours <= 3) {
            urgentClass = 'urgent';
        }
    }
    
    const tagBadges = tags.length > 0 
        ? tags.map(tagId => `<span class="tag-badge" data-tag-id="${tagId}">🏷️ ${tagId}</span>`).join('')
        : '';
    
    return `
        <div class="todo-item ${completedClass}" data-id="${todo.id}">
            <div class="todo-checkbox" onclick="toggleTodo('${todo.id}')"></div>
            <div class="todo-content">
                <div class="todo-text">${escapeHtml(todo.text)}</div>
                ${tagBadges ? `<div class="todo-tags">${tagBadges}</div>` : ''}
            </div>
            <div class="todo-actions">
                <button class="action-btn tag-btn" onclick="showTagPicker('${todo.id}')" title="标签">🏷️</button>
                <button class="action-btn clock-btn ${urgentClass}" onclick="showDeadlinePicker('${todo.id}')" title="截止时间" ${todo.completed ? 'disabled' : ''}>⏰</button>
                <button class="action-btn repeat-btn" onclick="showRepeatPicker('${todo.id}')" title="重复">🔄</button>
                <button class="action-btn delete-btn" onclick="confirmDeleteTodo('${todo.id}')" title="删除">🗑️</button>
            </div>
        </div>
    `;
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 添加待办
async function addTodo() {
    const text = elements.newTodoInput.value.trim();
    if (!text) return;
    
    try {
        await invoke('add_todo', {
            dateStr: state.currentDate,
            text: text,
            deadline: null,
            tagIds: null,
            repeatRule: null,
        });
        elements.newTodoInput.value = '';
        refreshTodos();
    } catch (e) {
        showMessage('错误', `添加失败: ${e}`);
    }
}

// 切换待办完成状态
async function toggleTodo(todoId) {
    const todos = await invoke('get_todos', { dateStr: state.currentDate });
    const todo = todos.find(t => t.id === todoId);
    
    if (todo) {
        await invoke('update_todo', {
            dateStr: state.currentDate,
            todoId: todoId,
            completed: !todo.completed,
        });
        refreshTodos();
        await updateUrgentBadge();
    }
}

// 确认删除待办
function confirmDeleteTodo(todoId) {
    showConfirmModal('确认删除', '确定要删除这个待办事项吗？', async () => {
        await invoke('delete_todo', {
            dateStr: state.currentDate,
            todoId: todoId,
        });
        refreshTodos();
    });
}

// 处理搜索
function handleSearch() {
    refreshTodos();
}

// 搜索待办
async function searchTodos(keyword, tagIds) {
    const results = await invoke('search_todos', { keyword, tagIds });
    
    if (results.length === 0) {
        elements.todoList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-text">没有找到匹配的待办事项</div>
            </div>
        `;
        return;
    }
    
    elements.todoList.innerHTML = results.map(result => `
        <div class="search-result-item" onclick="goToDate('${result.date}')">
            <div class="search-result-date">📅 ${result.date}</div>
            <div class="search-result-text">${escapeHtml(result.todo.text)}</div>
            ${result.todo.tag_ids && result.todo.tag_ids.length > 0 
                ? `<div class="todo-tags">${result.todo.tag_ids.map(id => `<span class="tag-badge">🏷️ ${id}</span>`).join('')}</div>` 
                : ''}
        </div>
    `).join('');
}

// 跳转到日期
function goToDate(dateStr) {
    state.currentDate = dateStr;
    elements.searchInput.value = '';
    state.selectedFilterTagIds.clear();
    updateDateDisplay();
    showTodoView();
    refreshTodos();
}

// 更新紧急任务角标
async function updateUrgentBadge() {
    const urgentTodos = await invoke('get_urgent_todos', { hours: 3 });
    state.urgentCount = urgentTodos.length;
    
    if (state.urgentCount > 0) {
        elements.urgentBadge.textContent = state.urgentCount;
        elements.urgentBadge.classList.remove('hidden');
    } else {
        elements.urgentBadge.classList.add('hidden');
    }
}

// 启动紧急任务检查定时器
function startUrgentTimer() {
    setInterval(updateUrgentBadge, 60000); // 每分钟检查一次
}

// 生成重复待办
async function generateRepeatTodos() {
    const count = await invoke('generate_repeat_todos');
    if (count > 0) {
        refreshTodos();
    }
}

// ==================== 模态框相关 ====================

// 显示模态框
function showModal(content) {
    elements.modalContent.innerHTML = content;
    elements.modalOverlay.classList.remove('hidden');
}

// 关闭模态框
function closeModal() {
    elements.modalOverlay.classList.add('hidden');
}

// 显示消息
function showMessage(title, message) {
    showModal(`
        <div class="modal-title">${title}</div>
        <div class="modal-body">
            <p>${message}</p>
        </div>
        <div class="modal-footer">
            <button class="btn btn-primary" onclick="closeModal()">确定</button>
        </div>
    `);
}

// 显示确认对话框
function showConfirmModal(title, message, onConfirm) {
    window._confirmCallback = onConfirm;
    showModal(`
        <div class="modal-title">${title}</div>
        <div class="modal-body">
            <p>${message}</p>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal()">取消</button>
            <button class="btn btn-danger" onclick="window._confirmCallback(); closeModal();">确定</button>
        </div>
    `);
}

// 显示密码模态框
function showPasswordModal(mode) {
    window._passwordMode = mode;
    showModal(`
        <div class="modal-title">🔒 ${mode === 'unlock' ? '验证密码' : '设置密码'}</div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label">请输入密码:</label>
                <input type="password" id="password-input" class="form-input" placeholder="输入密码...">
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal()">取消</button>
            <button class="btn btn-primary" onclick="handlePasswordSubmit()">确定</button>
        </div>
    `);
    
    setTimeout(() => {
        document.getElementById('password-input').focus();
    }, 100);
}

// 处理密码提交
async function handlePasswordSubmit() {
    const password = document.getElementById('password-input').value;
    
    if (window._passwordMode === 'unlock') {
        const valid = await invoke('check_password', { password });
        if (valid) {
            state.isLocked = false;
            await invoke('set_locked', { isLocked: false });
            updateLockButton();
            applyViewState();
            closeModal();
        } else {
            showMessage('错误', '密码错误，请重试！');
        }
    }
}

// 显示设置密码模态框
function showSetPasswordModal() {
    showModal(`
        <div class="modal-title">🔑 设置密码</div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label">设置新密码:</label>
                <input type="password" id="new-password-input" class="form-input" placeholder="输入新密码...">
            </div>
            <div class="form-group">
                <label class="form-label">确认密码:</label>
                <input type="password" id="confirm-password-input" class="form-input" placeholder="再次输入密码...">
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal()">取消</button>
            <button class="btn btn-primary" onclick="handleSetPassword()">确定</button>
        </div>
    `);
}

// 处理设置密码
async function handleSetPassword() {
    const password1 = document.getElementById('new-password-input').value;
    const password2 = document.getElementById('confirm-password-input').value;
    
    if (!password1) {
        showMessage('错误', '密码不能为空！');
        return;
    }
    
    if (password1 !== password2) {
        showMessage('错误', '两次输入的密码不一致！');
        return;
    }
    
    await invoke('set_password', { password: password1 });
    closeModal();
    showMessage('成功', '密码设置成功！');
}

// 显示设置模态框
async function showSettingsModal() {
    const config = await invoke('get_config');
    const isLight = config.theme === 'light';
    const isDark = config.theme === 'dark';
    const isOpaque = !config.is_transparent;
    const isTransparent = config.is_transparent;
    
    showModal(`
        <div class="modal-title">⚙️ 设置</div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label">🎨 主题设置:</label>
                <div style="display: flex; gap: 10px;">
                    <button class="btn" style="background-color: ${isLight ? 'rgba(255, 200, 150, 0.9)' : 'rgba(230, 230, 230, 0.8)'}; color: ${isLight ? 'white' : '#5a4a3a'};" onclick="setTheme('light')">☀️ 明亮</button>
                    <button class="btn" style="background-color: ${isDark ? 'rgba(80, 80, 100, 0.9)' : 'rgba(230, 230, 230, 0.8)'}; color: ${isDark ? 'white' : '#5a4a3a'};" onclick="setTheme('dark')">🌙 暗黑</button>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">✨ 透明度:</label>
                <div style="display: flex; gap: 10px;">
                    <button class="btn" style="background-color: ${isOpaque ? 'rgba(100, 180, 255, 0.9)' : 'rgba(230, 230, 230, 0.8)'}; color: ${isOpaque ? 'white' : '#5a4a3a'};" onclick="setTransparent(false)">🖼️ 不透明</button>
                    <button class="btn" style="background-color: ${isTransparent ? 'rgba(100, 180, 255, 0.9)' : 'rgba(230, 230, 230, 0.8)'}; color: ${isTransparent ? 'white' : '#5a4a3a'};" onclick="setTransparent(true)">💎 透明</button>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal()">关闭</button>
        </div>
    `);
}

// 设置主题
async function setTheme(theme) {
    await invoke('set_theme', { theme });
    state.config = await invoke('get_config');
    applyTheme();
    showSettingsModal();
}

// 设置透明度
async function setTransparent(isTransparent) {
    await invoke('set_transparent', { isTransparent });
    state.config = await invoke('get_config');
    applyTheme();
    showSettingsModal();
}

// 显示标签管理模态框
async function showTagManagerModal() {
    const tags = await invoke('get_all_tags');
    
    const tagsHtml = tags.length > 0 
        ? tags.map(tag => `
            <div class="todo-item" style="margin-bottom: 8px;">
                <div class="todo-content">
                    <div class="todo-text">🏷️ ${escapeHtml(tag.name)}</div>
                </div>
                <div class="todo-actions">
                    <button class="action-btn" style="background-color: rgba(100, 150, 255, 0.8);" onclick="showEditTagModal('${tag.id}', '${escapeHtml(tag.name)}')">✏️</button>
                    <button class="action-btn delete-btn" onclick="confirmDeleteTag('${tag.id}')">🗑️</button>
                </div>
            </div>
        `).join('')
        : '<p style="opacity: 0.6; text-align: center; padding: 20px;">还没有标签</p>';
    
    showModal(`
        <div class="modal-title">🏷️ 标签管理</div>
        <div class="modal-body">
            <div class="form-group">
                <input type="text" id="new-tag-input" class="form-input" placeholder="输入新标签名称...">
            </div>
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <button class="btn btn-primary" onclick="addNewTag()">➕ 添加</button>
                <button class="btn btn-secondary" onclick="showTagHelp()">❓ 帮助</button>
            </div>
            <div>${tagsHtml}</div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal(); refreshTodos();">关闭</button>
        </div>
    `);
}

// 添加新标签
async function addNewTag() {
    const input = document.getElementById('new-tag-input');
    const name = input.value.trim();
    
    if (!name) {
        showMessage('提示', '请输入标签名称！');
        return;
    }
    
    try {
        await invoke('add_tag', { name });
        showTagManagerModal();
    } catch (e) {
        showMessage('提示', e);
    }
}

// 显示编辑标签模态框
function showEditTagModal(tagId, oldName) {
    showModal(`
        <div class="modal-title">✏️ 修改标签</div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label">输入新标签名称:</label>
                <input type="text" id="edit-tag-input" class="form-input" value="${oldName}">
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="showTagManagerModal()">取消</button>
            <button class="btn btn-primary" onclick="updateTag('${tagId}')">确定</button>
        </div>
    `);
}

// 更新标签
async function updateTag(tagId) {
    const newName = document.getElementById('edit-tag-input').value.trim();
    
    if (!newName) {
        showMessage('提示', '请输入标签名称！');
        return;
    }
    
    await invoke('update_tag', { tagId, newName });
    showTagManagerModal();
}

// 确认删除标签
function confirmDeleteTag(tagId) {
    showConfirmModal('确认删除', '确定要删除这个标签吗？该操作会从所有待办事项中移除此标签。', async () => {
        await invoke('delete_tag', { tagId });
        showTagManagerModal();
    });
}

// 显示标签帮助
function showTagHelp() {
    showMessage('标签管理帮助', `
📝 标签管理帮助：<br><br>
• 添加标签：在输入框中输入标签名称，点击"添加"按钮<br>
• 修改标签：点击标签旁边的✏️按钮<br>
• 删除标签：点击标签旁边的🗑️按钮<br>
• 使用标签：在待办事项中点击🏷️按钮选择标签<br><br>
标签可以帮助您更好地分类和管理待办事项！
    `);
}

// 显示标签筛选模态框
async function showTagFilterModal() {
    const tags = await invoke('get_all_tags');
    
    const tagsHtml = tags.length > 0 
        ? tags.map(tag => {
            const isSelected = state.selectedFilterTagIds.has(tag.id);
            return `
                <div class="todo-item" style="margin-bottom: 8px; cursor: pointer; background-color: ${isSelected ? 'rgba(255, 215, 0, 0.3)' : ''};" onclick="toggleFilterTag('${tag.id}')">
                    <div class="todo-content">
                        <div class="todo-text">${isSelected ? '✓' : '○'} 🏷️ ${escapeHtml(tag.name)}</div>
                    </div>
                </div>
            `;
        }).join('')
        : '<p style="opacity: 0.6; text-align: center; padding: 20px;">还没有标签，请先在标签管理中添加标签</p>';
    
    showModal(`
        <div class="modal-title">🏷️ 筛选标签</div>
        <div class="modal-body">
            <p style="font-size: 12px; opacity: 0.7; margin-bottom: 15px;">提示：可选择多个标签，筛选结果将包含所有选中标签的待办事项</p>
            <div>${tagsHtml}</div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="clearTagFilter()">清除筛选</button>
            <button class="btn btn-secondary" onclick="closeModal()">取消</button>
            <button class="btn btn-primary" onclick="applyTagFilter()">确定</button>
        </div>
    `);
}

// 切换筛选标签
async function toggleFilterTag(tagId) {
    if (state.selectedFilterTagIds.has(tagId)) {
        state.selectedFilterTagIds.delete(tagId);
    } else {
        state.selectedFilterTagIds.add(tagId);
    }
    showTagFilterModal();
}

// 清除标签筛选
function clearTagFilter() {
    state.selectedFilterTagIds.clear();
    closeModal();
    refreshTodos();
}

// 应用标签筛选
function applyTagFilter() {
    closeModal();
    refreshTodos();
}

// 显示标签选择器
async function showTagPicker(todoId) {
    const tags = await invoke('get_all_tags');
    const todos = await invoke('get_todos', { dateStr: state.currentDate });
    const todo = todos.find(t => t.id === todoId);
    const currentTagIds = new Set(todo?.tag_ids || []);
    
    const tagsHtml = tags.length > 0 
        ? tags.map(tag => {
            const isSelected = currentTagIds.has(tag.id);
            return `
                <div class="todo-item" style="margin-bottom: 8px; cursor: pointer; background-color: ${isSelected ? 'rgba(255, 215, 0, 0.3)' : ''};" onclick="toggleTodoTag('${tag.id}')">
                    <div class="todo-content">
                        <div class="todo-text">${isSelected ? '✓' : '○'} 🏷️ ${escapeHtml(tag.name)}</div>
                    </div>
                </div>
            `;
        }).join('')
        : '<p style="opacity: 0.6; text-align: center; padding: 20px;">还没有标签，请先在标签管理中添加标签</p>';
    
    window._currentTodoId = todoId;
    window._selectedTagIds = currentTagIds;
    
    showModal(`
        <div class="modal-title">🏷️ 选择标签</div>
        <div class="modal-body">
            <div>${tagsHtml}</div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal()">取消</button>
            <button class="btn btn-primary" onclick="saveTodoTags()">确定</button>
        </div>
    `);
}

// 切换待办标签
function toggleTodoTag(tagId) {
    if (window._selectedTagIds.has(tagId)) {
        window._selectedTagIds.delete(tagId);
    } else {
        window._selectedTagIds.add(tagId);
    }
    showTagPicker(window._currentTodoId);
}

// 保存待办标签
async function saveTodoTags() {
    await invoke('update_todo', {
        dateStr: state.currentDate,
        todoId: window._currentTodoId,
        tagIds: Array.from(window._selectedTagIds),
    });
    closeModal();
    refreshTodos();
}

// 显示截止时间选择器
async function showDeadlinePicker(todoId) {
    const todos = await invoke('get_todos', { dateStr: state.currentDate });
    const todo = todos.find(t => t.id === todoId);
    
    const now = new Date();
    const defaultTime = new Date(now.getTime() + 60 * 60 * 1000);
    const defaultValue = defaultTime.toISOString().slice(0, 16);
    
    let currentValue = defaultValue;
    if (todo?.deadline) {
        const deadline = new Date(todo.deadline);
        if (deadline > now) {
            currentValue = deadline.toISOString().slice(0, 16);
        }
    }
    
    window._currentTodoId = todoId;
    
    showModal(`
        <div class="modal-title">⏰ 设置截止时间</div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label">选择截止时间:</label>
                <input type="datetime-local" id="deadline-input" class="form-input" value="${currentValue}">
            </div>
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <button class="btn" style="background-color: rgba(100, 180, 255, 0.9); color: white;" onclick="setQuickDeadline(1)">1小时后</button>
                <button class="btn" style="background-color: rgba(100, 180, 255, 0.9); color: white;" onclick="setQuickDeadline(3)">3小时后</button>
                <button class="btn" style="background-color: rgba(100, 180, 255, 0.9); color: white;" onclick="setQuickDeadline(24)">明天此时</button>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="clearDeadline()">清除截止时间</button>
            <button class="btn btn-secondary" onclick="closeModal()">取消</button>
            <button class="btn btn-primary" onclick="saveDeadline()">确定</button>
        </div>
    `);
}

// 设置快捷截止时间
function setQuickDeadline(hours) {
    const time = new Date(Date.now() + hours * 60 * 60 * 1000);
    document.getElementById('deadline-input').value = time.toISOString().slice(0, 16);
}

// 清除截止时间
async function clearDeadline() {
    await invoke('update_todo', {
        dateStr: state.currentDate,
        todoId: window._currentTodoId,
        deadline: null,
    });
    closeModal();
    refreshTodos();
    await updateUrgentBadge();
}

// 保存截止时间
async function saveDeadline() {
    const input = document.getElementById('deadline-input');
    const deadline = new Date(input.value);
    
    await invoke('update_todo', {
        dateStr: state.currentDate,
        todoId: window._currentTodoId,
        deadline: deadline.toISOString(),
    });
    closeModal();
    refreshTodos();
    await updateUrgentBadge();
}

// 显示重复规则选择器
async function showRepeatPicker(todoId) {
    const todos = await invoke('get_todos', { dateStr: state.currentDate });
    const todo = todos.find(t => t.id === todoId);
    const currentRule = todo?.repeat_rule;
    
    window._currentTodoId = todoId;
    window._repeatRule = currentRule ? { ...currentRule } : {
        type: 'daily',
        interval: 1,
        weekdays: [],
        endDate: null,
        lastGenerated: null,
    };
    window._selectedWeekdays = new Set(currentRule?.weekdays || []);
    
    renderRepeatModal();
}

// 渲染重复模态框
function renderRepeatModal() {
    const rule = window._repeatRule;
    const isWeekly = rule.type === 'weekly';
    const hasEndDate = rule.endDate !== null;
    
    const weekdays = ['一', '二', '三', '四', '五', '六', '日'];
    const weekdayHtml = weekdays.map((day, i) => {
        const isSelected = window._selectedWeekdays.has(i);
        return `
            <label style="margin-right: 10px; cursor: pointer;">
                <input type="checkbox" ${isSelected ? 'checked' : ''} onchange="toggleWeekday(${i})">
                周${day}
            </label>
        `;
    }).join('');
    
    const typeOptions = [
        { value: 'daily', label: '🔄 每天重复' },
        { value: 'weekly', label: '📅 每周重复' },
        { value: 'monthly', label: '📆 每月重复' },
        { value: 'yearly', label: '🎂 每年重复' },
        { value: 'weekdays', label: '💼 工作日（周一至周五）' },
        { value: 'weekends', label: '🎉 周末（周六、周日）' },
    ];
    
    const typeHtml = typeOptions.map(opt => `
        <label style="display: block; margin-bottom: 8px; cursor: pointer;">
            <input type="radio" name="repeat-type" value="${opt.value}" ${rule.type === opt.value ? 'checked' : ''} onchange="setRepeatType('${opt.value}')">
            ${opt.label}
        </label>
    `).join('');
    
    const unitMap = {
        daily: '天',
        weekly: '周',
        monthly: '月',
        yearly: '年',
        weekdays: '天',
        weekends: '天',
    };
    
    const endDateValue = rule.endDate || '';
    
    showModal(`
        <div class="modal-title">🔄 设置重复规则</div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label">选择重复类型:</label>
                ${typeHtml}
            </div>
            <div class="form-group" id="interval-group">
                <label class="form-label">重复间隔:</label>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span>每</span>
                    <input type="number" id="interval-input" class="form-input" style="width: 80px;" min="1" max="999" value="${rule.interval}">
                    <span id="interval-unit">${unitMap[rule.type]}</span>
                </div>
            </div>
            ${isWeekly ? `
            <div class="form-group" id="weekdays-group">
                <label class="form-label">选择星期:</label>
                <div>${weekdayHtml}</div>
            </div>
            ` : ''}
            <div class="form-group">
                <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                    <input type="checkbox" id="has-end-date" ${hasEndDate ? 'checked' : ''} onchange="toggleEndDate()">
                    设置结束日期
                </label>
                ${hasEndDate ? `
                <div style="margin-top: 10px; display: flex; align-items: center; gap: 10px;">
                    <span>结束于:</span>
                    <input type="date" id="end-date-input" class="form-input" value="${endDateValue}">
                </div>
                ` : ''}
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="clearRepeat()">清除重复</button>
            <button class="btn btn-secondary" onclick="closeModal()">取消</button>
            <button class="btn btn-primary" onclick="saveRepeat()">确定</button>
        </div>
    `);
}

// 设置重复类型
function setRepeatType(type) {
    window._repeatRule.type = type;
    renderRepeatModal();
}

// 切换星期选择
function toggleWeekday(day) {
    if (window._selectedWeekdays.has(day)) {
        window._selectedWeekdays.delete(day);
    } else {
        window._selectedWeekdays.add(day);
    }
    renderRepeatModal();
}

// 切换结束日期
function toggleEndDate() {
    const checked = document.getElementById('has-end-date').checked;
    if (checked) {
        const tomorrow = new Date(Date.now() + 24 * 60 * 60 * 1000);
        window._repeatRule.endDate = tomorrow.toISOString().split('T')[0];
    } else {
        window._repeatRule.endDate = null;
    }
    renderRepeatModal();
}

// 清除重复
async function clearRepeat() {
    await invoke('update_todo', {
        dateStr: state.currentDate,
        todoId: window._currentTodoId,
        repeatRule: null,
    });
    closeModal();
    refreshTodos();
}

// 保存重复规则
async function saveRepeat() {
    const interval = parseInt(document.getElementById('interval-input').value) || 1;
    const endDateInput = document.getElementById('end-date-input');
    const endDate = endDateInput ? endDateInput.value : null;
    
    if (window._repeatRule.type === 'weekly' && window._selectedWeekdays.size === 0) {
        showMessage('提示', '请至少选择一个星期几！');
        return;
    }
    
    const repeatRule = {
        type: window._repeatRule.type,
        interval: interval,
        weekdays: Array.from(window._selectedWeekdays),
        endDate: endDate,
        lastGenerated: null,
    };
    
    await invoke('update_todo', {
        dateStr: state.currentDate,
        todoId: window._currentTodoId,
        repeatRule: repeatRule,
    });
    closeModal();
    refreshTodos();
}

// 显示紧急任务模态框
async function showUrgentTodosModal() {
    const urgentTodos = await invoke('get_urgent_todos', { hours: 3 });
    
    if (urgentTodos.length === 0) {
        showMessage('提示', '当前没有即将超时的任务~');
        return;
    }
    
    const todosHtml = urgentTodos.map(item => `
        <div class="search-result-item" onclick="goToDateFromModal('${item.date}')">
            <div class="search-result-date">📅 ${item.date}</div>
            <div class="search-result-text">${escapeHtml(item.todo.text)}</div>
        </div>
    `).join('');
    
    showModal(`
        <div class="modal-title">⏰ 即将超时的任务</div>
        <div class="modal-body">
            ${todosHtml}
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal()">关闭</button>
        </div>
    `);
}

// 从模态框跳转到日期
function goToDateFromModal(dateStr) {
    closeModal();
    goToDate(dateStr);
    if (!state.isExpanded) {
        state.isExpanded = true;
        applyViewState();
    }
}

// 初始化应用
init();
