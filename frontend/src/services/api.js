const API_BASE = "http://localhost:5000/api";

// ---------- AUTH ----------
export async function loginUser(credentials) {
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(credentials)
  });
  return res.json();
}

export async function logoutUser() {
  await fetch(`${API_BASE}/logout`, {
    method: "POST",
    credentials: "include"
  });
}

// ---------- RETURNS ----------
export async function submitReturn(data) {
  const res = await fetch(`${API_BASE}/returns`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data)
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error);
  return json;
}

export async function fetchMyReturns() {
  const res = await fetch(`${API_BASE}/returns/my`, {
    credentials: "include"
  });
  return res.json();
}

export async function fetchAllReturns() {
  const res = await fetch(`${API_BASE}/returns/all`, {
    credentials: "include"
  });
  return res.json();
}

export async function approveReturn(id) {
  const res = await fetch(`${API_BASE}/returns/${id}/approve`, {
    method: "PUT",
    credentials: "include"
  });
  return res.json();
}

export async function rejectReturn(id) {
  const res = await fetch(`${API_BASE}/returns/${id}/reject`, {
    method: "PUT",
    credentials: "include"
  });
  return res.json();
}

export async function completeRefund(id) {
  const res = await fetch(`${API_BASE}/returns/${id}/refund`, {
    method: "PUT",
    credentials: "include"
  });
  return res.json();
}

export async function fetchAuditLogs(limit = 50, order = "desc") {
  const res = await fetch(
    `${API_BASE}/admin/audit-logs?limit=${limit}&order=${order}`,
    { credentials: "include" }
  );
  return res.json();
}
