# Jammate v1 - Distributed AI Music Framework Blueprint

## Overview
Jammate v1 is a distributed, real-time AI music accompaniment system designed to act as a "Jam Partner". It splits the cognitive load between two machines:
1.  **Desktop (Brain/Server)**: Handles high-fidelity audio IO, recording, and musical structure (Guitar Pro 8 sync).
2.  **Laptop (Voice/Voice)**: Handles voice command intent parsing and localized MIDI control from the Helix pedalboard.

## Architecture

```mermaid
graph TD
    subgraph "Desktop (Brain)"
        D_Main[Desktop Main Loop]
        Audio[Audio Engine (ASIO)]
        GPX[GPX Engine (Guitar Pro)]
        Rec[Recorder]
        ZMQ_S[ZeroMQ Server]
    end

    subgraph "Laptop (Voice)"
        L_Main[Laptop Main Loop]
        Voc[Voice/Intent Engine (Gemma 3)]
        Helix[Helix MIDI Interface]
        ZMQ_C[ZeroMQ Client]
    end

    %% Comms
    L_Main <-->|UDP/ZeroMQ (Draft < 5ms)| D_Main
    
    %% Desktop Internal
    D_Main --> Audio
    D_Main --> GPX
    D_Main --> Rec
    
    %% Laptop Internal
    Helix --> L_Main
    Voc --> L_Main
```

## Communication Protocol (`comms.py`)
- **Technology**: ZeroMQ ( `pyzmq` ) PUB/SUB for state updates, REQ/REP for commands.
- **Latency Target**: < 5ms.
- **Transport**: UDP (via `PULL`/`PUSH` or `RADIO`/`DISH` if available, otherwise TCP with `NO_DELAY` for reliability usually preferred in ZMQ unless strictly UDP). *Note: Standard ZMQ uses TCP/IPC/INPROC. reliable Multicast (PGM) or UDP (RADIO/DISH) are options. For "High-speed UDP", we can use raw UDP sockets or ZMQ RADIO/DISH if supported by the build. We will default to TCP `NO_DELAY` for simplicity and robustness unless raw UDP is strictly required by the <5ms constraint, but TCP on a LAN is usually <<1ms. We will implement a `ZMQBridge` class.*

### Message Schema (JSON/Dict)
```json
{
  "timestamp": 123456789.0,
  "type": "COMMAND" | "STATE" | "METADATA",
  "payload": { ... }
}
```

## Component Breakdowns

### 1. Style Engine (`style_engine.py`)
- **Role Swapping**: Logic to determine who is "leading" (Human vs AI).
- **State Machine**: `IDLE` -> `COUNT_IN` -> `JAMMING` -> `ENDING`.
- **Extraction**:
    - `DrumExtractor`: Audio -> MIDI (Rhythm).
    - `BassExtractor`: Audio -> MIDI (Root notes).

### 2. Desktop (Server)
- **`desktop_main.py`**:
    - Initializes ASIO driver via `sounddevice`.
    - Loads `.gp` files via `gpx_engine.py`.
    - Manages circular buffer for recording (30 min max).
    - Broadcasts `BPM`, `TimeSignature`, `CurrentBar` to Laptop.

### 3. Laptop (Client)
- **`laptop_main.py`**:
    - Listens to `Helix USB Ch 7/8` for voice commands.
    - **Intent Engine**: Triggers `Gemma 3 3n` (OpenVINO) when voice activity is detected > threshold.
    - **Helix MIDI**: Maps MIDI CC messages to Python functions (e.g., `CC 64` -> `Toggle Record`).

## Directory Structure
```
Jammate/
├── README.md
├── requirements.txt
├── blueprint.md
├── src/
│   ├── __init__.py
│   ├── comms.py          # ZeroMQ bridge
│   ├── style_engine.py   # Musical Logic
│   ├── desktop/
│   │   ├── __init__.py
│   │   ├── desktop_main.py
│   │   ├── audio_engine.py
│   │   ├── gpx_engine.py
│   │   └── recorder.py
│   └── laptop/
│       ├── __init__.py
│       ├── laptop_main.py
│       ├── voice_engine.py
│       └── midi_engine.py
└── tests/
```

## Critical Latency Path
1.  **Helix MIDI Press** -> Laptop USB -> `laptop_main.py` -> ZMQ -> `desktop_main.py` -> **Action**.
    - Must be perceptible as "instant".
2.  **Voice Command** -> STT -> LLM -> Intent -> ZMQ -> Desktop.
    - Latency allowable (~500ms-1s).

