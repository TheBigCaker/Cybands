import soundfile as sf
import numpy as np
import logging
import threading
import queue
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class Recorder:
    """
    Handles recording of multi-channel audio to disk.
    Uses a queue to offload file writing from the audio callback thread.
    """
    def __init__(self, output_dir: str = "recordings", samplerate: int = 48000, channels: int = 8):
        self.output_dir = output_dir
        self.samplerate = samplerate
        self.channels = channels
        self.recording = False
        self.file: Optional[sf.SoundFile] = None
        self.write_queue = queue.Queue()
        self._thread = threading.Thread(target=self._write_loop, daemon=True)
        self._thread.start()

    def start_recording(self):
        if self.recording:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/jam_session_{timestamp}.wav"
        
        try:
            import os
            os.makedirs(self.output_dir, exist_ok=True)
            self.file = sf.SoundFile(filename, mode='w', samplerate=self.samplerate, channels=self.channels)
            self.recording = True
            logger.info(f"Recording started: {filename}")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")

    def stop_recording(self):
        if not self.recording:
            return
            
        logger.info("Stopping recording...")
        self.recording = False
        # Wait for queue to drain in loop or just close file eventually
        # We handle closure in the write loop when we see recording is False and queue is empty

    def on_audio_data(self, data: np.ndarray):
        """Callback from AudioEngine."""
        if self.recording:
            self.write_queue.put(data)

    def _write_loop(self):
        while True:
            try:
                data = self.write_queue.get(timeout=0.1)
                if self.file and not self.file.closed:
                    self.file.write(data)
                self.write_queue.task_done()
            except queue.Empty:
                if not self.recording and self.file and not self.file.closed:
                    # Flush and close
                    self.file.close()
                    logger.info("Recording file closed.")
                    self.file = None
            except Exception as e:
                logger.error(f"Error writing audio file: {e}")
