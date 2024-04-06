import React from 'react';
import PanelPowerControls from './components/PanelPowerControls';
import PanelScripts from './components/PanelScripts';
import PanelGPU from './components/PanelGPU';
import { Row } from 'react-bootstrap';
import './App.css';

function App() {
  return (

    <div className='mainContainer'>
      <Row>
        <PanelPowerControls />
      </Row>
      <Row>
        <PanelScripts />
      </Row>
      <Row>
        <PanelGPU />
      </Row>
    </div>
  );
}

export default App;
