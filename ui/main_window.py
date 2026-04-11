import math
from pydub import AudioSegment
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QCheckBox,
    QRadioButton,
)
from ui.components import getSlider, getButton, getRadioButtonsGroup, getComboBox, getLoudnessPlot
from playback import PlaybackThread

# Główne okno aplikacji — zawiera cały interfejs użytkownika i logikę sterowania odtwarzaniem.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Editor Template")
        self.audio = None   # załadowany plik audio jako obiekt AudioSegment
        self.thread = None  # aktywny wątek odtwarzania (PlaybackThread)

        layout = QVBoxLayout()

        self.info_label = QLabel("No file loaded.")
        layout.addWidget(self.info_label)
        layout.addWidget(getButton("Load Audio File", self.load_file))

        # Przyciski Play/Stop — domyślnie nieaktywne do momentu załadowania pliku.
        self.play_btn = getButton("Play", self.play_audio)
        self.play_btn.setEnabled(False)
        layout.addWidget(self.play_btn)

        self.stop_btn = getButton("Stop", self.stop_audio)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        # Suwak głośności w zakresie 0–150% (wartość domyślna: 100%).
        self.volume_label = QLabel("Volume: 100%")
        layout.addWidget(self.volume_label)
        slider_range = (0, 150)
        slider_default_val = 100
        self.volume_slider = getSlider(slider_range, slider_default_val)
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"Volume: {v}%")
        )
        layout.addWidget(self.volume_slider)

        # Suwak panoramy (pan) w zakresie -100 (lewo) do 100 (prawo), 0 = środek.
        self.pan_label = QLabel("Pan: Center")
        layout.addWidget(self.pan_label)
        self.pan_slider = getSlider((-100, 100), 0)
        self.pan_slider.valueChanged.connect(self.on_pan_changed)
        layout.addWidget(self.pan_slider)

        self.reverse_checkbox = QCheckBox("Play in reverse")
        layout.addWidget(self.reverse_checkbox)

        # Grupa przycisków do wyboru trybu kanałów — stereo lub mono.
        self.stereo_radio = QRadioButton("Stereo")
        self.mono_radio = QRadioButton("Mono")
        self.stereo_radio.setChecked(True)
        self.channel_group = getRadioButtonsGroup([self.stereo_radio, self.mono_radio])
        channel_layout = QHBoxLayout()
        channel_layout.addWidget(self.stereo_radio)
        channel_layout.addWidget(self.mono_radio)
        layout.addLayout(channel_layout)

        # Lista rozwijana do wyboru jakości dźwięku (częstotliwość próbkowania w Hz).
        # Niższa częstotliwość = gorsza jakość, mniejszy rozmiar pliku.
        layout.addWidget(QLabel("Sound quality"))
        self.quality_combo = getComboBox([
            ("Default", None),
            ("Medium (22050 Hz)", 22050),
            ("Worst (8000 Hz)", 8000),
            ("Unlistenable (2000 Hz)", 2000),
        ])
        layout.addWidget(self.quality_combo)

        # Przycisk eksportu i lista wyboru formatu pliku wyjściowego.
        self.export_btn = getButton("Export Audio", lambda: self.export_to(self.format_combo.currentData()))
        self.export_btn.setEnabled(False)
        self.format_combo = getComboBox([
            ("WAV", "wav"),
            ("MP3", "mp3"),
            ("OGG", "ogg"),
            ("FLAC", "flac"),
        ])
        export_layout = QHBoxLayout()
        export_layout.addWidget(self.export_btn)
        export_layout.addWidget(self.format_combo)
        layout.addLayout(export_layout)

        # Qt wymaga osadzenia layoutu w widgecie — ustawiamy go jako centralny widget okna.
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self):
        # Otwieramy dialog wyboru pliku — filtrujemy tylko obsługiwane formaty audio.
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio", "", "Audio Files (*.mp3 *.wav *.ogg *.flac)"
        )
        if not path:
            return

        self.audio: AudioSegment = AudioSegment.from_file(path)

        duration = len(self.audio) / 1000.0  # pydub zwraca długość w milisekundach, przeliczamy na sekundy
        channels = self.audio.channels
        samplerate = self.audio.frame_rate
        # Aktualizujemy pierwszą opcję listy jakości, żeby pokazywała oryginalną częstotliwość pliku.
        self.quality_combo.setItemText(0, f"Default ({samplerate} Hz)")
        self.quality_combo.setItemData(0, samplerate)

        self.info_label.setText(
            f"Loaded: {path.split('/')[-1]}\n"
            f"Duration: {duration:.2f}s | "
            f"Channels: {channels} | "
            f"Sample rate: {samplerate}Hz"
        )

        # Resetujemy wszystkie kontrolki do wartości domyślnych przy każdym załadowaniu pliku.
        self.volume_slider.setValue(100)
        self.pan_slider.setValue(0)
        self.reverse_checkbox.setChecked(False)
        self.stereo_radio.setChecked(True)
        self.quality_combo.setCurrentIndex(0)
        self.format_combo.setCurrentIndex(0)
        self.update_loudness_plot(self.audio)
        self.play_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

    def export_to(self, fmt: str):
        if self.audio is None:
            return
        filter_map = {"wav": "WAV (*.wav)", "mp3": "MP3 (*.mp3)", "ogg": "OGG (*.ogg)", "flac": "FLAC (*.flac)"}
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Audio", "", filter_map.get(fmt, "WAV (*.wav)")
        )
        if not path:
            return
        # Upewniamy się, że plik ma poprawne rozszerzenie — dopisujemy je jeśli brakuje.
        if not path.lower().endswith(f".{fmt}"):
            path = f"{path}.{fmt}"
        audio = self.apply_effects_to_audio()
        audio.export(path, format=fmt)

    def play_audio(self):
        if self.audio is None:
            return

        audio = self.apply_effects_to_audio()

        self.update_loudness_plot(audio)

        # Blokujemy kontrolki na czas odtwarzania, żeby użytkownik nie zmieniał parametrów w trakcie.
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.volume_slider.setEnabled(False)
        self.pan_slider.setEnabled(False)
        self.reverse_checkbox.setEnabled(False)
        self.stereo_radio.setEnabled(False)
        self.mono_radio.setEnabled(False)
        self.quality_combo.setEnabled(False)

        # Biblioteka PyDub posiada wbudowaną funkcję play(), ale w kontekście aplikacji graficznych są dwa problemy:
        # - play() jest funkcją synchroniczną (blokuje główny wątek, czyli okno aplikacji)
        # - play() nie da się zatrzymać w trakcie odtwarzania
        # Dlatego używamy własnego PlaybackThread opartego na ffplay.
        self.thread = PlaybackThread(audio)

        # Po zakończeniu odtwarzania, sygnał finished odblokowuje wszystkie kontrolki z powrotem.
        self.thread.finished.connect(lambda: self.play_btn.setEnabled(True))
        self.thread.finished.connect(lambda: self.stop_btn.setEnabled(False))
        self.thread.finished.connect(lambda: self.volume_slider.setEnabled(True))
        self.thread.finished.connect(lambda: self.pan_slider.setEnabled(True))
        self.thread.finished.connect(lambda: self.reverse_checkbox.setEnabled(True))
        self.thread.finished.connect(lambda: self.stereo_radio.setEnabled(True))
        self.thread.finished.connect(lambda: self.mono_radio.setEnabled(True))
        self.thread.finished.connect(lambda: self.quality_combo.setEnabled(True))
        self.thread.start()

    def update_loudness_plot(self, audio):
        # Pobieramy wartość RMS (głośność) co 100ms — RMS to miara efektywnej głośności sygnału audio.
        rms_values = [fragment.rms for fragment in audio[::100]]
        max_rms = max(rms_values) or 1  # Zabezpieczenie przed dzieleniem przez zero dla cichych plików

        # Normalizujemy wartości RMS do zakresu 0–100%, żeby wykres był czytelny niezależnie od głośności pliku.
        rms_values_percentages = [rms / max_rms * 100 for rms in rms_values]
        seconds = [i * 0.1 for i in range(len(rms_values_percentages))]

        getLoudnessPlot(seconds, rms_values_percentages)


    def on_pan_changed(self, v):
        # Aktualizujemy etykietę panoramy — pokazujemy kierunek (L/R) i wartość procentową.
        if v == 0:
            self.pan_label.setText("Pan: Center")
        elif v > 0:
            self.pan_label.setText(f"Pan: R{v}%")
        else:
            self.pan_label.setText(f"Pan: L{abs(v)}%")

    def stop_audio(self):
        if self.thread:
            self.thread.stop()

    def apply_effects_to_audio(self) -> AudioSegment:
        volume = self.volume_slider.value()

        # Głośność skalujemy logarytmicznie (w decybelach), bo ludzkie ucho postrzega dźwięk logarytmicznie.
        # Wzór: dB = 20 * log10(volume / 100). Dla volume=0 ustawiamy -120 dB (praktyczna cisza).
        dB_change = 20 * math.log10(volume / 100) if volume > 0 else -120

        audio = self.audio + dB_change
        channels = 1 if self.mono_radio.isChecked() else 2
        audio = audio.set_channels(channels)
        framerate = self.quality_combo.currentData()
        if framerate is not None:
            audio = audio.set_frame_rate(framerate)
            
        # Panorama działa tylko dla stereo — w mono oba kanały są identyczne, więc pan nie ma sensu.
        pan = self.pan_slider.value() / 100
        if pan != 0 and channels == 2:
            audio = audio.pan(pan)
        if self.reverse_checkbox.isChecked():
            audio = audio.reverse()
        return audio
