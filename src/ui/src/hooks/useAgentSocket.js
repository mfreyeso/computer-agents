import { useEffect, useRef } from 'react';
import { useSessionStore } from '../store/sessionStore';
import { fetchSessionHistory } from '../api/client';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws/v1';

export function useAgentSocket(sessionId) {
  const wsRef = useRef(null);
  const appendMessage = useSessionStore(state => state.appendMessage);
  const appendTextChunk = useSessionStore(state => state.appendTextChunk);
  const setHistory = useSessionStore(state => state.setHistory);
  const updateSessionState = useSessionStore(state => state.updateSessionState);

  // Connection logic
  useEffect(() => {
    if (!sessionId) {
      if (wsRef.current) {
        wsRef.current.close();
      }
      return;
    }

    let isMounted = true;
    
    // First heavily hydrate
    const initSession = async () => {
      try {
        const history = await fetchSessionHistory(sessionId);
        if (!isMounted) return;
        setHistory(Array.isArray(history) ? history : []);
        updateSessionState('completed'); // Default historical state until ws active
      } catch (err) {
        console.error("Failed fetching history for session:", err);
      }

      if (!isMounted) return;

      // Boot websocket
      const wsUrl = `${WS_BASE_URL}/sessions/${sessionId}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        updateSessionState('running');
        console.log(`Connected WS strictly to ${sessionId}`);
      };

      ws.onmessage = (event) => {
        try {
          const chunk = JSON.parse(event.data);
          
          if (chunk.chunk_type === 'text') {
            appendTextChunk(chunk.payload);
          } else if (chunk.chunk_type === 'tool_execution_start') {
            appendMessage({
               role: 'tool',
               chunk_type: 'start',
               content: `Executing ${chunk.payload.tool}(${JSON.stringify(chunk.payload.input)})`
            });
          } else if (chunk.chunk_type === 'vnc_screenshot_result') {
            appendMessage({
               role: 'tool',
               chunk_type: 'image',
               content: chunk.payload.base64
            });
          }
        } catch (e) {
          console.warn("Failed translating chunk", e, event.data);
        }
      };

      ws.onclose = () => {
        updateSessionState('completed');
      };

      ws.onerror = (e) => {
        updateSessionState('error');
      };

      wsRef.current = ws;
    };

    initSession();

    return () => {
      isMounted = false;
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId, appendMessage, appendTextChunk, setHistory, updateSessionState]);

  // Command submission emitter
  const submitPrompt = (promptText) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Echo it visually immediately locally
      appendMessage({
        role: 'user',
        chunk_type: 'text',
        content: promptText
      });
      // Send upstream via payload expected by server 
      // (FastAPI parses raw string prompts in our minimal websocket mapping)
      wsRef.current.send(JSON.stringify({ type: 'user_prompt', text: promptText }));
    }
  };

  return { submitPrompt };
}
