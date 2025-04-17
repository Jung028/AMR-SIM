import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Algorithm from '../components/Algorithm';
import Sku_Sync from '../components/Sku_Sync';
import '../styles/Simulation.css';

const Simulation = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(null);
  const [selectedAlgorithms, setSelectedAlgorithms] = useState([]);

  const handleBack = () => navigate('/');
  const openModal = (modalId) => setIsModalOpen(modalId);
  const closeModal = () => setIsModalOpen(null);
  const handleStart = () => {
    console.log('Starting simulation with algorithms:', selectedAlgorithms);
  };

  return (
    <div className="home-container">
      <h1>Map Simulation & Algorithm</h1>

      {/* Back Button */}
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

      {/* Start Button */}
      <div className="start-container">
        <button onClick={handleStart} className="start-button">
          ▶ Start Simulation
        </button>
      </div>

      {/* SKU Sync Modal */}
      {isModalOpen === 'skuSync' && <Sku_Sync isOpen={true} closeModal={closeModal} />}
    </div>
  );
};

export default Simulation;
