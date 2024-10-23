import React, { useEffect, useState } from 'react';
import PanelPowerControls from './PanelPowerControls';
import PanelScripts from './PanelScripts';
import PanelGPU from './PanelGPU';
import { Card, Row } from 'react-bootstrap';
import usePing from '../hook/usePing';

export default function FramePC() {
  const [hostname, setHostname] = useState('PC');
  const data = usePing(process.env.REACT_APP_BACKEND_URL + '/ping');

  useEffect(() => {
    // Fetch hostname when the component mounts
    fetch(process.env.REACT_APP_BACKEND_URL + '/get_hostname')
      .then(response => response.json())
      .then(data => setHostname(data.hostname))
      .catch(error => console.error('Error fetching hostname:', error));
  }, []);

  return (
    <Card>
      <Card.Header>{hostname}</Card.Header>
      <Card.Body>
        {data === 1 ? (
          <Card.Title>Status: Online</Card.Title>
        ) : (
          <Card.Title>Status: Offline</Card.Title>
        )}
        <Row>
          <PanelPowerControls />
        </Row>
        {data === 1 && (
          <>
            <Row>
              <PanelScripts />
            </Row>
            <Row>
              <PanelGPU />
            </Row>
          </>
        )}
      </Card.Body>
    </Card>
  );
}
