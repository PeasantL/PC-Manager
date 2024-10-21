import React, { useEffect, useState } from 'react'
import { Container, Card } from 'react-bootstrap'
import ButtonBasic from './ButtonBasic'
import { runScript } from '../utils/api'
import './Panel.component.css'

export default function PanelScripts() {
  const [data, setData] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          process.env.REACT_APP_BACKEND_URL + '/retrieve_scripts',
        )
        const result = await response.json()
        setData(result)
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }
    fetchData()
  }, [])

  return (
    <Container className="panel">
      {data &&
        Object.keys(data).map((folder, index) => (
          <Card key={index} className="mb-3">
            <Card.Header>{folder}</Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                {data[folder].map((script, scriptIndex) => (
                  <ButtonBasic
                    text={script}
                    key={scriptIndex}
                    onClick={() => runScript(script)}
                  />
                ))}
              </div>
            </Card.Body>
          </Card>
        ))}
    </Container>
  )
}
