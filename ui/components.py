from PySide6.QtWidgets import QSlider, QRadioButton, QButtonGroup, QComboBox, QPushButton
from PySide6.QtCore import Qt
from typing import Callable

def getSlider(range: tuple[int, int], default_val: int) -> QSlider:
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(range[0], range[1])
    slider.setValue(default_val)
    return slider

def getButton(name: str, function: Callable[[], None]) -> QPushButton:
    button = QPushButton(name)
    button.clicked.connect(function)
    return button

def getRadioButtonsGroup(buttons: list[QRadioButton]) -> QButtonGroup:
    button_group = QButtonGroup()
    for btn in buttons:
        button_group.addButton(btn)
    return button_group

def getComboBox(combo_data: list[tuple[str, int]]) -> QComboBox:
    combo = QComboBox()
    for data in combo_data:
        combo.addItem(data[0], data[1])
    combo.setCurrentIndex(0)
    return combo