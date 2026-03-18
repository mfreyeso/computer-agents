import React from 'react'
import SidebarList from './components/SidebarList'
import VncViewer from './components/VncViewer'
import ChatPanel from './components/ChatPanel'

function App() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gray-950 text-slate-200">
      
      {/* Left Sidebar Pane - Navigation & History */}
      <SidebarList />

      {/* Middle Pane - Live VNC Viewer */}
      <VncViewer />

      {/* Right Pane - Real-Time Chat Feed */}
      <ChatPanel />
      
    </div>
  )
}

export default App
