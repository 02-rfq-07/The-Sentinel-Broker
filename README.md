# 🛡️ The Sentinel Broker (Prototype)

> An autonomous, AI-driven middleware platform enabling Machine-to-Machine (M2M) bidding for ephemeral 5G network slices.

This repository contains the **Phase I Prototype** of the Sentinel Broker. It serves as a lightweight, standalone Python simulation of a real-time, priority-weighted auction system for allocating high-performance 5G network slices to industrial IoT devices during critical events.

## 📖 Overview

Traditional 5G slicing is sold through static, long-term contracts. The Sentinel Broker introduces a **pay-per-event monetization model**. Using real-time device telemetry, autonomous agents programmatically "buy" high-priority network lanes (VIP Slices) from the telecom provider when an application needs guaranteed performance (e.g., remote surgery, autonomous drone landing). 

## 🚀 Core Features

* **Priority-Weighted Auction Mechanism:** Bids are evaluated based on a dynamic priority formula: `P = (0.6 * Criticality) + (0.4 * Urgency)`.
* **Pre-emption Logic:** High-priority critical events can automatically pre-empt lower-priority devices dynamically when total bandwidth is exhausted.
* **Device Telemetry Simulation:** Synthesizes realistic network degradation (RSRQ, Jitter) and task intent across different industries (Healthcare, Manufacturing, Enterprise).
* **Mock 5G NEF API:** A FastAPI server simulating a Telco's Network Exposure Function to toggle network states and limit bandwidth.

## 🗂️ Project Structure

* **`main.py`**: The **5G Core Simulator**. A FastAPI server that mocks the Network Exposure Function (NEF). It manages total bandwidth capacity, tracks active slices, and exposes `/provision_slice` and `/release_slice` endpoints.
* **`agent.py`**: The **Autonomous Brain**. A Python script simulating the Edge Agent. It polls device telemetry, calculates priority scores, and decides whether to bid, wait, or pre-empt existing network slices.
* **`telemetry.py`**: The **Device Simulator**. Generates synthetic data for various IoT devices (Healthcare UAV, Factory Robot, etc.), including network metrics and task states.
* **`Visualize.html`**: A dynamic visual dashboard demonstrating the Priority Score Auction mechanism. You can use sliders to adjust criticality and jitter and see the auction sorting in real-time.
* **`Prompt.txt`**: The original project specification and phased roadmap.

## ⚙️ Getting Started

### Prerequisites
* Python 3.11+

Install the required dependencies:
```bash
pip install fastapi uvicorn requests
```

### Running the Simulation

You will need two terminal windows to run the full simulation locally.

**1. Start the 5G Core Simulator (Broker API):**
In the first terminal, start the FastAPI server:
```bash
uvicorn main:app --reload
```
*The mock network tower will start on `http://127.0.0.1:8000`.*

**2. Start the Sentinel Agent:**
In the second terminal, run the autonomous agent:
```bash
python agent.py
```
The agent will begin polling the telemetry of the simulated devices, calculate their priority scores, and bid for bandwidth against the FastAPI server. You will see real-time logs of the agent's decisions (`BOUGHT`, `RELEASED`, `PRE-EMPTED`, `QUEUED`).

**3. Interactive Visualization:**
Open `Visualize.html` in any web browser to interactively tweak the Priority Score formula with sliders and see how the auction mechanism ranks competing devices in real-time.

## 🛑 Shutting Down
To gracefully stop the agent, press `Ctrl+C` in its terminal. It will automatically generate a **Session Impact Report**, detailing total interventions, network efficiency gains, and simulated micro-monetization revenue.

## 📄 License
MIT License
