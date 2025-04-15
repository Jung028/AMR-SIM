# AMR-SIM

**AMR-SIM** is an AI-powered simulation tool for planning and testing Autonomous Mobile Robot (AMR) systems in warehouse environments. It helps pre-sales engineers and warehouse planners simulate different scenarios to meet specific throughput goals, robot types, and layout configurations.

> 🚧 This project is still in progress — currently focused on building core features like throughput configuration, dynamic map layout, and algorithm selection.

---

## 🛠 Tech Stack

- **Frontend:** React.js, TypeScript, Tailwind CSS  
- **Backend:** Python, FastAPI  
- **Database & Tools:** Google Sheets API, PostgreSQL (planned), Docker  
- **AI & Analysis (Upcoming):** NumPy, pandas, scikit-learn, HuggingFace, LangChain  

---

## ✅ Current Features

- **Google Sheets Integration**
  - Users can input desired throughput, number of robots, and other warehouse configurations.
  - Data is synced with the front-end UI for real-time updates.

- **Custom Map Creation**
  - Define robot positions, stations, shelves, chargers, and high-traffic zones.
  - Interactive grid-based layout using data from the spreadsheet.

- **Algorithm Selection Interface**
  - Choose from multiple planning algorithms like A*, Dijkstra, Genetic, ACO, DWA.
  - Hover tooltips explain advantages and drawbacks of each method.

---

## 🧩 Coming Soon

- Order simulation using Geek+ Picking System API standard (v3.4.2)
- AI-powered chatbot assistant for system guidance and Q&A
- Visualization dashboard with heatmaps and performance insights
- Full simulation environment with robot coordination logic
- Web app login & spreadsheet sync for multiple users

---

## 📷 Preview

### Spreadsheet Integration  
![Desired Output Table](https://github.com/user-attachments/assets/f772aa76-8585-4b04-a32d-07fd7b6fb971)

### Excel Throughput Calculator  
![Throughput Calculator](https://github.com/user-attachments/assets/27b400f7-56fa-40fd-96b2-0cc24ca4d571)

### Custom Map Grid  
![Map Grid](https://github.com/user-attachments/assets/87bcca47-eea8-412b-83e2-fe1e3d9d8720)

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/your-username/amr-sim.git
cd amr-sim

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
npm run dev
```
