export function fetchMessage() {
  fetch('http://peasant.local/test')
    .then(response => response.json())
    .then(data => console.log('Message:', data.message))
    .catch(error => console.error('Error:', error));
}

export function shutDownDesktop() {
  fetch('http://peasant.local/shut_down_desktop', {
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
  fetch('http://peasant.local/start_desktop', {
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
