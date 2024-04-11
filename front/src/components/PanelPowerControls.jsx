import React from 'react'
import { Container, Card } from 'react-bootstrap'
import ButtonBasic from './ButtonBasic'
import { fetchMessage, shutDownDesktop, startDesktop } from '../utils/api'
import usePing from '../hook/usePing'
import './Panel.component.css'

export default function PanelPowerControls() {
  const data = usePing(process.env.REACT_APP_BACKEND_URL + '/ping')

  return (
    <Container className="panel">
      <Card>
        <Card.Header>Power Controls</Card.Header>
        <Card.Body>
          <Card.Title>Computer Status: {data}</Card.Title>
          <div className="d-grid gap-2">
            <ButtonBasic text="Shut Down Desktop" onClick={shutDownDesktop} />
            <ButtonBasic text="Start Desktop" onClick={startDesktop} />
            <ButtonBasic text="Test" onClick={fetchMessage} />
          </div>
        </Card.Body>
      </Card>
    </Container>
  )
}
