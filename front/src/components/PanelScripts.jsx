import React from "react";
import { useEffect, useState } from "react";
import { Container , Card } from 'react-bootstrap';
import ButtonBasic from "./ButtonBasic";
import './Panel.component.css'

export default function PanelScripts() {

    const [data, setData] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://peasant.local/retrive_misc_script');
                const result = await response.json();
                setData(result);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        fetchData();
    }, []);

    return(
    <Container className="panel">
        <Card>
            <Card.Header>Misc Scripts</Card.Header>
            <Card.Body>
                <div className="d-grid gap-2">
                   {data && Object.keys(data).map((key, index) => (
                        <ButtonBasic text={key} />
                   ))}
                </div>
            </Card.Body>
        </Card>
    </Container>
    );
}