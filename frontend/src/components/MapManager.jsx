// src/components/MapManager.jsx
import React, { useState, useEffect, useRef } from 'react';
import MapSimulation from './MapSimulation';
import PutawayTasksTable from './PutawayTasksTable';
import '../styles/MapManager.css';

const MapManager = ({ agvMode }) => {
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
  const [currentMapId, setCurrentMapId] = useState(null);

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

  try {
    let newMapData = { ...tempMapData };

    // Generate unique map ID if not present (i.e., new map)
    if (!newMapData.mapId) {
      // Fetch the latest map ID from the backend
      const idResponse = await fetch("http://127.0.0.1:8000/api/maps/latest-id");
      const { latestId } = await idResponse.json();

      // Increment and format as M### (e.g., M811 -> M812)
      const newIdNumber = parseInt(latestId?.replace("M", "")) + 1 || 801;
      const newMapId = `M${newIdNumber}`;

      newMapData = {
        ...newMapData,
        mapId: newMapId,
        name: `Map ${newMapId}`,
      };
    }

    newMapData.rows = newMapData.rows || 20;
    newMapData.cols = newMapData.cols || 20;

    if (!mapData._id) {
      alert("No map to save (missing ID).");
      return;
    }

    const response = await fetch(`http://127.0.0.1:8000/api/maps/${mapData._id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newMapData),
    });

    if (response.ok) {
      const updatedMap = await response.json();
      setTempMapData(updatedMap);
      alert("Map updated successfully!");
      handleCloseModal();
      fetchAvailableMaps();
      refreshMap();
      localStorage.setItem("mapData", JSON.stringify(updatedMap));
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
          setCurrentMapId(mapId); // Dynamically set the loaded map ID
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

  const startSimulation = async () => {
    const response = await fetch("http://127.0.0.1:8000/orders/putaway", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ currentMapId: currentMapId }) // <=== ADD THIS

    });
    const data = await response.json();
    console.log(data.message); // Logs: "Putaway order created"

    // Step 2: Generate putaway tasks (AFTER creating the order)
    const taskResponse = await fetch("http://127.0.0.1:8000/task/generate-putaway", {
      method: "POST",
      headers: { "Content-Type": "application/json",

      },
      body: JSON.stringify({ mode: agvMode }), // include selected mode

    });

    const taskData = await taskResponse.json();
    console.log(taskData.message); // Logs: "Putaway tasks generated" or similar
    
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

  const generateTables = async () => {


    if (!tempMapData || !tempMapData.components || !currentMapId) {
      alert("Map not loaded or missing map ID.");
      return;
    }
  
    const mapId = currentMapId; // <=== Use the correct current map ID
    const { components } = tempMapData;
  
    const robots = components.filter(c => c.type.toLowerCase() === 'robot')
      .map((robot, index) => ({
        robot_id: `R${index + 1}`,
        status: 'idle',
        location: { x: robot.row, y: robot.col },
        map_id: mapId,
        battery_level: 100, // battery starts 100%
      }));
  
    const shelves = components.filter(c => c.type.toLowerCase() === 'shelf')
      .map((shelf, index) => ({
        shelf_id: `S${index + 1}`,
        map_id: mapId,
        row: shelf.row,
        col: shelf.col,
        status: 'idle',
        available_space: 100,
        sku_group: 'default_sku_group',
      }));
  
    const stations = components.filter(c => c.type.toLowerCase() === 'station')
      .map((station, index) => ({
        station_id: `ST${index + 1}`,
        map_id: mapId,
        row: station.row,
        col: station.col,
        status: 'available',
        queue_length: 0,
        location: { x: station.row, y: station.col },
      }));
  
    console.log("Generated Payload:", { robots, shelves, stations });
  
    await sendDataToBackend(mapId, robots, shelves, stations);
  };
  
  
  const sendDataToBackend = async (mapId, robots, shelves, stations) => {
    try {
      // Send robots data
      for (const robot of robots) {
        const robotData = { 
          robot_id: robot.robot_id, 
          status: robot.status,
          location: robot.location,
          map_id: robot.map_id,  // Including map_id in the payload
          battery_level: robot.battery_level || 100, // Use provided battery level or default to 100
        };
  
        const response = await fetch('http://127.0.0.1:8000/robots/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(robotData),
        });
  
        if (!response.ok) {
          const errorData = await response.json();
          console.error('Error response:', errorData);
          throw new Error('Failed to save robot data.');
        }
      }
  
            // Send shelves data
      for (const shelf of shelves) {
        // Shelf total volume (capacity)
        const shelfTotalVolume = shelf.shelf_capacity || 41184; // Total capacity of the shelf (in volume)

        // Set available space to 1/3 of the total shelf volume
        const availableSpace = shelfTotalVolume / 3; // Available space is 1/3 of total volume

        // Shelf levels structure, each level gets the same available space
        const shelfLevels = {
          ground: {
            available_space: availableSpace, // 1/3 of the shelf volume for ground
            sku_details: []
          },
          second: {
            available_space: availableSpace, // 1/3 for second level
            sku_details: []
          },
          third: {
            available_space: availableSpace, // 1/3 for third level
            sku_details: []
          }
        };

        // Calculate the total available space by subtracting the space used by placed SKUs
        let totalUsedSpace = 0;
        const skusToPlace = shelf.sku_details || [];

        // Loop through each SKU to calculate the space used
        for (const sku of skusToPlace) {
          const skuVolume = sku.sku_volume; // Assuming each SKU has a volume property
          totalUsedSpace += skuVolume * sku.sku_amount; // Total space used by this SKU (considering amount)
        }

        // Subtract the used space from the shelf total volume to get the remaining available space
        const remainingSpace = shelfTotalVolume - totalUsedSpace;

        // Ensure remaining space is not less than 0
        const finalAvailableSpace = Math.max(remainingSpace, 0);

        // Adjust the shelf levels with the remaining available space (keeping each level proportional)
        shelfLevels.ground.available_space = finalAvailableSpace / 3; // Divide remaining space equally across 3 levels
        shelfLevels.second.available_space = finalAvailableSpace / 3; 
        shelfLevels.third.available_space = finalAvailableSpace / 3;

        const shelfData = {
          shelf_id: shelf.shelf_id,
          map_id: shelf.map_id,
          shelf_capacity: shelf.shelf_capacity || 41184, // Shelf capacity remains the same
          available_space: finalAvailableSpace, // Total remaining available space in shelf
          shelf_levels: shelfLevels, // Updated shelf levels with available space
        };

        try {
          console.log("Sending shelfData:", shelfData); // Debug log

          const response = await fetch('http://127.0.0.1:8000/station/add-shelf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(shelfData),
          });

          if (!response.ok) {
            const errorData = await response.json();
            console.error('Error response:', errorData);
            throw new Error('Failed to save shelf data.');
          }
        } catch (error) {
          console.error('Error sending data:', error);
        }
      }

      
  
      // Send stations data
      for (const station of stations) {
        const stationData = {
          station_id: station.station_id,
          map_id: station.map_id,
          row: station.row,
          col: station.col,
          status: station.status,
          queue_length: station.queue_length,
          location: station.location,
        };
  
        const response = await fetch('http://127.0.0.1:8000/station/add-putaway-station', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(stationData),
        });
  
        if (!response.ok) {
          const errorData = await response.json();
          console.error('Error response:', errorData);
          throw new Error('Failed to save station data.');
        }
      }
  
      alert("Data saved successfully.");
    } catch (error) {
      console.error("Error sending data:", error);
      alert('Error sending data to the backend: ' + error.message);
    }
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
        <button className="button" onClick={() => fileInputRef.current.click()}>Upload</button>
        <input
          type="file"
          accept=".json"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleUpload}
        />
        <button className="button" onClick={() => setIsLoadModalOpen(true)}>Load</button>
        <button className="button" onClick={handleDownload}>Download</button>
        <button className="button" onClick={handleEdit}>Edit</button>
        <button className="button" onClick={generateTables} style={{ marginTop: '10px' }}>Generate Tables</button>
        <button className="button" onClick={startSimulation} style={{ marginTop: '10px' }}>Start Simulation</button>
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

      {/* Modal for Edit Button */}
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

      <PutawayTasksTable mapId={currentMapId} />
    </div>
  );
};

export default MapManager;
