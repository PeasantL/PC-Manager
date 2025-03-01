import React, { useEffect, useState } from 'react'
import PanelPowerControls from './PanelPowerControls'
import PanelScripts from './PanelScripts'
import PanelGPU from './PanelGPU'
import PanelLinks from './PanelLinks'
import { Card, Row } from 'react-bootstrap'
import useHealthCheck from '../hook/useHealthCheck'

export default function FramePC() {
  const [hostname, setHostname] = useState('PC')
  const [os, setOs] = useState(null) // State for OS info
  const status = useHealthCheck('/health')

  useEffect(() => {
    // Fetch hostname when the component mounts
    fetch('/system/hostname')
      .then((response) => response.json())
      .then((data) => setHostname(data.data.hostname))
      .catch((error) => console.error('Error fetching hostname:', error))

    // Fetch OS info when the component mounts
    fetch('/system/os')
      .then((response) => response.json())
      .then((data) => setOs(data.os))
      .catch((error) => console.error('Error fetching OS info:', error))
  }, [])

  return (
    <Card>
      <Card.Header>{hostname}</Card.Header>
      <Card.Body>
        {status === 1 ? (
          <Card.Title>Status: Online</Card.Title>
        ) : (
          <Card.Title>Status: Offline</Card.Title>
        )}
        <Row>
          <PanelPowerControls />
        </Row>
        {status === 1 && os === 'Linux' && (
          <>
            <Row>
              <PanelScripts />
            </Row>
            <Row>
              <PanelLinks />
            </Row>
            <Row>
              <PanelGPU />
            </Row>
          </>
        )}
      </Card.Body>
    </Card>
  )
}
