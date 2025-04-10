import React, { useEffect, useState } from 'react';

const DesiredOutputTable = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/spreadsheet")
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch spreadsheet");
        }
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;
  if (!data) return <p>Loading...</p>;

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2>📊 Desired Output Configuration</h2>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Parameter</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data).map(([key, value]) => (
            <tr key={key}>
              <td><strong>{key}</strong></td>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DesiredOutputTable;
