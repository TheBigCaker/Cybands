from enum import Enum
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class JamRole(Enum):
    HUMAN = "HUMAN"
    AI = "AI"

class JamState(Enum):
    IDLE = "IDLE"
    COUNT_IN = "COUNT_IN"
    JAMMING = "JAMMING"
    ENDING = "ENDING"

class StyleEngine:
    """
    Manages the musical logic, state machine, and role swapping for Jammate.
    """
    def __init__(self):
        self.state = JamState.IDLE
        self.lead_role = JamRole.HUMAN
        self.bpm = 120
        self.current_bar = 0
        self.time_signature = (4, 4)

    def start_jam(self):
        if self.state == JamState.IDLE:
            self.state = JamState.COUNT_IN
            logger.info("Jam State: COUNT_IN")
            # Logic to transition to JAMMING after count-in would go here
            self.state = JamState.JAMMING
            return True
        return False

    def stop_jam(self):
        self.state = JamState.IDLE
        logger.info("Jam State: IDLE")

    def swap_roles(self):
        """Swaps who is leading (Human <-> AI)."""
        if self.lead_role == JamRole.HUMAN:
            self.lead_role = JamRole.AI
        else:
            self.lead_role = JamRole.HUMAN
        logger.info(f"Swapped Roles: Lead is now {self.lead_role.value}")

    def get_state_dict(self) -> Dict[str, Any]:
        """Returns current state for broadcasting."""
        return {
            "state": self.state.value,
            "lead": self.lead_role.value,
            "bpm": self.bpm,
            "bar": self.current_bar
        }

    def update_bar(self, bar: int):
        self.current_bar = bar
        # Potential logic: Swap roles every 8 bars?
        # if bar % 8 == 0:
        #     self.swap_roles()
