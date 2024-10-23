import { useEffect, useState } from 'react';

export default function useHealthCheck(url) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url);
        const result = await response.json();

        if (result['status'] === 'ok') {
          setStatus(1); // Online
        } else {
          setStatus(0); // Offline if not 'ok'
        }
      } catch (error) {
        setStatus(0); // Assume offline in case of error
      }
    };

    fetchData(); // Fetch immediately on component mount

    const intervalId = setInterval(fetchData, 5000); // Fetch every 5 seconds

    return () => clearInterval(intervalId); // Cleanup on component unmount
  }, [url]);

  return status;
}
