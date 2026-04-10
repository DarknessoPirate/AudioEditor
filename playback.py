import subprocess
import tempfile
from PySide6.QtCore import QThread, Signal
from pydub.utils import get_player_name

# Odtwarza dźwięk w osobnym wątku, żeby interfejs użytkownika nie blokował się podczas odtwarzania.
class PlaybackThread(QThread):
    # Sygnał emitowany po zakończeniu odtwarzania (naturalnym lub przez stop()).
    finished = Signal()

    def __init__(self, audio):
        super().__init__()
        self.audio = audio # przekazujemy plik typu AudioSegment z biblioteki PyDub
        self.process = None  # przechowuje podproces ffplay podczas odtwarzania

    def run(self):
        
        # Tworzymy tymczasowy plik .wav na dysku. delete=True usunie plik po zakończeniu procesu.
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:

            # Wczytany plik audio eksportujemy do wcześniej utworzonego tymczasowego pliku
            self.audio.export(f.name, format="wav")

            # Popen uruchamia zewnętrzny program jako osobny proces i jest równoznaczne z wpisaniem w terminalu komendy:
            # {get_player_name()} -nodisp -autoexit -hide_banner {f.name}.wav, gdzie:
            # get_player_name() zwraca ścieżkę do pliku wykonywalnego ffplay w systemie.
            # f.name to nazwa wczytanego pliku
            # -nodisp: brak okna wideo, -autoexit: wyjście po zakończeniu, -hide_banner: ukrywa informacje o wersji.
            self.process = subprocess.Popen(
                [get_player_name(), "-nodisp", "-autoexit", "-hide_banner", f.name]
            )
            self.process.wait()  # blokuje wątek do momentu zakończenia ffplay
        self.finished.emit()

    def stop(self):
        # Kończy proces ffplay przed czasem (np. gdy użytkownik kliknie Stop).
        if self.process:
            self.process.terminate()