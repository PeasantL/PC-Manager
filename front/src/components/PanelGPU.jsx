import React, { useEffect, useState } from 'react';
import { Container, Card, Alert } from 'react-bootstrap';
import RadioBasic from './RadioBasic';
import ButtonBasic from './ButtonBasic';
import { fetchVramUsage } from '../utils/api';
import './Panel.component.css';

export default function PanelGPU() {
  const [vramUsage, setVramUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadVramUsage = () => {
    setLoading(true);
    setError(null);

    fetchVramUsage()
      .then(data => {
        setVramUsage(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadVramUsage();
  }, []);

  return (
    <Container className="panel">
      <Card>
        <Card.Header>GPU Power Settings</Card.Header>
        <Card.Body>
          <div className="d-grid gap-2">
            <RadioBasic />
          </div>

          {/* Refresh button using ButtonBasic */}
          <ButtonBasic 
            text={loading ? 'Refreshing...' : 'Refresh VRAM'}
            onClick={loadVramUsage}
          />

          {/* Display VRAM usage or error message */}
          {error ? (
            <Alert variant="danger" className="mt-3">
              Error fetching VRAM usage: {error.message}
            </Alert>
          ) : (
            vramUsage && (
              <div className="mt-3">
                <p><strong>Used VRAM:</strong> {vramUsage.used_vram} MB</p>
                <p><strong>Total VRAM:</strong> {vramUsage.total_vram} MB</p>
              </div>
            )
          )}
        </Card.Body>
      </Card>
    </Container>
  );
}
