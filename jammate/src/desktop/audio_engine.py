# Copyright (c) 2026 David Baker (Delta Vector) and the Sol Mech R&D team.
# Licensed under the Business Source License 1.1 (BSL 1.1). See LICENSE.md in the project root for license information.

import sounddevice as sd
import numpy as np
import logging
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class AudioEngine:
    """
    Manages audio input/output using SoundDevice (PortAudio/ASIO).
    """
    def __init__(self, device_name: Optional[str] = None, samplerate: int = 48000, channels: int = 8, blocksize: int = 512):
        self.device_name = device_name
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.stream: Optional[sd.InputStream] = None
        self.active = False
        
        # Callbacks
        self.on_audio_block: Optional[Callable[[np.ndarray], None]] = None

    def list_devices(self):
        print(sd.query_devices())

    def start(self):
        """Starts the audio stream."""
        logger.info(f"Starting AudioEngine on device: {self.device_name or 'Default'}")
        
        try:
            self.stream = sd.InputStream(
                device=self.device_name,
                channels=self.channels,
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                callback=self._callback
            )
            self.stream.start()
            self.active = True
            logger.info("Audio Stream Started")
        except Exception as e:
            logger.error(f"Failed to start Audio Stream: {e}")
            raise

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.active = False
        logger.info("Audio Stream Stopped")

    def _callback(self, indata, frames, time_info, status):
        if status:
            logger.warning(f"Audio Status: {status}")
        
        if self.on_audio_block:
            # indata is (frames, channels)
            self.on_audio_block(indata.copy())
