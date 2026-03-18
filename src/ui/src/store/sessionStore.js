import { create } from 'zustand'

export const useSessionStore = create((set, get) => ({
  currentSessionId: null,
  sessionState: 'idle', // 'idle' | 'running' | 'completed' | 'error'
  chatHistory: [],

  // Set the active session context
  setSession: (id) => set({ 
    currentSessionId: id,
    chatHistory: [], // Clear on jump
    sessionState: 'idle'
  }),

  // Append incoming chunks from HTTP or WebSockets
  appendMessage: (msg) => set((state) => ({
    chatHistory: [...state.chatHistory, msg]
  })),

  // Accumulate streaming text into the last agent message
  appendTextChunk: (text) => set((state) => {
    const history = [...state.chatHistory];
    const last = history[history.length - 1];
    if (last && last.role === 'agent' && last.chunk_type === 'text') {
      history[history.length - 1] = { ...last, content: last.content + text };
      return { chatHistory: history };
    }
    return {
      chatHistory: [...history, { role: 'agent', chunk_type: 'text', content: text }]
    };
  }),

  // Hydrate an entire array at once (used when loading historical sessions)
  setHistory: (messages) => set({
    chatHistory: messages
  }),

  updateSessionState: (status) => set({
    sessionState: status
  }),

  // Clean wipe
  clearSession: () => set({
    currentSessionId: null,
    chatHistory: [],
    sessionState: 'idle'
  })
}))
