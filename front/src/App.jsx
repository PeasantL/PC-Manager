import React from 'react'
import FramePC from './components/FramePC'
import FrameServer from './components/FrameServer'

import './App.css'

function App() {
  return (
    <>
      <div className="mainContainer">
        <FrameServer />
      </div>
      <div className="mainContainer">
        <FramePC />
      </div>
    </>
  )
}

export default App
