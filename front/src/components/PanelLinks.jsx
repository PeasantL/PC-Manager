import React, { useEffect, useState } from 'react'
import {
  Container,
  Card,
  Accordion,
  Form,
  Row,
  Col,
} from 'react-bootstrap'
import ButtonBasic from './ButtonBasic'
import './Panel.component.css'

export default function PanelLinks() {
  // For model selection
  const [models, setModels] = useState([])
  const [selectedModel, setSelectedModel] = useState('')
  const [contextLength, setContextLength] = useState(16384)
  const [kvCacheQuant, setKvCacheQuant] = useState(0) // Default to FP16 (0)

  // Example: fetch available .gguf models on mount
  useEffect(() => {
    fetch('/koboldcpp/models')
      .then((res) => res.json())
      .then((data) => {
        if (data?.models) {
          setModels(data.models)
          if (data.models.length > 0) {
            setSelectedModel(data.models[0])
          }
        }
      })
      .catch((err) => console.error('Failed to load models:', err))
  }, [])

  // Model Select radio group handling
  const handleModelChange = (modelPath) => {
    setSelectedModel(modelPath)
  }

  const handleSetParameters = () => {
    fetch('/koboldcpp/set-parameters', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_path: selectedModel,
        context_length: contextLength,
        kv_cache_quant: kvCacheQuant,
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to set parameters')
        }
        return res.json()
      })
      .then((data) => {
        console.log('Parameters set:', data)
      })
      .catch((error) => {
        console.error('Error setting parameters:', error)
      })
  }

  // A helper to strip the .gguf extension for display
  const getLabel = (fullPath) => {
    const filename = fullPath.split('/').pop()
    return filename.replace(/\.gguf$/, '')
  }

  return (
    <Container className="panel">
      <Card>
        <Card.Header>Model Control</Card.Header>
        <Card.Body>
          <div className="d-grid gap-2">
            {/* -------------- Model Select Section -------------- */}
            <Accordion>
              <Accordion.Header>Model Select</Accordion.Header>
              <Accordion.Body>
                <Form>
                  {models.map((modelPath, index) => (
                    <Form.Check
                      key={index}
                      type="radio"
                      name="ggufModel"
                      label={getLabel(modelPath)}
                      id={`ggufModel-${index}`}
                      value={modelPath}
                      checked={selectedModel === modelPath}
                      onChange={() => handleModelChange(modelPath)}
                      className="mb-2"
                    />
                  ))}
                </Form>

                {/* Context Length Slider */}
                <Form.Group className="mt-3">
                  <Form.Label>Context Length: {contextLength}</Form.Label>
                  <Form.Range
                    min={8192}
                    max={32768}
                    step={1024}
                    value={contextLength}
                    onChange={(e) => setContextLength(Number(e.target.value))}
                  />
                </Form.Group>

                {/* KV Cache Quant Radio */}
                <Form.Group className="mt-3">
                  <Form.Label>KV Cache Quant</Form.Label>
                  <div>
                    <Form.Check
                      type="radio"
                      name="kvCacheQuant"
                      label="FP16"
                      value={0}
                      checked={kvCacheQuant === 0}
                      onChange={() => setKvCacheQuant(0)}
                    />
                    <Form.Check
                      type="radio"
                      name="kvCacheQuant"
                      label="Q8"
                      value={1}
                      checked={kvCacheQuant === 1}
                      onChange={() => setKvCacheQuant(1)}
                    />
                    <Form.Check
                      type="radio"
                      name="kvCacheQuant"
                      label="Q4"
                      value={2}
                      checked={kvCacheQuant === 2}
                      onChange={() => setKvCacheQuant(2)}
                    />
                  </div>
                </Form.Group>

                <ButtonBasic
                  text="Set Parameters"
                  className="mt-3"
                  onClick={handleSetParameters}
                />
              </Accordion.Body>
            </Accordion>
          </div>
        </Card.Body>
      </Card>
    </Container>
  )
}
