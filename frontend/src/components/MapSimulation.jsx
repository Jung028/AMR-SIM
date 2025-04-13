import React, { useState } from 'react';
import '../styles/MapSimulation.css';

const GRID_ROWS = 20;
const GRID_COLS = 20;

const MapSimulation = ({ showControls = true, mapData, setMapData }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);
  const [counts, setCounts] = useState({
    Robot: 13,
    Station: 10,
    Charging: 6,
    Shelf: 26,
    Disable: GRID_ROWS * GRID_COLS,
  });
  const [tooltipText, setTooltipText] = useState('');

  const isOuterCell = (row, col) => {
    return row === 0 || row === GRID_ROWS - 1 || col === 0 || col === GRID_COLS - 1;
  };

  const placeComponent = (row, col) => {
    if (!currentItem || counts[currentItem] <= 0) return;
    if (currentItem === 'Station' && !isOuterCell(row, col)) return;
    if ((currentItem === 'Robot' || currentItem === 'Charging' || currentItem === 'Shelf') && isOuterCell(row, col)) return;

    if (mapData[row][col]) return;

    const newMap = [...mapData.map(row => [...row])]; // Deep copy to avoid mutation
    newMap[row][col] = currentItem;
    setMapData(newMap);
    setCounts(prev => ({ ...prev, [currentItem]: prev[currentItem] - 1 }));
  };

  const handleMouseDown = (row, col) => {
    placeComponent(row, col);
    setIsDragging(true);
  };

  const handleMouseEnter = (row, col) => {
    if (isDragging) placeComponent(row, col);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleButtonClick = (item) => {
    setCurrentItem(item);
    let description = '';
    switch (item) {
      case 'Robot':
        description = 'A mobile robot that performs tasks.';
        break;
      case 'Station':
        description = 'A station that interacts with robots.';
        break;
      case 'Charging':
        description = 'A charging station for robots.';
        break;
      case 'Shelf':
        description = 'A shelf for storing items.';
        break;
      case 'Disable':
        description = 'Disables the selected item.';
        break;
      default:
        description = '';
    }
    setTooltipText(description);
  };

  return (
    <div className="simulation-container" onMouseUp={handleMouseUp}>
      {showControls && (
        <div className="controls">
          {Object.keys(counts).map((item) => (
            <button
              key={item}
              className={currentItem === item ? 'active' : ''}
              onClick={() => handleButtonClick(item)}
            >
              {item} ({counts[item]})
              {currentItem === item && tooltipText && (
                <div className="tooltip">{tooltipText}</div>
              )}
            </button>
          ))}
        </div>
      )}

      <div className="grid">
        {mapData.map((row, rowIndex) =>
          row.map((cell, colIndex) => {
            const cellType = mapData[rowIndex][colIndex];
            return (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={`grid-cell cell-${cellType || 'empty'} ${isOuterCell(rowIndex, colIndex) ? 'outer-cell' : ''}`}
                onClick={() => placeComponent(rowIndex, colIndex)}
                onMouseDown={() => handleMouseDown(rowIndex, colIndex)}
                onMouseEnter={() => handleMouseEnter(rowIndex, colIndex)}
              />
            );
          })
        )}
      </div>
    </div>
  );
};

export default MapSimulation;
