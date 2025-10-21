# 🧠 Static-SignOff-Simulator
A simplified educational project inspired by Real Intent’s static sign-off tools.  
It demonstrates how **CDC**, **RDC**, and visualization concepts work using pure Python.

---

## 🔍 Overview
Modern chips contain many sections (“clock domains”) that run at different speeds.  
When signals travel between them, they can cause errors if not synchronized.  
This project models those interactions as a **graph** and highlights potential hazards.

| Term | Meaning | Analogy |
|------|----------|----------|
| **CDC** | Clock-Domain Crossing — a signal moves from one timing domain to another | Sending data between offices in different time zones |
| **RDC** | Reset-Domain Crossing — reset signals affecting other domains asynchronously | Restarting one subsystem while others keep running |
| **Static Sign-Off** | Final structural checks before manufacturing | Blueprint QA before building a car |

---

## 🧰 Features
- Reads a small design from `example_design.json`
- Detects:
  - **CDC paths** (signal source and destination on different clocks)
  - **RDC paths** (reset sources/destinations differ)
- Classifies paths as:
  - ✅ Safe (known synchronizer)
  - ❌ Unsafe (direct or unguarded crossing)
- Exports:
  - `report.csv` summary  
  - `signoff_graph.png` PyGraphviz diagram

---

## ⚙️ Installation
```bash
git clone https://github.com/yourusername/Static-SignOff-Simulator.git
cd Static-SignOff-Simulator
pip install -r requirements.txt
