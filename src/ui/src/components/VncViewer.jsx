import React, { useRef, useEffect, useState } from 'react';
import RFB from '@novnc/novnc/lib/rfb';
import { useSessionStore } from '../store/sessionStore';
import { MonitorPlay, MonitorOff, HelpCircle } from 'lucide-react';

export default function VncViewer() {
  const currentSessionId = useSessionStore(state => state.currentSessionId);
  const containerRef = useRef(null);
  const rfbRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  useEffect(() => {
    if (rfbRef.current) {
      rfbRef.current.disconnect();
      rfbRef.current = null;
    }

    if (!currentSessionId || !containerRef.current) {
      setConnectionStatus('disconnected');
      return;
    }

    setConnectionStatus('connecting');

    // Useport 6080 for websockify as per docker-compose
    const vncUrl = `ws://${window.location.hostname}:6080/`;
    console.log('Connecting to VNC at:', vncUrl);
    
    try {
      // Robust constructor check for minified/CJS interop environments
      const RFBConstructor = (RFB && RFB.default) ? RFB.default : RFB;
      
      const vncInstance = new RFBConstructor(containerRef.current, vncUrl, {
        credentials: { password: '' },
      });

      vncInstance.scaleViewport = true;
      vncInstance.resizeSession = false;

      vncInstance.addEventListener('connect', () => {
        setConnectionStatus('connected');
      });

      vncInstance.addEventListener('disconnect', () => {
        setConnectionStatus('disconnected');
      });

      rfbRef.current = vncInstance;
      
      const resizeObserver = new ResizeObserver(() => {
        if (rfbRef.current && rfbRef.current._display) {
          rfbRef.current._display.autoscale(
            containerRef.current.clientWidth,
            containerRef.current.clientHeight
          );
        }
      });
      resizeObserver.observe(containerRef.current);

      return () => {
        resizeObserver.disconnect();
        if (rfbRef.current) {
          try {
            // Release any pending display frames before disconnect
            if (rfbRef.current._display) {
              rfbRef.current._display.clear();
            }
          } catch (_) { /* ignore cleanup errors */ }
          rfbRef.current.disconnect();
          rfbRef.current = null;
        }
        // Remove any orphaned canvas elements left by noVNC to prevent VideoFrame leaks
        if (containerRef.current) {
          containerRef.current.querySelectorAll('canvas').forEach(c => c.remove());
        }
      };
    } catch (err) {
      console.error('VNC initialization error:', err);
      setConnectionStatus('disconnected');
    }
  }, [currentSessionId]);

  return (
    <div className="flex-1 flex flex-col border-r border-slate-800 bg-black relative">
      <div className="absolute top-0 w-full p-2 bg-slate-900/80 backdrop-blur z-10 flex items-center justify-between border-b border-slate-800">
        <span className="font-mono text-xs text-slate-300 flex items-center gap-2">
          <MonitorPlay size={14} className="text-blue-500" /> VNC Desktop Stream
        </span>
        <span className="flex items-center gap-2 transition-all">
          {connectionStatus === 'connected' && (
             <><div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
             <span className="text-xs text-emerald-500 font-semibold">Live</span></>
          )}
          {connectionStatus === 'connecting' && (
             <><div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
             <span className="text-xs text-amber-500 font-semibold">Connecting...</span></>
          )}
          {connectionStatus === 'disconnected' && (
             <><div className="w-2 h-2 rounded-full bg-slate-600"></div>
             <span className="text-xs text-slate-500 font-semibold">Offline</span></>
          )}
        </span>
      </div>
      
      <div className="flex-1 w-full h-full flex items-center justify-center pt-10 overflow-hidden relative group">
        <div 
           ref={containerRef} 
           className="w-full h-full flex items-center justify-center outline-none bg-zinc-950" 
           tabIndex="-1" 
        >
          {connectionStatus === 'disconnected' && (
             <div className="flex flex-col items-center justify-center text-slate-600 space-y-4">
                <MonitorOff size={48} className="opacity-50" />
                <p className="text-sm font-mono tracking-wider">NO ACTIVE CONNECTION</p>
                {!currentSessionId && (
                  <p className="text-xs text-slate-500 flex items-center gap-1 border border-slate-700/50 bg-slate-800/30 px-3 py-1.5 rounded-full">
                    <HelpCircle size={12}/> Please select or start a session on the left
                  </p>
                )}
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
