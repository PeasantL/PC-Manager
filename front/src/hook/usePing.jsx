import { useEffect, useState } from 'react'

export default function usePing(url) {
  const [data, setData] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url)
        const result = await response.json()

        if (result['detail'] === null) {
          setData('Checking Connection')
        } else if (result['detail'] === 1) {
          setData('Online')
        } else if (result['detail'] === 0) {
          setData('Offline')
        }
      } catch (error) {
        //console.error('Error fetching data:', error);
      }
    }

    fetchData() // Fetch immediately on component mount

    const intervalId = setInterval(fetchData, 2000) // Fetch every two second

    return () => clearInterval(intervalId) // Cleanup on component unmount
  }, [url]) // Dependency array with URL, so if the URL changes, the effect will re-run

  return data
}
