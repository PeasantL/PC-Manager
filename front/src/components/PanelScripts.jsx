import React, { useEffect, useState } from 'react';
import { Container, Card } from 'react-bootstrap';
import ButtonBasic from './ButtonBasic';
import { runScript } from '../utils/api';
import './Panel.component.css';

export default function PanelScripts() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          '/scripts'
        );
        const result = await response.json();
        setData(result.data); // Adjust to access the 'data' property
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, []);

  return (
    <Container className="panel">
      {data &&
        Object.keys(data).map((folder, index) => (
          <Card key={index} className="mb-3">
            <Card.Header>Scripts: {folder}</Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                {Array.isArray(data[folder]) ? (
                  data[folder].map((script, scriptIndex) => (
                    <ButtonBasic
                      text={script}
                      key={scriptIndex}
                      onClick={() => runScript(script)}
                    />
                  ))
                ) : (
                  <p>No scripts available for this folder.</p>
                )}
              </div>
            </Card.Body>
          </Card>
        ))}
    </Container>
  );
}
