import React, { useState, useRef, useEffect } from 'react';
import MapSimulation from '../components/MapSimulation';
import DesiredOutputTable from '../components/DesiredOutputTable';
import '../styles/Home.css';

const Home = () => {
  const [mapData, setMapData] = useState({ components: [] });
  const [tempMapData, setTempMapData] = useState({ components: [] });
  const [availableMaps, setAvailableMaps] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoadModalOpen, setIsLoadModalOpen] = useState(false);
  const fileInputRef = useRef(null);

  // Fetch available maps from the backend
  const fetchAvailableMaps = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/maps");
      if (response.ok) {
        const maps = await response.json();
        console.log("Fetched maps:", maps);
  
        const formattedMaps = maps
        .filter((map) => map && map._id) // Filter out null maps or missing IDs
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

  useEffect(() => {
    fetchAvailableMaps();
  }, []);

  // Handle file upload for maps
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
        console.log("Uploaded map data:", data);
        alert("Map uploaded and saved successfully!");
        fetchAvailableMaps();
      } else {
        alert("Failed to upload map.");
      }
    } catch (err) {
      alert("Error uploading map: " + err.message);
    }
  };
  
  

  // Handle map saving
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
      // Assuming mapData._id holds the ID of the map being edited
      if (!mapData._id) {
        alert("No map to save (missing ID).");
        return;
      }
  
      const response = await fetch(`http://127.0.0.1:8000/api/maps/${mapData._id}`, {
        method: "PUT",  // Use PUT to update the existing map
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(mapToSave),
      });
  
      if (response.ok) {
        const updatedMap = await response.json();
        console.log("Updated map:", updatedMap);
        setMapData(updatedMap);  // Update the state with the updated map
        setTempMapData(updatedMap);  // Update the temporary map data
        alert("Map updated successfully!");
        handleCloseModal();  // Close the modal after saving
        fetchAvailableMaps();  // Refresh the list of available maps
      } else {
        alert("Failed to save the map.");
      }
    } catch (error) {
      alert("Error saving map: " + error.message);
    }
  };
  
  
  
  

  // Handle downloading of map data
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

  // Handle loading of a specific map
  const handleLoad = async (mapId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/maps/id/${mapId}`);
      if (response.ok) {
        const map = await response.json();
        console.log("Loaded map from MongoDB:", map);
  
        if (map && map.components) {
          setMapData(map);
          setTempMapData(map);
          setIsLoadModalOpen(false);
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
      console.log('Editing components:', mapData.components);
      setIsEditing(true);
      setIsModalOpen(true);
    } else {
      console.error("mapData is missing components or is empty");
      alert("No valid map components to edit.");
    }
  };
  
  
  
  

  // Close the modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setIsEditing(false);
  };

  return (
    <div className="home-container">
      <h1>Map Simulation</h1>
      <DesiredOutputTable />

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
      </div>


      <div className="main-map">
      <MapSimulation
        showControls={isEditing}
        mapData={tempMapData}  // Ensure this is the editable state
        setMapData={setTempMapData}  // Allow updating the temp map data
      />

      </div>

      {/* Load Modal */}
      {isLoadModalOpen && (
        <div className="modal">
          <div className="modal-content">
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

      {/* Edit Modal */}
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={handleCloseModal}>X</button>
            <MapSimulation
              showControls={isEditing}
              mapData={tempMapData}
              setMapData={setTempMapData}  // Allow updating map data in tempMapData
            />
            <button onClick={handleSave}>Save</button>
          </div>
        </div>
      )}

    </div>
  );
};

export default Home;
