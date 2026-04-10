from PySide6.QtWidgets import QSlider, QRadioButton, QButtonGroup, QComboBox, QPushButton
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
from typing import Callable

# Moduł z fabrykami komponentów UI — każda funkcja tworzy i konfiguruje gotowy widget Qt.

def getSlider(range: tuple[int, int], default_val: int) -> QSlider:
    # Tworzy poziomy suwak o podanym zakresie i wartości domyślnej.
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(range[0], range[1])
    slider.setValue(default_val)
    return slider

def getButton(name: str, function: Callable[[], None]) -> QPushButton:
    # Tworzy przycisk z etykietą i podłącza do niego funkcję wywoływaną po kliknięciu.
    button = QPushButton(name)
    button.clicked.connect(function)
    return button

def getRadioButtonsGroup(buttons: list[QRadioButton]) -> QButtonGroup:
    # Grupuje przyciski radiowe — QButtonGroup zapewnia, że tylko jeden z nich może być zaznaczony naraz.
    button_group = QButtonGroup()
    for btn in buttons:
        button_group.addButton(btn)
    return button_group

def getComboBox(combo_data: list[tuple[str, int]]) -> QComboBox:
    # Tworzy listę rozwijaną. Każdy element to para (etykieta, wartość) —
    # etykieta jest wyświetlana użytkownikowi, wartość pobierana przez currentData().
    combo = QComboBox()
    for data in combo_data:
        combo.addItem(data[0], data[1])
    combo.setCurrentIndex(0)
    return combo

def getLoudnessPlot(x_data, y_data):
    # Rysuje wykres głośności w czasie w osobnym oknie matplotlib.
    # plt.clf() czyści poprzedni wykres przed narysowaniem nowego — bez tego wykresy by się nakładały.
    # plt.pause(0.001) wymusza odświeżenie okna bez blokowania głównego wątku aplikacji.
    plt.figure("Loudness")
    plt.clf()
    plt.plot(x_data, y_data)
    plt.xlabel("Time (s)")
    plt.ylabel("Loudness (%)")
    plt.title("Loudness over time")
    plt.tight_layout()
    plt.pause(0.001)
