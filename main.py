import sys
import soundfile as sf
import sounddevice as sd
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
)
from PySide6.QtCore import QThread, Signal


class PlaybackThread(QThread):
    finished = Signal()

    def __init__(self, data, samplerate):
        super().__init__()
        self.data = data
        self.samplerate = samplerate

    def run(self):
        sd.play(self.data, self.samplerate)
        sd.wait()
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Editor Template")
        self.audio_data = None
        self.samplerate = None
        self.thread = None

        layout = QVBoxLayout()

        self.info_label = QLabel("No file loaded.")
        layout.addWidget(self.info_label)

        load_btn = QPushButton("Load Audio File")
        load_btn.clicked.connect(self.load_file)
        layout.addWidget(load_btn)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_audio)
        self.play_btn.setEnabled(False)
        layout.addWidget(self.play_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio", "", "Audio Files (*.mp3 *.wav *.ogg *.flac)"
        )
        if not path:
            return
        self.audio_data, self.samplerate = sf.read(path)
        duration = len(self.audio_data) / self.samplerate
        channels = 1 if self.audio_data.ndim == 1 else self.audio_data.shape[1]
        self.info_label.setText(
            f"Loaded: {path.split('/')[-1]}\n"
            f"Duration: {duration:.2f}s | "
            f"Channels: {channels} | "
            f"Sample rate: {self.samplerate}Hz"
        )
        self.play_btn.setEnabled(True)

    def play_audio(self):
        if self.audio_data is None:
            return
        self.play_btn.setEnabled(False)
        self.thread = PlaybackThread(self.audio_data, self.samplerate)
        self.thread.finished.connect(lambda: self.play_btn.setEnabled(True))
        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 200)
    window.show()
    sys.exit(app.exec())
