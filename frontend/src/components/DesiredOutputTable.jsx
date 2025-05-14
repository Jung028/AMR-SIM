import React, { useEffect, useState } from 'react';

const DesiredOutputTable = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/google-sheets-data');
      if (!response.ok) {
        throw new Error('Failed to fetch data from the backend.');
      }
      const result = await response.json();
      setData(result.rows || []);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 300000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2>📊 Desired Output Configuration</h2>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            {data[0]?.data.map((col, idx) => (
              <th key={idx}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(1).map((row, idx) => (
            <tr key={idx}>
              {row.data.map((cell, i) => (
                <td key={i}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DesiredOutputTable;
