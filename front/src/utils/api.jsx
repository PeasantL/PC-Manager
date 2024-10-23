export function fetchHostname() {
  fetch(process.env.REACT_APP_BACKEND_URL + '/system/hostname')
    .then(response => response.json())
    .then(data => console.log('Hostname:', data.data.hostname))
    .catch(error => console.error('Error:', error));
}

export function runScript(scriptName) {
  fetch(process.env.REACT_APP_BACKEND_URL + '/scripts/run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ script: scriptName })
  })
  .then(response => response.json())
  .then(data => console.log('Message:', data.message || data))
  .catch(error => console.error('Error:', error));
}

export function shutDownDesktop() {
  fetch(process.env.REACT_APP_BACKEND_URL + '/system/shutdown', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ value: 'ValidData' })
  })
  .then(response => response.json())
  .then(data => console.log('Message:', data.message || data))
  .catch(error => console.error('Error:', error));
}

export function startDesktop() {
  fetch(process.env.REACT_APP_BACKEND_URL + '/system/start-desktop', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ value: 'ValidData' })
  })
  .then(response => response.json())
  .then(data => console.log('Message:', data.message || data))
  .catch(error => console.error('Error:', error));
}

export function fetchVramUsage() {
  return fetch(process.env.REACT_APP_BACKEND_URL + '/system/vram-usage')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('VRAM Usage:', data);
      return data; // Return the data here
    })
    .catch(error => {
      console.error('Error fetching VRAM usage:', error);
      throw error; // Rethrow the error to handle it in the component
    });
}