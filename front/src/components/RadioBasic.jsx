import React from 'react'
import Form from 'react-bootstrap/Form'

export default function RadioBasic() {
  return (
    <Form>
      <div key={`inline-radio`} className="mb-3">
        <Form.Check
          inline
          label="280W"
          name="group1"
          type={'radio'}
          id={`inline-radio-1`}
        />
        <Form.Check
          inline
          label="390W"
          name="group1"
          type={'radio'}
          id={`inline-radio-2`}
        />
      </div>
    </Form>
  )
}
