import React, { useState, useRef, useEffect } from 'react';
import { useSessionStore } from '../store/sessionStore';
import { useAgentSocket } from '../hooks/useAgentSocket';
import { Send, TerminalSquare, User, Bot, AlertTriangle, MonitorPlay } from 'lucide-react';

export default function ChatPanel() {
  const currentSessionId = useSessionStore(state => state.currentSessionId);
  const sessionState = useSessionStore(state => state.sessionState);
  const chatHistory = useSessionStore(state => state.chatHistory);
  const [inputText, setInputText] = useState('');
  const endOfMessagesRef = useRef(null);

  // Bind WebSockets
  const { submitPrompt } = useAgentSocket(currentSessionId);

  // Auto-scroll logic strictly mapped to chatHistory mutations
  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    submitPrompt(inputText);
    setInputText('');
  };

  // Guard loading UI
  if (!currentSessionId) {
    return (
      <div className="w-[450px] flex flex-col bg-slate-950 items-center justify-center border-l border-slate-800">
          <TerminalSquare size={48} className="text-slate-800 mb-4" />
          <p className="text-slate-500 text-sm font-mono tracking-wide">NO ACTIVE SESSION</p>
      </div>
    );
  }

  return (
    <div className="w-[450px] flex flex-col bg-slate-950 border-l border-slate-800 h-full">
      <div className="p-3 border-b border-slate-800 bg-slate-900 text-sm font-semibold flex items-center justify-between shadow-sm z-10 shrink-0">
        <span className="flex items-center gap-2 text-slate-200">
           <TerminalSquare size={16} className="text-blue-500" />
           Execution Loop
        </span>
        <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
           sessionState === 'running' ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-800' :
           sessionState === 'error' ? 'bg-red-900/50 text-red-400 border border-red-800' :
           'bg-slate-800 text-slate-400 border border-slate-700'
        }`}>
          {sessionState}
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 relative">
         {!chatHistory.length && (
            <div className="absolute inset-0 flex flex-col items-center justify-center opacity-30 text-slate-500">
              <Bot size={55} className="mb-4 text-blue-500" />
               <p className="text-sm">Agent is waiting for instructions</p>
            </div>
         )}
         
         {chatHistory.map((msg, index) => {
            // Unmarshal block structures generic or strictly formatted
            const role = msg.role || (msg.author === 'user' ? 'user' : 'agent');
            const type = msg.chunk_type || 'text';
            let text = msg.content;
            if (Array.isArray(text)) {
               text = text.map(block => {
                 if (block.type === 'text') return block.text;
                 if (block.type === 'tool_use') return `[Tool Use: ${block.name}]\nInput: ${JSON.stringify(block.input, null, 2)}`;
                 if (block.type === 'tool_result') {
                   const hasImage = Array.isArray(block.content) && block.content.some(c => c.type === 'image');
                   return `[Tool Result] ${hasImage ? '(includes screenshot)' : ''}`;
                 }
                 return JSON.stringify(block);
               }).join('\n\n');
            } else if (typeof text === 'object' && text !== null) {
               text = JSON.stringify(text, null, 2);
            }
            if (role === 'user') {
               return (
                 <div key={index} className="bg-slate-800 rounded p-3 text-sm border-l-2 border-blue-500 shadow drop-shadow-sm ml-6">
                   <span className="text-blue-400 font-semibold mb-1 mt-0 flex items-center gap-1.5"><User size={14}/> User</span>
                   <p className="text-slate-200 whitespace-pre-wrap">{text}</p>
                 </div>
               );
            }

            if (type === 'image') {
              return (
                 <div key={index} className="bg-slate-900 border border-slate-800 rounded p-2 mr-6 flex items-center justify-center overflow-hidden">
                   <img src={`data:image/png;base64,${text}`} alt="vnc screen" className="max-w-full rounded h-auto max-h-48 border border-slate-700 shadow-xl opacity-90 transition-opacity hover:opacity-100" />
                 </div>
              );
            }

            if (role === 'tool' || type === 'start') {
               return (
                 <div key={index} className="bg-amber-950/20 border border-amber-900/50 rounded p-3 text-xs font-mono mr-6">
                   <span className="text-amber-500 font-bold mb-1 flex items-center gap-1.5"><MonitorPlay size={12}/> Tool Execution</span>
                   <p className="text-slate-400 opacity-80 break-words">{text}</p>
                 </div>
               );
            }

            // Fallback Agent Text/Thoughts
            return (
               <div key={index} className="bg-emerald-950/20 border border-emerald-900/40 rounded p-3 text-sm mr-6">
                 <span className="text-emerald-500 font-semibold mb-1 flex items-center gap-1.5"><Bot size={14}/> Agent Thought</span>
                 <p className="text-slate-300 opacity-90 leading-relaxed font-sans">{text}</p>
               </div>
            );
         })}
         
         {/* Invisible div forces smooth auto-scroll to structural bottom boundary */}
         <div ref={endOfMessagesRef} className="h-4" />
      </div>

      <div className="p-3 border-t border-slate-800 bg-slate-900 shrink-0">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input 
            type="text" 
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={sessionState !== 'running' && sessionState !== 'completed'} // Block inputs until WS clears or binds
            placeholder={sessionState === 'error' ? "Connection Lost..." : "Instruct the agent..."} 
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm pr-12 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50 transition-all text-slate-200 disabled:opacity-50 placeholder-slate-500 shadow-inner"
          />
          <button 
             type="submit" 
             disabled={!inputText.trim() || sessionState === 'error'}
             className="absolute right-2 p-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-md transition-all active:scale-95"
          >
            <Send size={16} />
          </button>
        </form>
        {sessionState === 'running' && (
           <p className="text-[10px] text-slate-500 mt-2 text-center items-center flex justify-center gap-1 font-mono tracking-wider">
             <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
             LIVE AGENT LOOP ACTIVE
           </p>
        )}
      </div>
    </div>
  );
}
