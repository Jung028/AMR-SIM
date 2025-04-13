import React, { useState, useRef } from 'react';
import MapSimulation from '../components/MapSimulation';
import DesiredOutputTable from '../components/DesiredOutputTable';
import '../styles/Home.css';

const GRID_ROWS = 20;
const GRID_COLS = 20;

const emptyMap = Array(GRID_ROWS).fill(null).map(() => Array(GRID_COLS).fill(null));

const Home = () => {
  const [mapData, setMapData] = useState(emptyMap);
  const [tempMapData, setTempMapData] = useState(mapData); // for editing
  const [isEditing, setIsEditing] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false); // State for modal visibility
  const fileInputRef = useRef(null);

  // Upload handler
  const handleUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        if (
          Array.isArray(json) &&
          json.length === GRID_ROWS &&
          json.every(row => Array.isArray(row) && row.length === GRID_COLS)
        ) {
          setMapData(json);
          setTempMapData(json); // also set tempMap for editing
        } else {
          alert("Invalid map file format.");
        }
      } catch (err) {
        alert("Error reading file: " + err.message);
      }
    };
    reader.readAsText(file);
  };

  // Download handler
  const handleDownload = () => {
    const json = JSON.stringify(mapData);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "mapData.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Toggle edit mode
  const handleEdit = () => {
    setIsEditing(true);
    setIsModalOpen(true); // Open modal when editing
  };

  // Save edited map
  const handleSave = () => {
    setMapData(tempMapData);
    setIsEditing(false);
    setIsModalOpen(false); // Close modal after saving
  };

  // Close the modal without saving
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setIsEditing(false); // Exit edit mode if modal is closed without saving
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
        <button onClick={handleDownload}>Download</button>
        {!isEditing ? (
          <button onClick={handleEdit}>Edit</button>
        ) : (
          <button onClick={handleSave}>Save</button>
        )}

      </div>
        
        {/* Main Page Map - without controls */}
            
        <div className="main-map">
        <MapSimulation
          showControls={false} // No controls shown outside modal
          mapData={mapData} // Display the current map
          setMapData={() => {}} // Disable updating map outside of editing
        />
      </div>


      {/* Modal for editing map */}
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={handleCloseModal}>X</button>
            <MapSimulation
              showControls={isEditing}
              mapData={isEditing ? tempMapData : mapData}
              setMapData={isEditing ? setTempMapData : () => {}}
            />
            <button onClick={handleSave}>Save</button>
          </div>
        </div>
      )}

    </div>
  );
};

export default Home;
