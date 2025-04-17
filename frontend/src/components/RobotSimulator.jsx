// components/RobotSimulator.jsx
import React, { useState } from 'react';
import { calculatePath } from '../utils/pathfinding';

const RobotSimulator = ({ mapData }) => {
  const [robotPos, setRobotPos] = useState(null);

  const simulatePath = (path) => {
    let index = 0;

    const interval = setInterval(() => {
      if (index >= path.length) {
        clearInterval(interval);
        return;
      }

      const { row, col } = path[index];
      setRobotPos({ row, col }); // Update robot position in the grid
      index++;
    }, 500); // Adjust speed as needed
  };

  const startSimulation = () => {
    if (!mapData || !mapData.components) return alert("No map data found");

    const components = mapData.components;
    const robot = components.find(c => c.type === 'Robot');
    const shelf = components.find(c => c.type === 'Shelf');
    const station = components.find(c => c.type === 'Station');

    if (!robot || !shelf || !station) {
      return alert("Robot, Shelf, or Station not found in map.");
    }

    const obstacles = components.filter(c => c.type === 'Obstacle')
      .map(o => ({ row: o.row, col: o.col }));

    const start = { row: robot.row, col: robot.col };
    const shelfPos = { row: shelf.row, col: shelf.col };
    const stationPos = { row: station.row, col: station.col };

    // Step 1: Path to the shelf
    const pathToShelf = calculatePath(start, shelfPos, obstacles, mapData.rows, mapData.cols);

    // Step 2: Path to the station (carrying the shelf)
    const pathToStation = calculatePath(shelfPos, stationPos, obstacles, mapData.rows, mapData.cols);

    // Step 3: Path back to the shelf's original position
    const pathBackToShelf = calculatePath(stationPos, shelfPos, obstacles, mapData.rows, mapData.cols);

    // Step 4: Path back to the robot's original position
    const pathBackToStart = calculatePath(shelfPos, start, obstacles, mapData.rows, mapData.cols);

    // Combine all paths
    const fullPath = [
      ...pathToShelf,
      ...pathToStation.slice(1), // Avoid duplicating the shelf position
      ...pathBackToShelf.slice(1),
      ...pathBackToStart.slice(1),
    ];

    console.log("Robot full path:", fullPath);
    simulatePath(fullPath); // Trigger the animation
  };

  return (
    <button onClick={startSimulation} className="start-button">
      ▶ Start Simulation
    </button>
  );
};

export default RobotSimulator;
