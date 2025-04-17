import React, { useState, useEffect } from 'react';
import '../styles/MapSimulation.css';
import robotParameters from './RobotConfig';

const GRID_ROWS = 20;
const GRID_COLS = 20;

const MapSimulation = ({ mapData, setMapData, showControls = true }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);
  const [maxCounts, setMaxCounts] = useState(null);
  const [placedCounts, setPlacedCounts] = useState({});
  const [tooltipText, setTooltipText] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  // New simulation states
  const [robotPos, setRobotPos] = useState(null);
  const [shelfPos, setShelfPos] = useState(null);
  const [shelfOriginalPos, setShelfOriginalPos] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/google-sheets-data')
      .then((res) => res.json())
      .then((data) => {
        const rows = data.rows.map(row => row.data);
        const getValue = (label) => {
          const row = rows.find(r => r[0] === label);
          return row ? parseInt(row[2], 10) : 0;
        };

        const initialMaxCounts = {
          Robot: getValue('Number of Robots'),
          Station: getValue('Stations'),
          Charging: getValue('Charging Ports'),
          Shelf: getValue('Shelves'),
          Disable: Infinity,
        };

        setMaxCounts(initialMaxCounts);
      })
      .catch((err) => console.error('Failed to fetch component limits:', err));
  }, []);

  useEffect(() => {
    if (!mapData || !mapData.components) {
      setMapData(prevData => prevData || {
        _id: { $oid: generateRandomObjectId() },
        name: 'New Map',
        rows: GRID_ROWS,
        cols: GRID_COLS,
        components: [],
      });
    } else {
      const counts = mapData.components.reduce((acc, comp) => {
        acc[comp.type] = (acc[comp.type] || 0) + 1;
        return acc;
      }, {});
      setPlacedCounts({
        Robot: counts.Robot || 0,
        Station: counts.Station || 0,
        Charging: counts.Charging || 0,
        Shelf: counts.Shelf || 0,
        Disable: 0,
      });
    }
  }, [mapData, setMapData]);

  const generateRandomObjectId = () => {
    return Math.floor(Date.now() / 1000).toString(16) + 'xxxxxxxxxxxxxxxx'.replace(/[x]/g, () =>
      ((Math.random() * 16) | 0).toString(16)
    );
  };

  const isOuterCell = (row, col) => {
    return row === 0 || row === GRID_ROWS - 1 || col === 0 || col === GRID_COLS - 1;
  };

  const placeComponent = (row, col) => {
    if (!currentItem || !maxCounts || (currentItem !== 'Disable' && placedCounts[currentItem] >= maxCounts[currentItem])) return;
    if (currentItem === 'Station' && !isOuterCell(row, col)) return;
    if ((currentItem === 'Robot' || currentItem === 'Charging' || currentItem === 'Shelf') && isOuterCell(row, col)) return;
    if (mapData.components.some((component) => component.row === row && component.col === col)) return;

    const newComponent = {
      id: `${currentItem.toLowerCase()}-${row}-${col}`,
      type: currentItem,
      row,
      col,
    };

    setMapData(prev => ({
      ...prev,
      components: [...prev.components, newComponent],
    }));

    setPlacedCounts(prev => ({
      ...prev,
      [currentItem]: (prev[currentItem] || 0) + 1,
    }));

    setRefreshKey(prev => prev + 1);
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
      case 'Robot': description = 'A mobile robot that performs tasks.'; break;
      case 'Station': description = 'A station that interacts with robots.'; break;
      case 'Charging': description = 'A charging station for robots.'; break;
      case 'Shelf': description = 'A shelf for storing items.'; break;
      case 'Disable': description = 'Disables the selected item.'; break;
      default: description = '';
    }
    setTooltipText(description);
  };

  const startSimulation = async () => {
    const robot = mapData.components.find(c => c.type === 'Robot');
    const shelf = mapData.components.find(c => c.type === 'Shelf');
    const station = mapData.components.find(c => c.type === 'Station');

    if (!robot || !shelf || !station) {
      alert("Place a robot, shelf, and station first!");
      return;
    }

    setRobotPos({ row: robot.row, col: robot.col });
    setShelfPos({ row: shelf.row, col: shelf.col });
    setShelfOriginalPos({ row: shelf.row, col: shelf.col });
    setIsSimulating(true);

    await moveTo(robot, shelf);
    await pickUpShelf();
    await moveTo(shelf, station);
    await waitAtStation();
    await moveTo(station, shelfOriginalPos);
    await placeShelf();
    await moveTo(shelfOriginalPos, { row: robot.row, col: robot.col });

    setIsSimulating(false);
  };

  const moveTo = (from, to) => {
    return new Promise((resolve) => {
      let current = { ...from };
      const interval = setInterval(() => {
        if (current.row !== to.row) {
          current.row += Math.sign(to.row - current.row);
        } else if (current.col !== to.col) {
          current.col += Math.sign(to.col - current.col);
        } else {
          clearInterval(interval);
          resolve();
          return;
        }

        setRobotPos({ ...current });

        // Carry shelf if robot and shelf are together
        if (shelfPos && robotPos && robotPos.row === shelfPos.row && robotPos.col === shelfPos.col) {
          setShelfPos({ ...current });
        }
      }, 1000 / robotParameters.speed);
    });
  };

  const pickUpShelf = () => new Promise(res => setTimeout(res, 500));
  const waitAtStation = () => new Promise(res => setTimeout(res, robotParameters.waitTime));
  const placeShelf = () => {
    setShelfPos(shelfOriginalPos);
    return new Promise(res => setTimeout(res, 500));
  };

  if (!mapData || !mapData.rows || !mapData.cols || !Array.isArray(mapData.components)) {
    return <div>Loading map...</div>;
  }

  if (!maxCounts) {
    return <div>Loading component limits...</div>;
  }

  return (
    <div className="simulation-container" onMouseUp={handleMouseUp}>
      {showControls && (
        <div className="controls">
          {Object.keys(maxCounts).map((item) => (
            <button
              key={item}
              className={currentItem === item ? 'active' : ''}
              onClick={() => handleButtonClick(item)}
            >
              {item}
              {item !== 'Disable' && maxCounts[item] !== Infinity &&
                ` (${maxCounts[item] - (placedCounts[item] || 0)})`}
              {currentItem === item && tooltipText && (
                <div className="tooltip">{tooltipText}</div>
              )}
            </button>
          ))}
          <button onClick={startSimulation} style={{ marginLeft: '10px' }}>Start Simulation</button>
        </div>
      )}

      <div className="grid" key={refreshKey}>
        {Array.from({ length: GRID_ROWS }).map((_, rowIndex) =>
          Array.from({ length: GRID_COLS }).map((_, colIndex) => {
            let cellType = mapData.components.find(
              (component) => component.row === rowIndex && component.col === colIndex
            )?.type;

            // Override with dynamic simulation positions
            if (isSimulating) {
              if (robotPos?.row === rowIndex && robotPos?.col === colIndex) {
                cellType = 'Robot';
              }
              if (shelfPos?.row === rowIndex && shelfPos?.col === colIndex) {
                cellType = 'Shelf';
              }
            }

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
