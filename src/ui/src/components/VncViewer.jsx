import React, { useRef, useEffect, useState } from 'react';
import RFB from '@novnc/novnc/lib/rfb';
import { useSessionStore } from '../store/sessionStore';
import { MonitorPlay, MonitorOff, HelpCircle } from 'lucide-react';

export default function VncViewer() {
  const currentSessionId = useSessionStore(state => state.currentSessionId);
  const currentVncHost = useSessionStore(state => state.currentVncHost);
  const containerRef = useRef(null);
  const rfbRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [retryCount, setRetryCount] = useState(0);

  // Reset retries when session changes
  useEffect(() => {
    setRetryCount(0);
  }, [currentSessionId]);

  useEffect(() => {
    if (rfbRef.current) {
      rfbRef.current.disconnect();
      rfbRef.current = null;
    }

    if (!currentSessionId || !currentVncHost || !containerRef.current) {
      setConnectionStatus('disconnected');
      return;
    }

    let isEffectActive = true;
    let reconnectTimeout = null;

    setConnectionStatus('connecting');

    const vncUrl = `ws://${currentVncHost}/`;
    console.log(`Connecting to VNC at: ${vncUrl} (Attempt: ${retryCount})`);
    
    try {
      // Robust constructor check for minified/CJS interop environments
      const RFBConstructor = (RFB && RFB.default) ? RFB.default : RFB;
      
      const vncInstance = new RFBConstructor(containerRef.current, vncUrl, {
        credentials: { password: '' },
      });

      vncInstance.scaleViewport = true;
      vncInstance.resizeSession = false;

      vncInstance.addEventListener('connect', () => {
        if (!isEffectActive) return;
        setConnectionStatus('connected');
        setRetryCount(0); // reset retries upon solid connection
      });

      vncInstance.addEventListener('disconnect', () => {
        if (!isEffectActive) return;
        setConnectionStatus('disconnected');
        // Retry connection roughly every ~2 seconds for up to 30 attempts given container start delays
        if (retryCount < 30) {
          reconnectTimeout = setTimeout(() => {
            if (isEffectActive) setRetryCount(rc => rc + 1);
          }, 2000);
        }
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
        isEffectActive = false;
        if (reconnectTimeout) clearTimeout(reconnectTimeout);
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
      // Try again even if the constructor throws due to detached DOM states
      if (retryCount < 30) {
         reconnectTimeout = setTimeout(() => setRetryCount(rc => rc + 1), 2000);
      } else {
         setConnectionStatus('disconnected');
      }
    }
  }, [currentSessionId, currentVncHost, retryCount]);

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
      
      <div className="flex-1 w-full h-full flex items-center justify-center pt-10 overflow-hidden relative group bg-zinc-950">
        {/* Dedicated container strictly for noVNC so React DOM updates do not clash with raw canvas injection */}
        <div 
           ref={containerRef} 
           className="absolute inset-0 z-0" 
           tabIndex="-1" 
        />
        
        {/* React managed overlay layered above the VNC safely */}
        {connectionStatus === 'disconnected' && (
           <div className="z-10 absolute inset-0 pointer-events-none flex flex-col items-center justify-center text-slate-600 space-y-4">
              <MonitorOff size={48} className="opacity-50" />
              <p className="text-sm font-mono tracking-wider">NO ACTIVE CONNECTION</p>
              {!currentSessionId && (
                <p className="text-xs text-slate-500 flex items-center gap-1 border border-slate-700/50 bg-slate-800/30 px-3 py-1.5 rounded-full pointer-events-auto">
                  <HelpCircle size={12}/> Please select or start a session on the left
                </p>
              )}
           </div>
        )}
      </div>
    </div>
  );
}
