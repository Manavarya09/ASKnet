// API functions for ASK-Net backend

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function submitQuery(queryText, userId = "web-user") {
  const response = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      query_text: queryText,
    }),
  })
  
  if (!response.ok) {
    throw new Error(`Failed to submit query: ${response.statusText}`)
  }
  
  return response.json()
}

export async function getTaskStatus(taskId) {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`)
  
  if (!response.ok) {
    throw new Error(`Failed to get task status: ${response.statusText}`)
  }
  
  return response.json()
}

export async function submitFeedback(taskId, rating, comments = "") {
  const response = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      task_id: taskId,
      rating,
      comments,
    }),
  })
  
  if (!response.ok) {
    throw new Error(`Failed to submit feedback: ${response.statusText}`)
  }
  
  return response.json()
}

export async function getAgentMemory(agentName) {
  const response = await fetch(`${API_BASE}/memory/${agentName}`)
  
  if (!response.ok) {
    throw new Error(`Failed to get agent memory: ${response.statusText}`)
  }
  
  return response.json()
}

export async function listAgents() {
  const response = await fetch(`${API_BASE}/agents`)
  
  if (!response.ok) {
    throw new Error(`Failed to list agents: ${response.statusText}`)
  }
  
  return response.json()
}

export async function getLearningAnalytics() {
  const response = await fetch(`${API_BASE}/learning/analytics`)
  
  if (!response.ok) {
    throw new Error(`Failed to get learning analytics: ${response.statusText}`)
  }
  
  return response.json()
}