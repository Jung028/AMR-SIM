// src/components/Algorithm.jsx
import React, { useState, useEffect } from 'react';
import '../styles/Algorithm.css';

const algorithms = [
  {
    id: 'AStar',
    type: 'Pathfinding',
    name: 'A* Algorithm',
    description: 'Finds the shortest path using a heuristic-based approach.',
  },
  {
    id: 'Dijkstra',
    type: 'Pathfinding',
    name: "Dijkstra's Algorithm",
    description: 'Classic pathfinding algorithm with guaranteed shortest path.',
  },
  {
    id: 'Greedy',
    type: 'Heuristic',
    name: 'Greedy Best-First Search',
    description: 'Follows the path that appears best at each step.',
  },
  {
    id: 'BellmanFord',
    type: 'Pathfinding',
    name: 'Bellman-Ford Algorithm',
    description: 'Solves single-source shortest path problems in graphs.',
  },
  {
    id: 'Prim',
    type: 'Graph',
    name: 'Prim\'s Algorithm',
    description: 'Finds the minimum spanning tree of a graph.',
  },
];

const Algorithm = ({ onChange }) => {
  const [selectedAlgorithms, setSelectedAlgorithms] = useState([]);
  const [openModalId, setOpenModalId] = useState(null);
  const [selectedType, setSelectedType] = useState('Pathfinding'); // Default to 'Pathfinding'

  const handleToggle = (algorithmId) => {
    setSelectedAlgorithms((prev) =>
      prev.includes(algorithmId)
        ? prev.filter((id) => id !== algorithmId)
        : [...prev, algorithmId]
    );
    setOpenModalId(null); // Close modal after selecting
  };

  const openModal = (id) => {
    setOpenModalId(id);
  };

  const closeModal = () => {
    setOpenModalId(null);
  };

  useEffect(() => {
    onChange(selectedAlgorithms);
  }, [selectedAlgorithms, onChange]);

  const filterAlgorithmsByType = (type) => {
    return algorithms.filter((algo) => algo.type === type);
  };

  return (
    <div className="algorithm-section">
      {/* Instruction Title */}
      <div className="instruction-title-container">
        <h3 className="instruction-title">Please Choose an Algorithm</h3>
      </div>

      {/* Algorithm Type Toggle Buttons */}
      <div className="algorithm-type-toggle">
        <button
          className={`toggle-btn ${selectedType === 'Pathfinding' ? 'active' : ''}`}
          onClick={() => setSelectedType('Pathfinding')}
        >
          Pathfinding Algorithms
        </button>
        <button
          className={`toggle-btn ${selectedType === 'Heuristic' ? 'active' : ''}`}
          onClick={() => setSelectedType('Heuristic')}
        >
          Heuristic Algorithms
        </button>
        <button
          className={`toggle-btn ${selectedType === 'Graph' ? 'active' : ''}`}
          onClick={() => setSelectedType('Graph')}
        >
          Graph Algorithms
        </button>
      </div>

      <div className="algorithm-container">
        {/* Left Section (30% width) */}
        <div className="algorithm-left">
          <div className="title-container">
            <h3 className="section-title">Algorithms</h3>
            <p className="section-description">
              Select an algorithm type from the buttons above to explore the different algorithms
              that help solve various computational problems. Each algorithm has its own unique way
              of approaching tasks such as finding shortest paths, solving graph problems, or making
              decisions based on heuristic methods.
            </p>
            <p className="section-info">
              Algorithms are categorized into different types based on their approach and problem-solving
              domain. Understanding the differences between these types will help you select the right one
              for your needs.
            </p>
          </div>

           
        </div>

        {/* Right Section (70% width) */}
        <div className="algorithm-right">
          <div className="algorithms-container">
            <div className="algorithm-grid">
              {filterAlgorithmsByType(selectedType).map((algo) => (
                <div
                  key={algo.id}
                  className={`algorithm-card ${selectedAlgorithms.includes(algo.id) ? 'selected' : ''}`}
                  onClick={() => openModal(algo.id)}
                >
                  <h4>{algo.name}</h4>
                  <p>{algo.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {openModalId && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-modal" onClick={closeModal}>×</button>
            <h2>{algorithms.find((a) => a.id === openModalId).name}</h2>
            <p>{algorithms.find((a) => a.id === openModalId).description}</p>

            <button
              onClick={() => handleToggle(openModalId)}
              className={`modal-submit ${selectedAlgorithms.includes(openModalId) ? 'deselect' : ''}`}
            >
              {selectedAlgorithms.includes(openModalId) ? 'Deselect' : 'Select'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Algorithm;
