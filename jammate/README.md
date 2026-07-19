# Jammate v1

**Distributed AI Jam Partner Framework**

Jammate is a real-time, distributed music accompaniment system designed to split cognitive load between a high-performance **Desktop (Brain)** and a **Laptop (Visual/Voice Interface)**.

## Architecture
- **Desktop (Server)**:
  - Handles Audio monitoring (8 channels via UMC1820).
  - Runs Guitar Pro 8 synchronization (`gpx_engine`).
  - Manages high-fidelity recording.
- **Laptop (Client)**:
  - Captures Voice Commands.
  - Runs Local AI (Gemma 3) for Intent Parsing.
  - Interfaces with Helix Floor via MIDI.

## Setup

### Prerequisites
- Python 3.10+
- ZeroMQ
- OpenAI Gemma 3 (for Laptop)

### Installation
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/jammate.git
    cd jammate
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Start Desktop (Brain)
On the main desktop machine:
```bash
python -m src.desktop.desktop_main
```

### 2. Start Laptop (Client)
On the laptop/interface machine:
```bash
python -m src.laptop.laptop_main --host <DESKTOP_IP>
```
*Note: Ensure both machines are on the same LAN.*

## Configuration
Edit `src/config.py` (to be created) for IP addresses, ports, and audio device IDs.

## License
MIT
