// src/components/MapManager.jsx
import React, { useState, useEffect, useRef } from 'react';
import MapSimulation from './MapSimulation';
import '../styles/MapManager.css';

const MapManager = ({ hideTopBar = false }) => {
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
        localStorage.setItem("mapData", JSON.stringify(mapData));
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

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setIsEditing(false);
  };

  return (
    <div>
      {!hideTopBar && (
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
      )}

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
