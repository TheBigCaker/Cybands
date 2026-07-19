import time
import argparse
import logging
from src.comms import ZMQBridge, CommsMode
from src.laptop.midi_engine import MidiEngine
from src.laptop.voice_engine import VoiceEngine

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LaptopMain")

def main():
    parser = argparse.ArgumentParser(description="Jammate Laptop (Voice/Voice)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="IP address of Desktop (Brain)")
    args = parser.parse_args()

    # Initialize Components
    comms = ZMQBridge(mode=CommsMode.CLIENT, host=args.host)
    midi = MidiEngine(device_name_substring="Helix")
    voice = VoiceEngine()

    # Handlers
    def on_midi_cc(channel, cc, value):
        """Map Helix FS/Exp switches to Commands."""
        # Example mappings
        if cc == 64 and value == 127: # Sustain pedal / FS1
            logger.info("MIDI Trigger: Toggle Record")
            comms.send_command("TOGGLE_RECORD")
        elif cc == 65 and value == 127: 
            logger.info("MIDI Trigger: Start Jam")
            comms.send_command("START_JAM")
        elif cc == 66 and value == 127:
            logger.info("MIDI Trigger: Stop Jam")
            comms.send_command("STOP_JAM")

    def on_server_state(state):
        # Update UI or LED rings on Helix based on state
        # For now, just log unique states
        # logger.debug(f"State Update: {state}")
        pass

    midi.callback = on_midi_cc
    comms.state_handler = on_server_state

    # Start Services
    try:
        comms.start()
        midi.start()
        voice.load_model()
        
        logger.info(f"Laptop Client Connected to {args.host}. Ready.")
        
        while True:
            # Main Loop
            # Check for voice activity (not implemented here, assumes push-to-talk or always listening thread)
            
            # Simulate a voice command input for testing via console input in a real app
            # Here we just sleep
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        comms.stop()
        midi.stop()
        logger.info("Shutdown Complete.")

if __name__ == "__main__":
    main()
