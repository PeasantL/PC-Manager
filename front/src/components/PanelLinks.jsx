import React, { useEffect, useState } from 'react'
import {
  Container,
  Card,
  Accordion,
  Form,
  ProgressBar,
  Row,
  Col,
} from 'react-bootstrap'
import ButtonBasic from './ButtonBasic'
import './Panel.component.css'

export default function PanelLinks() {
  // For model download
  const [huggingFaceModel, setHuggingFaceModel] = useState('')
  const [specificFile, setSpecificFile] = useState('') // NEW: track a specific file
  const [downloadProgress, setDownloadProgress] = useState(0)
  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState(null)

  // For model selection
  const [models, setModels] = useState([])
  const [selectedModel, setSelectedModel] = useState('')
  const [contextLength, setContextLength] = useState(8192)

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

  // Start the download
  const startDownload = () => {
    const jobId = Date.now().toString() // unique identifier for this download job
    setDownloadProgress(0)
    setDownloading(true)
    setDownloadError(null)

    fetch('/koboldcpp/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        hf_model: huggingFaceModel,
        branch: 'main',
        job_id: jobId,
        specific_file: specificFile, // <-- Include the specific_file parameter
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status} - Download start failed`)
        }
        return res.json()
      })
      .then(() => {
        pollProgress(jobId)
      })
      .catch((err) => {
        console.error('Error starting download:', err)
        setDownloadError(err.message)
        setDownloading(false)
      })
  }

  // Poll the download progress
  const pollProgress = (jobId) => {
    const intervalId = setInterval(() => {
      fetch(`/koboldcpp/download/progress/${jobId}`)
        .then((res) => {
          if (!res.ok) {
            throw new Error(`HTTP ${res.status} - Can't get progress`)
          }
          return res.json()
        })
        .then((data) => {
          // data might look like:
          // { filename: "...", progress_ratio: 0.45, done: false, error: null }

          if (data.error) {
            setDownloadError(data.error)
            setDownloading(false)
            clearInterval(intervalId)
            return
          }

          const percentage = Math.round((data.progress_ratio || 0) * 100)
          setDownloadProgress(percentage)

          if (data.done) {
            setDownloading(false)
            clearInterval(intervalId)
          }
        })
        .catch((err) => {
          console.error('Error polling progress:', err)
          setDownloadError(err.message)
          setDownloading(false)
          clearInterval(intervalId)
        })
    }, 2000)
  }

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
            {/* -------------- Model Download Section -------------- */}
            <Accordion>
              <Accordion.Header>Model Download</Accordion.Header>
              <Accordion.Body>
                <Row>
                  <Form>
                    <Form.Group className="mb-3">
                      <Form.Label>Hugging Face Address</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF"
                        value={huggingFaceModel}
                        onChange={(e) => setHuggingFaceModel(e.target.value)}
                      />
                    </Form.Group>

                    {/* NEW: Specific file text input */}
                    <Form.Group className="mb-3">
                      <Form.Label>Specific File (optional)</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="DeepSeek-R1-Distill-Qwen-1.5B-Q2_K.gguf"
                        value={specificFile}
                        onChange={(e) => setSpecificFile(e.target.value)}
                      />
                    </Form.Group>
                  </Form>
                </Row>
                <Row className="mt-2">
                  <Col>
                    <ButtonBasic text="Download" onClick={startDownload} />
                  </Col>
                  <Col>
                    <ProgressBar
                      now={downloadProgress}
                      label={`${downloadProgress}%`}
                    />
                  </Col>
                </Row>
                {downloading && <div>Downloading...</div>}
                {downloadError && (
                  <div style={{ color: 'red' }}>Error: {downloadError}</div>
                )}
              </Accordion.Body>
            </Accordion>

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

                {/* Three radio buttons for context length */}
                <Form className="mt-3">
                  <Form.Group>
                    <Form.Label>Context Length</Form.Label>
                    <div>
                      <Form.Check
                        type="radio"
                        name="contextLength"
                        label="8192"
                        value="8192"
                        checked={contextLength === 8192}
                        onChange={() => setContextLength(8192)}
                      />
                      <Form.Check
                        type="radio"
                        name="contextLength"
                        label="15360"
                        value="15360"
                        checked={contextLength === 15360}
                        onChange={() => setContextLength(15360)}
                      />
                      <Form.Check
                        type="radio"
                        name="contextLength"
                        label="20480"
                        value="20480"
                        checked={contextLength === 20480}
                        onChange={() => setContextLength(20480)}
                      />
                    </div>
                  </Form.Group>
                </Form>

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
