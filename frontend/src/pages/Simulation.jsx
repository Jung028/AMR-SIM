import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Algorithm from '../components/Algorithm';
import Sku_Sync from '../components/Sku_Sync';
import MapManager from '../components/MapManager';
import PutawayTasksTable from '../components/PutawayTasksTable';
import '../styles/Simulation.css';

const Simulation = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(null);
  const [selectedAlgorithms, setSelectedAlgorithms] = useState([]);
  const [simulationInProgress, setSimulationInProgress] = useState(false);
  const [agvMode, setAgvMode] = useState('proximity'); // NEW STATE for AGV mode

  const mapRef = useRef(); // Ref to control MapManager

  const handleBack = () => navigate('/');
  const openModal = (modalId) => setIsModalOpen(modalId);
  const closeModal = () => setIsModalOpen(null);

  const handleStartSimulation = () => {
    if (simulationInProgress) return;
    console.log('Starting simulation with algorithms:', selectedAlgorithms);
    console.log('Selected AGV mode:', agvMode);
    setSimulationInProgress(true);
    
    // Trigger simulation inside MapManager and pass agvMode
    mapRef.current?.startSimulationSequence(() => {
      setSimulationInProgress(false);
    }, agvMode);
  };

  return (
    <div className="home-container">
      <h1>Map Simulation & Algorithm</h1>

      <button onClick={handleBack} className="back-button">← Back</button>

      {/* SKU Sync Section */}
      <div className="category-container">
        <div className="category">
          <h3>SKU Sync</h3>
          <p>To create a new SKU, enter values catered to your company's products</p>
          <div className="button-group">
            <button onClick={() => openModal('skuSync')}>SKU SYNC</button>
          </div>
        </div>
      </div>

      {/* Algorithm Selector */}
      <Algorithm onChange={setSelectedAlgorithms} />

      {/* AGV Mode Selector */}
      <div className="category-container">
        <div className="category">
          <h3>AGV Assignment Mode</h3>
          <div className="button-group">
            {['proximity', 'energy', 'load_balanced'].map(mode => (
              <button
                key={mode}
                className={`mode-button ${agvMode === mode ? 'selected' : ''}`}
                onClick={() => setAgvMode(mode)}
              >
                {mode.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Map Manager with ref */}
      <MapManager ref={mapRef} isSimulating={simulationInProgress} hideTopBar={true} agvMode={agvMode}/>

      {/* Putaway Tasks Table */}
      <PutawayTasksTable />

      {/* Start Simulation Button */}
      <div className="start-container">
        <button onClick={handleStartSimulation} className="start-button" disabled={simulationInProgress}>
          ▶ Start Simulation
        </button>
      </div>

      {/* SKU Sync Modal */}
      {isModalOpen === 'skuSync' && <Sku_Sync isOpen={true} closeModal={closeModal} />}
    </div>
  );
};

export default Simulation;
