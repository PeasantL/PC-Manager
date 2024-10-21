export function fetchMessage() {
  fetch(process.env.REACT_APP_BACKEND_URL + '/test')
    .then(response => response.json())
    .then(data => console.log('Message:', data.message))
    .catch(error => console.error('Error:', error));
}

export function fetchHostname() {
  fetch(process.env.REACT_APP_BACKEND_URL + '/get_hostname')
    .then(response => response.json())
    .then(data => console.log('Hostname:', data.hostname))
    .catch(error => console.error('Error:', error));
}


export function runScript(scriptName) {
  fetch(process.env.REACT_APP_BACKEND_URL + '/run_misc_script', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ value: scriptName })
  })
  .then(response => response.json())
  .then(data => console.log('Message:', data.message))
  .catch(error => console.error('Error:', error));
}

export function shutDownDesktop() {
  fetch(process.env.REACT_APP_BACKEND_URL + '/shut_down_desktop', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ value: 'ValidData' })
  })
  .then(response => response.json())
  .then(data => console.log('Message:', data.message))
  .catch(error => console.error('Error:', error));
}

export function startDesktop() {
  fetch(process.env.REACT_APP_BACKEND_URL + '/start_desktop', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ value: 'ValidData' })
  })
  .then(response => response.json())
  .then(data => console.log('Message:', data.message))
  .catch(error => console.error('Error:', error));
}
