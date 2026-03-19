import React, { useEffect, useState } from 'react';
import { useSessionStore } from '../store/sessionStore';
import { fetchSessions, createSession } from '../api/client';
import { Plus, ListTree } from 'lucide-react';
import { parseISO, formatDistanceToNow } from 'date-fns';

export default function SidebarList() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const currentSessionId = useSessionStore(state => state.currentSessionId);
  const setSession = useSessionStore(state => state.setSession);

  const loadSessions = async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleStartNewTask = async () => {
    try {
      setLoading(true);
      const newSession = await createSession();
      setSessions([newSession, ...sessions]);
      setSession(newSession.session_id, newSession.vnc_host);
    } catch (err) {
      console.error("Failed to start new session:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-64 border-r border-slate-800 flex flex-col h-full shrink-0">
      <div className="p-4 border-b border-slate-800">
        <button 
          onClick={handleStartNewTask}
          disabled={loading}
          className="w-full py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 transition-colors rounded font-semibold text-white shadow flex items-center justify-center gap-2"
        >
          <Plus size={18} />
          New Agent Task
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2">
        <div className="px-2 pb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-2">
          <ListTree size={14} /> session history
        </div>
        
        {loading && sessions.length === 0 ? (
          <div className="p-4 text-sm text-slate-400 text-center animate-pulse">Loading list...</div>
        ) : (
          <div className="space-y-1">
            {sessions.map(s => {
              const isActive = currentSessionId === s.session_id;
              // Format time nicely if creation exists
              const timeStr = s.created_at ? formatDistanceToNow(parseISO(s.created_at), { addSuffix: true }) : 'unknown time';
              
              return (
                <div 
                  key={s.session_id}
                  onClick={() => setSession(s.session_id, s.vnc_host)}
                  className={`text-sm p-3 border rounded cursor-pointer transition-all ${
                    isActive 
                      ? 'bg-blue-900/30 border-blue-700/50 text-blue-100 shadow-inner' 
                      : 'bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-800/50 text-slate-300'
                  }`}
                >
                  <div className="font-mono text-xs truncate opacity-80 mb-1">
                    {s.session_id.split('-')[0]}-...
                  </div>
                  <div className="flex items-center justify-between text-xs">
                     <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium uppercase ${s.status === 'RUNNING' ? 'bg-emerald-900/50 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                        {s.status}
                     </span>
                     <span className="text-slate-500">{timeStr}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
