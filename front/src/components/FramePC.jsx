import React from 'react'
import PanelPowerControls from './PanelPowerControls'
import PanelScripts from './PanelScripts'
import PanelGPU from './PanelGPU'
import { Card, Row } from 'react-bootstrap'

export default function FramePC() {
  return (
    <Card>
      <Card.Header>PC</Card.Header>
      <Card.Body>
        <Row>
          <PanelPowerControls />
        </Row>
        <Row>
          <PanelScripts />
        </Row>
        <Row>
          <PanelGPU />
        </Row>
      </Card.Body>
    </Card>
  )
}
