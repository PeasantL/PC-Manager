import React from "react";
import { Container , Card } from 'react-bootstrap';
import RadioBasic from "./RadioBasic";
import './Panel.component.css'

export default function PanelGPU() {

    return(
    <Container className="panel">
        <Card>
            <Card.Header>GPU Power Settings</Card.Header>
            <Card.Body>
                <div className="d-grid gap-2">
                    <RadioBasic />
                </div>
            </Card.Body>
        </Card>
    </Container>
    );
}