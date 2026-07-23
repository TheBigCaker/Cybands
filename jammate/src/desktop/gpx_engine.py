# Copyright (c) 2026 David Baker (Delta Vector) and the Sol Mech R&D team.
# Licensed under the Business Source License 1.1 (BSL 1.1). See LICENSE.md in the project root for license information.

import logging
import time

logger = logging.getLogger(__name__)

class GPXEngine:
    """
    Manages synchronization with Guitar Pro 8 (or reads .gp files).
    For v1, this acts as a tempo/structure master based on loaded metadata.
    """
    def __init__(self):
        self.current_file = None
        self.bpm = 120
        self.playing = False
        self.start_time = 0
        self.time_signature = (4, 4)

    def load_file(self, filepath: str):
        """
        Loads a .gp file (or metadata sidecar).
        """
        logger.info(f"Loading GPX file: {filepath}")
        self.current_file = filepath
        # Mock parsing logic
        self.bpm = 120 
        self.time_signature = (4, 4)

    def play(self):
        if not self.playing:
            self.playing = True
            self.start_time = time.time()
            logger.info("GPX Playback Started")

    def stop(self):
        self.playing = False
        logger.info("GPX Playback Stopped")

    def get_transport_info(self):
        """Returns current bar, beat, tempo."""
        if not self.playing:
            return {"bar": 0, "beat": 0, "bpm": self.bpm}
        
        elapsed = time.time() - self.start_time
        # Simple beat calculation for mock
        bps = self.bpm / 60.0
        total_beats = elapsed * bps
        bar = int(total_beats / self.time_signature[0]) + 1
        beat = (total_beats % self.time_signature[0]) + 1
        
        return {
            "bar": bar,
            "beat": beat,
            "bpm": self.bpm
        }
