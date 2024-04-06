import React from "react";
import { Container , Card } from 'react-bootstrap';
import ButtonBasic from "./ButtonBasic";
import './Panel.component.css'

export default function PanelScripts() {

    return(
    <Container className="panel">
        <Card>
            <Card.Header>Misc Scripts</Card.Header>
            <Card.Body>
                <div className="d-grid gap-2">
                    <ButtonBasic text="Run LLM Server + SillyTavern" disabled />
                </div>
            </Card.Body>
        </Card>
    </Container>
    );
}