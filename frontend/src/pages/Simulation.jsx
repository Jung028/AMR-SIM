// src/pages/Simulation.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Simulation.css';

const Simulation = () => {
  const navigate = useNavigate();

  // State to control which modal is open
  const [isModalOpen, setIsModalOpen] = useState(null);

  const handleBack = () => {
    navigate('/');
  };

  // Function to open specific modal
  const openModal = (modalId) => {
    setIsModalOpen(modalId);
  };

  // Function to close all modals
  const closeModal = () => {
    setIsModalOpen(null);
  };

  return (
    <div className="home-container">
      <h1>Map Simulation & Algorithm</h1>

      {/* Back Button */}
      <button onClick={handleBack} className="back-button">
        ← Back
      </button>

      {/* Background Container for Categories */}
      <div className="category-container">
        {/* SKU Sync Category */}
        <div className="category">
          <h3>SKU Sync</h3>
          <div className="button-group">
            <button onClick={() => openModal('skuSync')}>SKU SYNC</button>
          </div>
        </div>

        {/* Putaway Actions Category */}
        <div className="category">
          <h3>Putaway Actions</h3>
          <div className="button-group">
            <button onClick={() => openModal('putawayOrderCreation')}>Putaway Order Creation</button>
            <button onClick={() => openModal('putawayOrderConfirm')}>Putaway Order Confirm</button>
            <button onClick={() => openModal('putawayOrderCancellation')}>Putaway Order Cancellation</button>
          </div>
        </div>

        {/* Pickaway Actions Category */}
        <div className="category">
          <h3>Pickaway Actions</h3>
          <div className="button-group">
            <button onClick={() => openModal('pickOrderCreation')}>Pick Order Creation</button>
            <button onClick={() => openModal('pickOrderConfirm')}>Pick Order Confirm</button>
            <button onClick={() => openModal('pickOrderCancellation')}>Pick Order Cancellation</button>
          </div>
        </div>

        {/* Inventory Actions Category */}
        <div className="category">
          <h3>Inventory Actions</h3>
          <div className="button-group">
            <button onClick={() => openModal('internalStocktaking')}>Internal Stocktaking Variance Adjustment</button>
            <button onClick={() => openModal('inventorySnapshot')}>Inventory Snapshot Reconciliation</button>
          </div>
        </div>
      </div>

      {/* Modals */}
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-modal" onClick={closeModal}>
              X
            </button>
            <h2>{isModalOpen.replace(/([A-Z])/g, ' $1').trim()}</h2> {/* Dynamic modal title */}
            <form>
              <div>
                <label>Form Input:</label>
                <input type="text" placeholder="Enter details" />
              </div>
              <button type="submit">Submit</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Simulation;
