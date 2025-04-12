import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      // Fetch data from the FastAPI backend
      const response = await axios.get('http://127.0.0.1:8000/google-sheets-data');
      setData(response.data.rows || []);
      setLoading(false);
    } catch (err) {
      setError('Error fetching data from the backend.');
      setLoading(false);
    }
  };

  // Fetch data when component mounts and then every 30 seconds (optional)
  useEffect(() => {
    fetchData();  // Initial fetch

    // Poll every 30 seconds (optional)
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);  // Clean up interval on component unmount
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <h1>Google Sheets Data (B87 to E92)</h1>
      <table border="1">
        <thead>
          <tr>
            {data[0] && data[0].data.map((_, index) => (
              <th key={index}>{data[0].data[index]}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(1).map((row, index) => (
            <tr key={index}>
              {row.data.map((cell, idx) => (
                <td key={idx}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;
