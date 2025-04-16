// src/pages/Home.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import MapManager from '../components/MapManager';
import DesiredOutputTable from '../components/DesiredOutputTable';
import '../styles/Home.css';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="home-container" style={{ position: 'relative', minHeight: '100vh' }}>
      <h1>Map Simulation</h1>
      <DesiredOutputTable />
      <MapManager />

      {/* Next Button */}
      <button
        className="next-button"
        onClick={() => navigate('/simulation')}
      >
        Next →
      </button>
    </div>
  );
};

export default Home;
