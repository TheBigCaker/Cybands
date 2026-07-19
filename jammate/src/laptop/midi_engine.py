import rtmidi
import logging
from typing import Callable, Optional, Dict

logger = logging.getLogger(__name__)

class MidiEngine:
    """
    Handles MIDI input from Helix Floor (or other devices).
    Maps CC messages to actions.
    """
    def __init__(self, device_name_substring: str = "Helix"):
        self.device_name_substring = device_name_substring
        self.midi_in = rtmidi.MidiIn()
        self.port_name: Optional[str] = None
        self.callback: Optional[Callable[[int, int, int], None]] = None # (channel, cc, value)

    def list_ports(self):
        ports = self.midi_in.get_ports()
        logger.info(f"Available MIDI Ports: {ports}")
        return ports

    def start(self):
        ports = self.midi_in.get_ports()
        for i, port in enumerate(ports):
            if self.device_name_substring.lower() in port.lower():
                self.midi_in.open_port(i)
                self.port_name = port
                self.midi_in.set_callback(self._midi_callback)
                logger.info(f"Connected to MIDI Device: {port}")
                return
        
        logger.warning(f"No MIDI device found matching '{self.device_name_substring}'. using virtual/mock.")
        # self.midi_in.open_virtual_port("Jammate Virtual In")

    def stop(self):
        if self.midi_in.is_port_open():
            self.midi_in.close_port()

    def _midi_callback(self, event, data=None):
        message, deltatime = event
        if len(message) == 3:
            status, data1, data2 = message
            # Check for Control Change (0xB0 - 0xBF)
            if 0xB0 <= status <= 0xBF:
                channel = status & 0x0F
                cc_num = data1
                value = data2
                
                if self.callback:
                    self.callback(channel, cc_num, value)
