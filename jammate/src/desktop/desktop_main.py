# Copyright (c) 2026 David Baker (Delta Vector) and the Sol Mech R&D team.
# Licensed under the Business Source License 1.1 (BSL 1.1). See LICENSE.md in the project root for license information.

import time
import logging
import argparse
from src.comms import ZMQBridge, CommsMode
from src.style_engine import StyleEngine, JamState
from src.desktop.audio_engine import AudioEngine
from src.desktop.recorder import Recorder
from src.desktop.gpx_engine import GPXEngine

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DesktopMain")

def main():
    parser = argparse.ArgumentParser(description="Jammate Desktop (Brain)")
    parser.add_argument("--device", type=str, help="ASIO Device Name", default=None)
    args = parser.parse_args()

    # Initialize Components
    comms = ZMQBridge(mode=CommsMode.SERVER)
    style = StyleEngine()
    
    # Audio & Recorder
    recorder = Recorder()
    audio = AudioEngine(device_name=args.device)
    audio.on_audio_block = recorder.on_audio_data # Pipe audio to recorder
    
    # GPX
    gpx = GPXEngine()

    # Command Handlers
    def handle_command(msg):
        cmd = msg.get("cmd")
        payload = msg.get("payload", {})
        logger.info(f"Received Command: {cmd}")
        
        if cmd == "START_JAM":
            if style.start_jam():
                recorder.start_recording()
                gpx.play()
                return {"status": "started"}
            return {"status": "failed", "reason": "Already running"}
            
        elif cmd == "STOP_JAM":
            style.stop_jam()
            recorder.stop_recording()
            gpx.stop()
            return {"status": "stopped"}
            
        elif cmd == "TOGGLE_RECORD":
            if recorder.recording:
                recorder.stop_recording()
                return {"status": "recording_stopped"}
            else:
                recorder.start_recording()
                return {"status": "recording_started"}
                
        return {"status": "unknown_command"}

    comms.command_handler = handle_command

    # Start Services
    try:
        comms.start()
        # audio.start() # Uncomment when real ASIO device is present or testing
        logger.info("Desktop System Ready. Waiting for commands...")
        
        while True:
            # Main Loop: Broadcast State
            transport = gpx.get_transport_info()
            
            state = style.get_state_dict()
            state.update(transport)
            state["recording"] = recorder.recording
            
            comms.broadcast_state(state)
            
            time.sleep(0.05) # 20Hz update rate for UI
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        comms.stop()
        audio.stop()
        recorder.stop_recording()
        logger.info("Shutdown Complete.")

if __name__ == "__main__":
    main()
