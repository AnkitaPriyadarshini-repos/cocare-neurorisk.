// Small wrapper around the backend API.
async function req(method, path, body) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`${method} ${path} failed: ${res.status}`)
  return res.json()
}

export const api = {
  listUsers: () => req('GET', '/users'),
  getUser: (id) => req('GET', `/users/${id}`),
  createUser: (data) => req('POST', '/users', data),
  updateUser: (id, data) => req('PATCH', `/users/${id}`, data),
  startSession: (user_id, game) => req('POST', '/sessions', { user_id, game }),
  logAttempt: (sid, attempt) => req('POST', `/sessions/${sid}/attempts`, attempt),
  endSession: (sid, completed) => req('POST', `/sessions/${sid}/end`, { completed }),
  history: (id) => req('GET', `/users/${id}/history`),
}
