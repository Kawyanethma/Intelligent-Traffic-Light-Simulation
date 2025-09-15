# Intelligent Traffic Light System Using Machine Learning

This repository contains a **simulation-driven Intelligent Traffic Light System** that optimizes traffic flow in urban environments using **machine learning, image processing, and reinforcement learning**. The system simulates a four-way junction, dynamically adjusts traffic signals based on vehicle density, and evaluates performance with real-time data logging and visualization.

##  Credits

This project is **built upon and inspired by** the excellent work from: [mihir-m-gandhi / Basic-Traffic-Intersection-Simulation](https://github.com/mihir-m-gandhi/Basic-Traffic-Intersection-Simulation)

I extended it with:
- **Reinforcement Learning integration** for adaptive signal timing.
- **Data logging & visualization** (waiting time, throughput, queue lengths).
- **Tkinter-based control panel** for real-time parameter changes.


## 📌 Project Overview

- **Problem**: Sri Lanka’s current fixed-time traffic lights do not adapt to congestion, causing long waits, high fuel use, and inefficiencies.
- **Solution**: A simulation-based adaptive system that adjusts green light times in real time using reinforcement learning and traffic data.
- **Goal**: Develop a scalable, low-cost solution to improve urban traffic flow and reduce congestion.



## 🎯 Objectives

- Review existing adaptive traffic control technologies.
- Develop a **Python-based simulation** with real-time data collection.
- Implement **reinforcement learning** for adaptive timing optimization.
- Evaluate performance using metrics such as **average waiting time, throughput, and queue length**.


## ⚙️ Features

- **Traffic Simulation**: Four-way junction modeled with variable traffic densities.
- **Dynamic Signal Adjustment**: Real-time green light optimization.
- **User Control Panel**: Adjust vehicle types, duration, green light times, and logging frequency.
- **Data Logging**: Automatic recording of throughput, queue lengths, and delays.
- **Visualization**: Pygame-based live graphics + Matplotlib performance plots.
- **Reinforcement Learning Agent**: Learns to minimize waiting times across lanes.(Testing on `RLModelIntergration`, Contributions are welcome)

## 📸 Screenshots
<table>
  <tr>
    <th>
      🟢 Simulation Interface (Pygame)
    </th>
     <th>
      🖥  Start Screen (Tkinter)
    </th>
<tr>
  <td width="70%">
    <p align="center">
      <img src="https://github.com/user-attachments/assets/00ae0370-81f4-4175-b481-7c530ed2f42e" alt="Simulation Interface" width="95%">
    </p>
  </td>
  <td width="30%">
  <p align="center">
    <img src="https://github.com/user-attachments/assets/071546a9-dcb7-41b8-a1ec-0536188e32b7" alt="Control Panel" width="95%">
  </p>
  </td>
</tr>
<tr>
  <th>
    🔢 Real-time Metrics
  </th>
   <th>
    📊 Plots
  </th>
</tr>
<tr>
  <td>
    <p align="center">
      <img src="https://github.com/user-attachments/assets/15dd9cdf-ac2e-4da6-ae97-220570efc81f" alt="Metrics Plot 1" width="95%">
    </p>
  </td>
  <td>
    <p align="center"> 
    <img src="https://github.com/user-attachments/assets/b29196ad-85c4-4bdb-afc9-f154c84c2343" alt="Metrics Plot 2" width="95%"> </p>
    </td>
  </tr>
</table>

## 🚦 Intelligent Mode vs Normal Mode

### 🔴 Normal Mode (Fixed-Time Signals)

**Operation**: Traffic lights follow a **predefined cycle** (e.g., 30s green, 5s yellow, 30s red).
#### **Pros**:
- Simple, predictable, low computing cost.
- Works without sensors or data.
#### **Cons**:
- Does not adapt to **real-time traffic density**.
- Causes long waits in empty lanes.
- Leads to congestion, fuel waste, and inefficiency.


### 🟢 Intelligent Mode (Adaptive Signals)

**Operation**: Traffic lights are controlled by the **simulation’s ML/optimization engine**.
- Vehicle density is tracked in real time.
- Reinforcement learning allocates green time dynamically.(Testing on `RLModelIntergration`)
- Historical + live data (waiting time, queue length, throughput) influence decisions.
#### **Pros**:
- Optimizes average waiting time across all lanes.
- Reduces congestion and idle fuel consumption.
- Scales better for multi-junction coordination.

#### **Cons**:
- Requires data collection & computation.
- Needs initial training or calibration for new environments.

| Scenario                | Normal Mode                                                     | Intelligent Mode                                     |
| ----------------------- | --------------------------------------------------------------- | ---------------------------------------------------- |
| **Low traffic (night)** | Empty roads still cycle through red lights.                     | Detects no vehicles → keeps green or skips cycle.    |
| **Rush hour**           | All lanes get equal time (some overflow, others underutilized). | Dynamically gives more time to congested lanes.      |
| **Mixed flow**          | Pedestrian & vehicle flow not prioritized.                      | Can integrate pedestrian & emergency priority rules. |


## 🗂 Repository Structure

```
├── src/
│   ├── vehicle_generator.py      # Code for generating vehicles in simulation
│   ├── data_logger.py            # Logs throughput, wait times, queues
│   ├── user_controls.py          # Tkinter-based control panel for parameters
│   ├── simulation.py             # Main entry point
│   └── rl_agent.py               # Reinforcement learning optimization module
├── docs/
│   └── thesis.pdf                # Full research thesis (reference)
├── results/
│   ├── simulation_stats.txt      # Example raw data logs
│   └── plots.png                 # Performance visualizations
└── README.md

```
## 💻 Code Snippets

### Vehicle Generation

```python
import random

def generate_vehicle(lanes):
    vehicle_types = ["car", "bus", "lorry", "bike"]
    lane = random.choice(lanes)
    vehicle = {
        "type": random.choice(vehicle_types),
        "speed": random.randint(20, 60),
        "lane": lane,
        "arrival_time": random.uniform(0, 5)
    }
    return vehicle

```

### Data Logging

```python
import time

def log_data(file, stats):
    with open(file, "a") as f:
        f.write(f"{time.time()},{stats['waiting_time']},{stats['queue_length']},{stats['throughput']}\n")

```

### User Control & Parameters

```python
import tkinter as tk

def setup_controls(simulation):
    root = tk.Tk()
    tk.Label(root, text="Green Light Duration (s)").pack()
    duration = tk.IntVar(value=10)
    tk.Entry(root, textvariable=duration).pack()

    def update():
        simulation.set_green_time(duration.get())
    tk.Button(root, text="Apply", command=update).pack()
    root.mainloop()

```

## 🛠 Tech Stack

- **Language**: Python
- **Libraries**: Tkinter, Pygame, Pandas, Matplotlib
- **IDE**: PyCharm

## 📦 Prerequisites

Before running the simulation, ensure you have the following installed:
**Python 3.10+**
Verify with:
```bash
python --version
```

**Required Libraries** (you can installed via `requirements.txt`)
- `pygame` – for simulation rendering
- `tkinter` – for GUI (comes with Python, but install separately on some Linux distros: `sudo apt-get install python3-tk`)
- `matplotlib` – for plots
- `pandas` – for data handling

## 🚀 How to Clone & Run

### 1. Clone Repository

```bash
git clone https://github.com/your-username/intelligent-traffic-light-system.git
cd intelligent-traffic-light-system
```
### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
#### requirements.txt
```
pygame
matplotlib
pandas
# Tkinter is included in the standard Python library, no need to install separately
```
### 4. Run Simulation

```bash
python src/simulation.py
```

### 5. Modify Parameters

- Using control panel (Pygame GUI).
- Adjust **vehicle types, signal timings, simulation duration, or logging frequency**.
- Observe real-time updates in the Pygame simulation window.
- Intelligent Mode amd Normal Mode


## ✅ Testing

- Unit tests for **vehicle generation, signal adjustment, data logging**.
- Performance metrics validation for **waiting times, throughput, queue lengths**

## 🤝 Contributing

We welcome contributions to improve the **Intelligent Traffic Light System** project!

- Current testing focus: **`RLModelIntegration` branch**
	- This branch contains experimental work on reinforcement learning integration.
	- Feedback, bug reports, and improvements are highly encouraged.

- How to contribute:
	1. Fork the repository.
	2. Create a new branch:  
		```bash
		git checkout -b feature-name
		```
	3. Commit your changes and push:
		```bash
		git commit -m "Added new feature/fix"
		git push origin feature-name
