export function fetchHostname() {
  fetch('/system/hostname')
    .then((response) => response.json())
    .then((data) => console.log('Hostname:', data.data.hostname))
    .catch((error) => console.error('Error:', error))
}

export function runScript(scriptName) {
  fetch('/scripts/run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ script: scriptName }),
  })
    .then((response) => response.json())
    .then((data) => console.log('Message:', data.message || data))
    .catch((error) => console.error('Error:', error))
}

export function shutDownDesktop() {
  fetch('/system/shutdown', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ script: 'ValidData' }),
  })
    .then((response) => response.json())
    .then((data) => console.log('Message:', data.message || data))
    .catch((error) => console.error('Error:', error))
}

export function startDesktop() {
  fetch('/system/start-desktop', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ script: 'ValidData' }),
  })
    .then((response) => response.json())
    .then((data) => console.log('Message:', data.message || data))
    .catch((error) => console.error('Error:', error))
}

export function fetchVramUsage() {
  return fetch('/system/vram-usage')
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      return response.json()
    })
    .then((data) => {
      console.log('VRAM Usage:', data)
      return data
    })
    .catch((error) => {
      console.error('Error fetching VRAM usage:', error)
      throw error
    })
}

export function fetchGgufModels() {
  // This endpoint returns: { "models": ["path/to/model1.gguf", "path/to/model2.gguf", ...] }
  return fetch('/koboldcpp/models')
    .then((response) => {
      if (!response.ok) {
        throw new Error('Failed to fetch models')
      }
      return response.json()
    })
    .then((data) => {
      // data.models is an array of paths
      return data.models
    })
    .catch((error) => {
      console.error('Error fetching GGUF models:', error)
      throw error
    })
}
