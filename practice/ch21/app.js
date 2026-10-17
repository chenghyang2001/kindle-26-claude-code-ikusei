// 待辦清單主程式：純 JS，資料存於 localStorage
'use strict';

const STORAGE_KEY = 'k26-todos';
const MAX_TITLE_LENGTH = 200;

const form = document.getElementById('new-todo-form');
const input = document.getElementById('new-todo-input');
const list = document.getElementById('todo-list');
const message = document.getElementById('message');
const countLabel = document.getElementById('todo-count');
const filterNav = document.getElementById('filters');
const clearCompletedButton = document.getElementById('clear-completed');

const FILTERS = {
  all: () => true,
  active: (t) => !t.done,
  completed: (t) => t.done,
};

let currentFilter = 'all';
let todos = loadTodos();

function showMessage(text) {
  message.textContent = text;
}

// localStorage 可能被停用（隱私模式）或內容損毀，任何狀況都不能讓頁面崩潰
function loadTodos() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === null) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) throw new TypeError('資料格式不是陣列');
    return parsed.filter((t) => t && typeof t.id === 'string' && typeof t.title === 'string');
  } catch (err) {
    console.error('讀取待辦失敗：', err);
    showMessage('儲存的資料無法讀取，已重設為空清單。');
    return [];
  }
}

function saveTodos() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  } catch (err) {
    console.error('儲存待辦失敗：', err);
    showMessage('無法儲存到瀏覽器，重新整理後資料會遺失。');
  }
}

function createId() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function addTodo(rawTitle) {
  const title = rawTitle.trim().slice(0, MAX_TITLE_LENGTH);
  if (title === '') {
    showMessage('請輸入待辦內容。');
    return false;
  }
  // 先清提示再存檔，存檔失敗的警告才不會被立刻蓋掉
  showMessage('');
  todos.push({ id: createId(), title, done: false, createdAt: Date.now() });
  saveTodos();
  return true;
}

function toggleTodo(id) {
  const todo = todos.find((t) => t.id === id);
  if (!todo) return;
  todo.done = !todo.done;
  saveTodos();
}

function deleteTodo(id) {
  todos = todos.filter((t) => t.id !== id);
  saveTodos();
}

// 用 textContent 建立節點，使用者輸入的 HTML 只會顯示成文字（防 XSS）
function createTodoItem(todo) {
  const li = document.createElement('li');
  li.dataset.id = todo.id;
  li.classList.toggle('done', todo.done);

  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.className = 'toggle';
  checkbox.checked = todo.done;
  checkbox.setAttribute('aria-label', `標記完成：${todo.title}`);

  const span = document.createElement('span');
  span.className = 'title';
  span.textContent = todo.title;

  const deleteButton = document.createElement('button');
  deleteButton.type = 'button';
  deleteButton.className = 'delete';
  deleteButton.textContent = '刪除';
  deleteButton.setAttribute('aria-label', `刪除：${todo.title}`);

  li.append(checkbox, span, deleteButton);
  return li;
}

function clearCompleted() {
  todos = todos.filter((t) => !t.done);
  saveTodos();
}

function renderStatus() {
  const remaining = todos.filter(FILTERS.active).length;
  countLabel.textContent = `剩下 ${remaining} 項未完成`;
  clearCompletedButton.disabled = !todos.some(FILTERS.completed);
  for (const button of filterNav.querySelectorAll('button[data-filter]')) {
    const isActive = button.dataset.filter === currentFilter;
    button.classList.toggle('active', isActive);
    button.setAttribute('aria-pressed', String(isActive));
  }
}

function render() {
  const visible = todos.filter(FILTERS[currentFilter]);
  list.replaceChildren(...visible.map(createTodoItem));
  renderStatus();
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  if (addTodo(input.value)) {
    input.value = '';
    render();
  }
  input.focus();
});

// 事件委派：清單每次重繪都會換新節點，綁在父層就不必重複綁定
list.addEventListener('click', (event) => {
  const item = event.target.closest('li[data-id]');
  if (!item) return;
  if (event.target.matches('.toggle')) {
    toggleTodo(item.dataset.id);
    render();
  } else if (event.target.matches('.delete')) {
    deleteTodo(item.dataset.id);
    render();
  }
});

filterNav.addEventListener('click', (event) => {
  const button = event.target.closest('button[data-filter]');
  if (!button || !(button.dataset.filter in FILTERS)) return;
  currentFilter = button.dataset.filter;
  render();
});

clearCompletedButton.addEventListener('click', () => {
  clearCompleted();
  render();
});

render();
