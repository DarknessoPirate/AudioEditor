import sys
from pydub import AudioSegment
from pydub.playback import play
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QSlider,
)
from PySide6.QtCore import Qt, QThread, Signal


class PlaybackThread(QThread):
    finished = Signal()

    def __init__(self, audio):
        super().__init__()
        self.audio = audio

    def run(self):
        play(self.audio)
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Editor Template")
        self.audio = None
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

        self.volume_label = QLabel("Volume: 100%")
        layout.addWidget(self.volume_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 150)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"Volume: {v}%")
        )
        layout.addWidget(self.volume_slider)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio", "", "Audio Files (*.mp3 *.wav *.ogg *.flac)"
        )
        if not path:
            return
        self.audio = AudioSegment.from_file(path)
        duration = len(self.audio) / 1000.0
        channels = self.audio.channels
        samplerate = self.audio.frame_rate

        self.info_label.setText(
            f"Loaded: {path.split('/')[-1]}\n"
            f"Duration: {duration:.2f}s | "
            f"Channels: {channels} | "
            f"Sample rate: {samplerate}Hz"
        )
        self.play_btn.setEnabled(True)

    def play_audio(self):
        if self.audio is None:
            return
        volume = self.volume_slider.value()
        import math
        db_change = 20 * math.log10(volume / 100) if volume > 0 else -120
        audio = self.audio + db_change
        self.play_btn.setEnabled(False)
        self.volume_slider.setEnabled(False)
        self.thread = PlaybackThread(audio)
        self.thread.finished.connect(lambda: self.play_btn.setEnabled(True))
        self.thread.finished.connect(lambda: self.volume_slider.setEnabled(True))
        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 200)
    window.show()
    sys.exit(app.exec())
