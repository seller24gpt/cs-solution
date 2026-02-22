function fillDetails(call) {
  document.getElementById('call-id').value = call.id;
  document.getElementById('status').value = call.processing_status;
  document.getElementById('resolver').value = call.resolver_name || '';
  document.getElementById('channel').value = call.response_channel || '';
  document.getElementById('response-note').value = call.response_note || '';
  document.getElementById('action-note').value = call.action_note || '';

  const recordingLink = document.getElementById('recording-url');
  if (call.recording_url) {
    recordingLink.href = call.recording_url;
    recordingLink.innerText = call.recording_url;
  } else {
    recordingLink.href = '#';
    recordingLink.innerText = '-';
  }
  document.getElementById('transcript').innerText = call.transcript_text || '-';
  document.getElementById('summary').innerText = call.summary_text || '-';
}

async function loadDashboard() {
  const res = await fetch('/api/dashboard/daily');
  const data = await res.json();
  document.getElementById('inbound').innerText = data.inbound_count;
  document.getElementById('processed').innerText = data.processed_count;
  document.getElementById('unprocessed').innerText = data.unprocessed_count;
  document.getElementById('processed-rate').innerText = `${data.processed_rate}%`;
}

async function loadCalls() {
  const res = await fetch('/api/calls');
  const calls = await res.json();
  const tbody = document.getElementById('calls-body');
  tbody.innerHTML = '';

  calls.forEach((call) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${call.id}</td>
      <td>${new Date(call.inbound_at).toLocaleString()}</td>
      <td>${call.caller_number}</td>
      <td>${call.summary_text}</td>
      <td>${call.processing_status}</td>
    `;
    tr.classList.add('clickable-row');
    tr.addEventListener('click', () => fillDetails(call));
    tbody.appendChild(tr);
  });

  if (calls.length > 0) {
    fillDetails(calls[0]);
  }
}

document.getElementById('update-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('call-id').value;
  const payload = {
    processing_status: document.getElementById('status').value,
    resolver_name: document.getElementById('resolver').value,
    response_channel: document.getElementById('channel').value,
    response_note: document.getElementById('response-note').value,
    action_note: document.getElementById('action-note').value,
    follow_up_required: false,
    follow_up_due_at: null,
  };

  const res = await fetch(`/api/calls/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const message = document.getElementById('form-message');
  if (!res.ok) {
    const err = await res.json();
    message.innerText = `저장 실패: ${err.detail}`;
    return;
  }

  message.innerText = '저장 완료';
  await loadDashboard();
  await loadCalls();
});

loadDashboard();
loadCalls();
