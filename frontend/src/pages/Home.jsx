import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Home = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/google-sheets-data');
      setData(response.data.rows || []);
      setLoading(false);
    } catch (err) {
      setError('Error fetching data from the backend.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Google Sheets Data (B87 to E92)</h1>

      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <table border="1">
          <thead>
            <tr>
              {data[0]?.data.map((col, idx) => <th key={idx}>{col}</th>)}
            </tr>
          </thead>
          <tbody>
            {data.slice(1).map((row, idx) => (
              <tr key={idx}>
                {row.data.map((cell, i) => <td key={i}>{cell}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      )}


    </div>
  );
};

export default Home;
