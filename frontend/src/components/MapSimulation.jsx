import React, { useState } from 'react';
import '../styles/MapSimulation.css';

const GRID_ROWS = 20;
const GRID_COLS = 20;

const MapSimulation = () => {
  const [mapData, setMapData] = useState(
    Array(GRID_ROWS).fill(null).map(() => Array(GRID_COLS).fill(null))
  );

  const [currentItem, setCurrentItem] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const [counts, setCounts] = useState({
    Robot: 13,
    Station: 10,
    Charging: 6,
    Shelf: 26,
    Disable: GRID_ROWS * GRID_COLS
  });

  const isOuterCell = (row, col) => {
    return row === 0 || row === GRID_ROWS - 1 || col === 0 || col === GRID_COLS - 1;
  };

  const placeComponent = (row, col) => {
    if (!currentItem || counts[currentItem] <= 0) return;
    if (currentItem === 'Station' && !isOuterCell(row, col)) return;
    if ((currentItem === 'Robot' || currentItem === 'Charging' || currentItem === 'Shelf' ) && isOuterCell(row, col)) return;


    if (mapData[row][col]) return; // If the cell is already occupied, do nothing.

    const newMap = [...mapData];
    newMap[row][col] = currentItem;
    setMapData(newMap);
    setCounts(prev => ({ ...prev, [currentItem]: prev[currentItem] - 1 }));
  };

  const handleMouseDown = (row, col) => {
    setIsDragging(true);
    placeComponent(row, col);
  };

  const handleMouseEnter = (row, col) => {
    if (isDragging) placeComponent(row, col);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div className="simulation-container" onMouseUp={handleMouseUp}>
      <div className="controls">
        {Object.keys(counts).map((item) => (
          <button
            key={item}
            className={currentItem === item ? 'active' : ''}
            onClick={() => setCurrentItem(item)}
          >
            {item} ({counts[item]})
          </button>
        ))}
      </div>

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
