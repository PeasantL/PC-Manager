import React from 'react'
import { Container, Card } from 'react-bootstrap'
import ButtonBasic from './ButtonBasic'
import { shutDownDesktop, startDesktop } from '../utils/api'
import './Panel.component.css'

export default function PanelPowerControls() {
  return (
    <Container className="panel">
      <Card>
        <Card.Header>Power Controls</Card.Header>
        <Card.Body>
          <div className="d-grid gap-2">
            <ButtonBasic text="Shut Down Desktop" onClick={shutDownDesktop} />
            <ButtonBasic text="Start Desktop" onClick={startDesktop} />
          </div>
        </Card.Body>
      </Card>
    </Container>
  )
}
