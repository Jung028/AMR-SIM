// src/components/MapManager.jsx
import React, { useState, useEffect, useRef } from 'react';
import MapSimulation from './MapSimulation';
import '../styles/MapManager.css';

const MapManager = () => {
  const [mapData, setMapData] = useState({
    _id: { $oid: "initial-map-id" },
    name: 'New Map',
    rows: 20,
    cols: 20,
    components: []
  });
  const [tempMapData, setTempMapData] = useState({ components: [] });
  const [availableMaps, setAvailableMaps] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoadModalOpen, setIsLoadModalOpen] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [robotPos, setRobotPos] = useState({ row: 0, col: 0 });
  const [shelfPos, setShelfPos] = useState({ row: 0, col: 0 });
  const [shelfOriginalPos, setShelfOriginalPos] = useState({ row: 0, col: 0 });
  const fileInputRef = useRef(null);

  const fetchAvailableMaps = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/maps");
      if (response.ok) {
        const maps = await response.json();
        const formattedMaps = maps
          .filter((map) => map && map._id)
          .map((map) => ({
            _id: map._id?.$oid || map._id,
            name: map.name || "Unnamed Map",
          }));
        setAvailableMaps(formattedMaps);
      } else {
        alert("No maps available.");
      }
    } catch (error) {
      alert("Error fetching map data: " + error.message);
    }
  };

  const refreshMap = async () => {
    if (!mapData._id) {
      alert("No map ID found to refresh.");
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/maps/id/${mapData._id}`);
      if (response.ok) {
        const updatedMap = await response.json();
        setMapData(updatedMap);
        setTempMapData(updatedMap);
        localStorage.setItem("mapData", JSON.stringify(updatedMap));
      } else {
        alert("Failed to refresh map.");
      }
    } catch (error) {
      alert("Error refreshing map: " + error.message);
    }
  };

  useEffect(() => {
    const savedMap = localStorage.getItem("mapData");
    if (savedMap) {
      const map = JSON.parse(savedMap);
      setMapData(map);
      setTempMapData(map);
    }
    fetchAvailableMaps();
  }, []);

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/maps/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        alert("Map uploaded and saved successfully!");
        fetchAvailableMaps();
        setMapData(data);
        setTempMapData(data);
        localStorage.setItem("mapData", JSON.stringify(data));
      } else {
        alert("Failed to upload map.");
      }
    } catch (err) {
      alert("Error uploading map: " + err.message);
    }
  };

  const handleSave = async () => {
    if (!tempMapData.components.length) {
      alert("No components to save.");
      return;
    }

    const mapToSave = {
      ...tempMapData,
      name: tempMapData.name || "Updated Map Name",
      rows: tempMapData.rows || 20,
      cols: tempMapData.cols || 20,
    };

    try {
      if (!mapData._id) {
        alert("No map to save (missing ID).");
        return;
      }

      const response = await fetch(`http://127.0.0.1:8000/api/maps/${mapData._id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(mapToSave),
      });

      if (response.ok) {
        const updatedMap = await response.json();
        setTempMapData(updatedMap);
        alert("Map updated successfully!");
        handleCloseModal();
        fetchAvailableMaps();
        refreshMap();
        localStorage.setItem("mapData", JSON.stringify(updatedMap)); // Fixed to store updated map
      } else {
        alert("Failed to save the map.");
      }
    } catch (error) {
      alert("Error saving map: " + error.message);
    }
  };

  const handleDownload = () => {
    const json = JSON.stringify(mapData, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "mapData.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleLoad = async (mapId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/maps/id/${mapId}`);
      if (response.ok) {
        const map = await response.json();
        if (map && map.components) {
          setMapData(map);
          setTempMapData(map);
          setIsLoadModalOpen(false);
          localStorage.setItem("mapData", JSON.stringify(map));
        } else {
          alert("Map data is missing or incomplete.");
        }
      } else {
        alert("Failed to load map");
      }
    } catch (error) {
      alert("Error loading map: " + error.message);
    }
  };

  const handleEdit = () => {
    if (mapData?.components?.length > 0) {
      setTempMapData({ ...mapData });
      setIsEditing(true);
      setIsModalOpen(true);
    } else {
      alert("No valid map components to edit.");
    }
  };

  const startSimulation = () => {
    if (mapData && mapData.components) {
      const robot = mapData.components.find(c => c.type === 'Robot');
      const shelf = mapData.components.find(c => c.type === 'Shelf');
      const station = mapData.components.find(c => c.type === 'Station');
  
      if (!robot || !shelf || !station) {
        alert("Please place both a robot, a shelf, and a station first.");
        return;
      }
  
      setIsEditing(false);
      setIsModalOpen(false); // Close any modal if open
      setIsSimulating(true);
      startRobotMovementSimulation(robot, shelf, station);
    }
  };

  const startRobotMovementSimulation = async (robot, shelf, station) => {
    // Set initial positions
    setRobotPos({ row: robot.row, col: robot.col });
    setShelfPos({ row: shelf.row, col: shelf.col });
    setShelfOriginalPos({ row: shelf.row, col: shelf.col });
  
    // Move robot to shelf
    await moveTo({ row: robot.row, col: robot.col }, { row: shelf.row, col: shelf.col });
    await pickUpShelf();
  
    // Move to station
    await moveTo({ row: shelf.row, col: shelf.col }, { row: station.row, col: station.col });
    await waitAtStation();
  
    // Return shelf to original position
    await moveTo({ row: station.row, col: station.col }, shelfOriginalPos);
    await placeShelf();
  
    // Move robot back to its original position
    await moveTo(shelfOriginalPos, { row: robot.row, col: robot.col });
  
    setIsSimulating(false); // End simulation
  };
  
  // This is the function to simulate movement. You can modify it as needed to update `mapData` based on new robot positions
  const moveTo = async (start, end) => {
    // Assume movement takes place in steps, and each step is a 1-unit movement.
    const totalSteps = Math.max(Math.abs(end.row - start.row), Math.abs(end.col - start.col));
  
    for (let step = 0; step <= totalSteps; step++) {
      const currentRow = start.row + ((end.row - start.row) / totalSteps) * step;
      const currentCol = start.col + ((end.col - start.col) / totalSteps) * step;
  
      // Update the robot's position in the mapData state
      setMapData((prevState) => {
        const updatedComponents = prevState.components.map((component) =>
          component.type === 'Robot'
            ? { ...component, row: Math.round(currentRow), col: Math.round(currentCol) }
            : component
        );
        return { ...prevState, components: updatedComponents };
      });
  
      // Simulate a delay to make the movement visible
      await new Promise((resolve) => setTimeout(resolve, 500)); // 100ms delay for each step
    }
  };

  const pickUpShelf = async () => {
    // Simulate picking up the shelf
    return new Promise(resolve => setTimeout(resolve, 1000));
  };

  const waitAtStation = async () => {
    // Simulate waiting at the station
    return new Promise(resolve => setTimeout(resolve, 1000));
  };

  const placeShelf = async () => {
    // Simulate placing the shelf back
    return new Promise(resolve => setTimeout(resolve, 1000));
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setIsEditing(false);
  };

  return (
    <div>
      <div className="top-bar">
        <button onClick={() => fileInputRef.current.click()}>Upload</button>
        <input
          type="file"
          accept=".json"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleUpload}
        />
        <button onClick={() => setIsLoadModalOpen(true)}>Load</button>
        <button onClick={handleDownload}>Download</button>
        <button onClick={handleEdit}>Edit</button>
        <button onClick={startSimulation} style={{ marginTop: '10px' }}>Start Simulation</button>
      </div>

      <div className="main-map">
        <MapSimulation
          showControls={isEditing}
          mapData={mapData}
          setMapData={setTempMapData}
        />
      </div>

      {isLoadModalOpen && (
        <div className="modal">
          <div className="modal-content scrollable-modal">
            <button className="close-btn" onClick={() => setIsLoadModalOpen(false)}>X</button>
            <h2>Select a Map</h2>
            <table>
              <thead>
                <tr>
                  <th>Map Name</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {availableMaps.map((map) => (
                  <tr key={map._id}>
                    <td>{map.name}</td>
                    <td>
                      <button onClick={() => handleLoad(map._id)}>Load</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={handleCloseModal}>X</button>
            <MapSimulation
              showControls={isEditing}
              mapData={tempMapData}
              setMapData={setTempMapData}
            />
            <button onClick={handleSave}>Save</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapManager;
