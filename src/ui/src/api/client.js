const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const fetchSessions = async () => {
  const res = await fetch(`${API_BASE_URL}/sessions`)
  if (!res.ok) throw new Error("Failed to load sessions")
  return res.json()
}

export const createSession = async () => {
  const res = await fetch(`${API_BASE_URL}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ user_id: 'default' })
  })
  if (!res.ok) throw new Error("Failed to create new session")
  return res.json()
}

export const fetchSessionHistory = async (sessionId) => {
  const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}/history`)
  if (!res.ok) throw new Error(`Failed to load history for ${sessionId}`)
  return res.json()
}
