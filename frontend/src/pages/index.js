import { useEffect, useState } from 'react';
import api from '@/utils/api';

export default function HomePage() {
  const [poems, setPoems] = useState(null);

  useEffect(() => {
    const fetchPoems = async () => {
      try {
        const response = await api.get('/poems');
        setPoems(response.data);
      } catch (error) {
        console.error('ouch! Failed to fetch poems:', error.response?.data || error.message);
      }
    };
    fetchPoems();
  }, []);

  return (
    <div>
      <h1>...just some (yummy) poems here, <br></br> 
      nothing more, <br></br>
      nothing less.</h1>
      {poems ? <pre>{JSON.stringify(poems, null, 2)}</pre> : <p>Loading...</p>}
    </div>
  );
}
