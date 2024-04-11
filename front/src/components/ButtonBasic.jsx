import React from 'react'
import Button from 'react-bootstrap/Button'

export default function ButtonBasic({ text, onClick }) {
  return (
    <Button variant="primary" onClick={onClick}>
      {text}
    </Button>
  )
}
