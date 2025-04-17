// utils/pathfinding.js
export function calculatePath(start, goal, obstacles, rows, cols) {
    const queue = [[start]];
    const visited = new Set();
    const key = (r, c) => `${r}-${c}`;
    visited.add(key(start.row, start.col));
  
    const dirs = [
      [0, 1], [1, 0], [0, -1], [-1, 0]
    ];
  
    while (queue.length > 0) {
      const path = queue.shift();
      const { row, col } = path[path.length - 1];
  
      if (row === goal.row && col === goal.col) {
        return path;
      }
  
      for (const [dr, dc] of dirs) {
        const newRow = row + dr;
        const newCol = col + dc;
        const posKey = key(newRow, newCol);
  
        const inBounds = newRow >= 0 && newRow < rows && newCol >= 0 && newCol < cols;
        const isObstacle = obstacles.some(o => o.row === newRow && o.col === newCol);
  
        if (inBounds && !isObstacle && !visited.has(posKey)) {
          visited.add(posKey);
          queue.push([...path, { row: newRow, col: newCol }]);
        }
      }
    }
  
    return []; // No path found
  }
  