import React, { useEffect, useState } from 'react';
import '../styles/PutawayTasksTable.css'; // Import your CSS file for styling

const PutawayTasksTable = ({ mapId }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from the FastAPI backend
  useEffect(() => {
    const fetchTasks = async () => {
      if (!mapId) return; // Wait until mapId is available
      try {
        const response = await fetch(`http://localhost:8000/task/putaway-tasks?map_id=${mapId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Fetched data:', data); // Debug log
        setTasks(data.tasks);
      } catch (err) {
        console.error('Fetch error:', err); // Debug log
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [mapId]); // Re-fetch tasks whenever mapId changes

  // Handle error case
  if (error) {
    return <div>Error: {error}</div>;
  }

  // Handle loading case
  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="putaway-tasks-table">
      <h3>Putaway Tasks</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Object ID</th>
              <th>Task ID</th>
              <th>Putaway Order Code</th>
              <th>Robot ID</th>
              <th>Station ID</th>
              <th>Map ID</th>
              <th>Shelf ID</th>
              <th>Level</th>
              <th>SKU ID</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.task_id}>
                <td>{task._id}</td>
                <td>{task.task_id}</td>
                <td>{task.putaway_order_code}</td>
                <td>{task.robot_id}</td>
                <td>{task.station_id}</td>
                <td>{task.map_id}</td>
                <td>{task.shelf_id}</td>
                <td>{task.level}</td>
                <td>{task.sku_id}</td>
                <td>{task.amount}</td>
                <td>{task.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PutawayTasksTable;
