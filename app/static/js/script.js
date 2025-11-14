const apiUrl = '/notes';

async function loadNotes() {
  const res = await fetch(apiUrl);
  const notes = await res.json();
  const container = document.getElementById('notes');
  container.innerHTML = '';
  notes.forEach(note => {
    const div = document.createElement('div');
    div.className = 'note';
    div.innerHTML = `
      <div class="note-title">${note.title}</div>
      <div>${note.content}</div>
      <button class="delete-btn" onclick="deleteNote(${note.id})">Delete</button>
    `;
    container.appendChild(div);
  });
}

async function addNote(e) {
  e.preventDefault();
  const title = document.getElementById('title').value;
  const content = document.getElementById('content').value;

  await fetch(apiUrl, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ title, content })
  });

  document.getElementById('noteForm').reset();
  loadNotes();
}

async function deleteNote(id) {
  await fetch(`${apiUrl}/${id}`, { method: 'DELETE' });
  loadNotes();
}

document.getElementById('noteForm').addEventListener('submit', addNote);
loadNotes();
