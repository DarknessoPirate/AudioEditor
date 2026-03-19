import subprocess
import tempfile
from PySide6.QtCore import QThread, Signal
from pydub.utils import get_player_name

class PlaybackThread(QThread):
    finished = Signal()

    def __init__(self, audio):
        super().__init__()
        self.audio = audio
        self._process = None

    def run(self):
        # it exports pydub audio segment to temp file on disk so ffplay can play the audio from file and manage it
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            self.audio.export(f.name, format="wav")
            self._process = subprocess.Popen(
                [get_player_name(), "-nodisp", "-autoexit", "-hide_banner", f.name]
            )
            self._process.wait()
        self.finished.emit()

    def stop(self):
        if self._process:
            self._process.terminate()