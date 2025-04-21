import React, { useEffect, useState } from 'react';
import '../styles/PutawayTasksTable.css'; // Import your CSS file for styling

const PutawayTasksTable = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from the FastAPI backend
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await fetch('http://localhost:8000/task/putaway-tasks'); // Adjust the URL based on your backend API
        if (!response.ok) {
          throw new Error('Failed to fetch tasks');
        }
        const data = await response.json();
        setTasks(data.tasks); // Set the tasks data in state
      } catch (err) {
        setError(err.message); // Capture any errors
      } finally {
        setLoading(false); // Set loading to false after fetching
      }
    };

    fetchTasks();
  }, []);

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
      <div className="table-container"> {/* Wrap the table in this div */}
        <table>
          <thead>
            <tr>
              <th>Task ID</th>
              <th>Order ID</th>
              <th>Robot ID</th>
              <th>Shelf ID</th>
              <th>Station ID</th>
              <th>Status</th>
              <th>SKU List</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.task_id}>
                <td>{task.task_id}</td>
                <td>{task.order_id}</td>
                <td>{task.robot_id}</td>
                <td>{task.shelf_id}</td>
                <td>{task.station_id}</td>
                <td>{task.status}</td>
                <td>
                  <ul>
                    {task.sku_list.map((sku, index) => (
                      <li key={index}>
                        {sku.sku_code} (Amount: {sku.amount})
                      </li>
                    ))}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PutawayTasksTable;
