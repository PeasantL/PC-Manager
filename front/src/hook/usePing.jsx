import { useEffect, useState } from 'react'

export default function usePing(url) {
  const [status, setStatus] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url)
        const result = await response.json()

        if (result['detail'] === 1) {
          setStatus(1)
        } else if (result['detail'] === 0) {
          setStatus(0)
        }
      } catch (error) {
        // Handle error silently or log it if needed
      }
    }

    fetchData() // Fetch immediately on component mount

    const intervalId = setInterval(fetchData, 5000) // Fetch every two seconds

    return () => clearInterval(intervalId) // Cleanup on component unmount
  }, [url]) // Dependency array with URL, so if the URL changes, the effect will re-run

  return status
}
