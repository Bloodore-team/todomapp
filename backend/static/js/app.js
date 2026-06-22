// Frontend logic (vanilla JS) - with Web Push subscription
const API = {
  async get(url){
    const r = await fetch(url);
    return r.json();
  },
  async post(url, data){
    const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)});
    return r.json();
  },
  async put(url, data){
    const r = await fetch(url, {method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)});
    return r.json();
  },
  async delete(url){
    const r = await fetch(url, {method:'DELETE'});
    return r;
  }
}

let tasks = [];
let projects = [];

// helper for base64 -> Uint8Array
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

async function registerServiceWorkerAndSubscribe(){
  if(!('serviceWorker' in navigator) || !('PushManager' in window)) return;
  try{
    const reg = await navigator.serviceWorker.register('/static/js/sw.js');
    // fetch VAPID public key
    const keyResp = await fetch('/api/vapid_public');
    const keyJson = await keyResp.json();
    const vapidPublic = keyJson.publicKey;
    if(Notification.permission === 'default') await Notification.requestPermission();
    if(Notification.permission !== 'granted') return;
    let sub = await reg.pushManager.getSubscription();
    if(!sub){
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublic)
      });
      // send subscription to server
      await fetch('/api/subscribe', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(sub)});
    } else {
      // ensure server has it (optional)
      await fetch('/api/subscribe', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(sub)});
    }
  }catch(e){
    console.error('SW or Push registration failed', e);
  }
}

async function loadProjects(){
  projects = await API.get('/api/projects');
  const list = document.getElementById('project-list');
  list.innerHTML='';
  const select = document.getElementById('task-project');
  select.innerHTML='';
  projects.forEach(p=>{
    const li = document.createElement('li');
    li.className='px-3 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700';
    li.textContent = p.name;
    list.appendChild(li);

    const opt = document.createElement('option');
    opt.value = p.id; opt.textContent = p.name;
    select.appendChild(opt);
  });
}

async function loadTasks(){
  tasks = await API.get('/api/tasks');
  renderTasks();
  updateStats();
}

function renderTasks(){
  const container = document.getElementById('tasks');
  container.innerHTML='';
  // simple card layout
  tasks.forEach(t=>{
    const card = document.createElement('div');
    card.className='p-4 bg-white dark:bg-gray-800 rounded shadow';
    card.innerHTML = `
      <div class="flex justify-between items-start">
        <div>
          <div class="font-semibold">${escapeHtml(t.title)}</div>
          <div class="text-sm text-gray-500">${t.description?escapeHtml(t.description):''}</div>
        </div>
        <div class="text-right">
          <div class="text-xs text-gray-500">${t.status}</div>
          <div class="mt-2">
            <button data-id="${t.id}" class="fav-btn text-yellow-400">★</button>
            <button data-id="${t.id}" class="edit-btn text-blue-500">✎</button>
            <button data-id="${t.id}" class="del-btn text-red-500">🗑</button>
          </div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });

  // hooks
  document.querySelectorAll('.del-btn').forEach(b=>b.addEventListener('click', async e=>{
    const id = e.currentTarget.dataset.id;
    await API.delete('/api/tasks/'+id);
    await loadTasks();
  }));
  document.querySelectorAll('.edit-btn').forEach(b=>b.addEventListener('click', e=>{
    const id = e.currentTarget.dataset.id;
    openTaskModal(tasks.find(x=>x.id==id));
  }));
  document.querySelectorAll('.fav-btn').forEach(b=>b.addEventListener('click', async e=>{
    const id = e.currentTarget.dataset.id;
    const t = tasks.find(x=>x.id==id);
    await API.put('/api/tasks/'+id, {...t, favorite: !t.favorite});
    await loadTasks();
  }));
}

function escapeHtml(s){
  if(!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

async function updateStats(){
  const s = await API.get('/api/stats');
  document.getElementById('stat-done').textContent = s.done;
  document.getElementById('stat-en_cours').textContent = s.en_cours;
  document.getElementById('stat-todo').textContent = s.todo;
  renderChart(s.activity||[]);
}

let chart = null;
function renderChart(data){
  const ctx = document.getElementById('activityChart').getContext('2d');
  const labels = data.map(d=>d.date);
  const counts = data.map(d=>d.count);
  if(chart) chart.destroy();
  chart = new Chart(ctx, {
    type: 'line',
    data: {labels, datasets:[{label:'Tâches créées', data: counts, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.2)'}]}
  });
}

// Task modal
let editingTask = null;
function openTaskModal(task=null){
  editingTask = task;
  document.getElementById('task-modal').style.display='flex';
  document.getElementById('task-title').value = task?task.title:'';
  document.getElementById('task-desc').value = task?task.description:'';
  document.getElementById('task-status').value = task?task.status:'todo';
  document.getElementById('task-project').value = task?task.project_id||'':'';
}
function closeTaskModal(){
  editingTask = null;
  document.getElementById('task-modal').style.display='none';
}

async function saveTask(){
  const payload = {
    title: document.getElementById('task-title').value,
    description: document.getElementById('task-desc').value,
    status: document.getElementById('task-status').value,
    project_id: document.getElementById('task-project').value || null,
  };
  if(editingTask){
    await API.put('/api/tasks/'+editingTask.id, payload);
  } else {
    await API.post('/api/tasks', payload);
  }
  closeTaskModal();
  await loadTasks();
}

// UI wiring
window.addEventListener('load', async ()=>{
  await registerServiceWorkerAndSubscribe();
  await loadProjects();
  await loadTasks();

  document.getElementById('new-task-btn').addEventListener('click', ()=>openTaskModal());
  document.getElementById('cancel-task').addEventListener('click', ()=>closeTaskModal());
  document.getElementById('save-task').addEventListener('click', ()=>saveTask());

  document.getElementById('create-project').addEventListener('click', async ()=>{
    const name = document.getElementById('new-project-name').value.trim();
    if(!name) return alert('Nom requis');
    await API.post('/api/projects', {name});
    document.getElementById('new-project-name').value='';
    await loadProjects();
  });

  document.getElementById('show-dashboard').addEventListener('click', ()=>{
    document.getElementById('dashboard').scrollIntoView();
  });
  document.getElementById('show-calendar').addEventListener('click', ()=>{
    window.location.href='/calendar';
  });

  document.getElementById('toggle-dark').addEventListener('click', ()=>{
    document.documentElement.classList.toggle('dark');
  });

  // basic reminders polling (fallback)
  setInterval(checkReminders, 60*1000);
  checkReminders();
});

async function checkReminders(){
  if(!('Notification' in window)) return;
  if(Notification.permission === 'default') Notification.requestPermission();
  const now = new Date();
  tasks.forEach(t=>{
    if(t.remind_at && new Date(t.remind_at) <= now && !t._reminded){
      if(Notification.permission === 'granted'){
        new Notification('Rappel: '+t.title, {body: t.description||''});
      }
      t._reminded = true; // local flag
    }
  });
}
