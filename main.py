import os
import sys

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog,
    QHBoxLayout, QWidget, QComboBox, QVBoxLayout, QProgressBar, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QScreen
import moviepy
from moviepy import VideoFileClip

from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QEnterEvent, QMouseEvent


class HoverButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.original_geometry = None

    def enterEvent(self, event: QEnterEvent):
        self.original_geometry = self.geometry()
        new_rect = self.original_geometry.adjusted(-1, -1, 1, 1)  # grow slightly

        self.anim.stop()
        self.anim.setDuration(50)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(new_rect)
        self.anim.start()

        # Apply glow
        self.apply_hover_shadow()

    def leaveEvent(self, event: QMouseEvent):
        if self.original_geometry:
            self.anim.stop()
            self.anim.setDuration(50)
            self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.anim.setStartValue(self.geometry())
            self.anim.setEndValue(self.original_geometry)
            self.anim.start()

        # Remove glow
        self.setGraphicsEffect(None)

    def apply_hover_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(Qt_GlobalColor="White")
        shadow.setOffset(0)
        shadow.setBlurRadius(15)
        self.setGraphicsEffect(shadow)


class Main(QMainWindow):
    def __init__(self, screen):
        super().__init__()

        self.selected_file_extension = None
        self.selected_file = None

        # Screen sizes
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_width = screen_width // 3
        window_height = screen_height // 3

        # Set window properties
        self.setWindowTitle("File Converter")
        self.setGeometry(
            (screen_width - window_width) // 2,
            (screen_height - window_height) // 2,
            window_width,
            window_height
        )

        # Buttons and layout
        self.select_file_button = QPushButton("Select File")
        self.select_file_button.setMinimumSize(window_width // 5, window_height // 5)
        self.select_file_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # self.select_file_button.setStyleSheet("""
        #                                         QPushButton {
        #                                             background-color: #3498db;
        #                                             color: white;
        #                                             border-radius: 20px;
        #                                             padding: 5px;
        #                                         }
        #                                         QPushButton:hover {
        #                                             background-color: #2980b9;
        #                                         }
        #                                         QPushButton:pressed {
        #                                             background-color: #1c5980;
        #                                         }
        #                                     """)
        self.download_converted_button = QPushButton("Convert and Download")
        self.download_converted_button.setMinimumSize(window_width // 5, window_height // 5)
        self.download_converted_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.download_converted_button.hide()

        self.clear_file_button = QPushButton("Reset")
        self.clear_file_button.setMinimumSize(window_height // 5, window_height // 5)
        self.clear_file_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # self.clear_file_button.setStyleSheet("""
        #                                         QPushButton {
        #                                             background-color: red;
        #                                             color: white;
        #                                             border-radius: 20px;
        #                                             padding: 5px;
        #                                         }
        #                                         QPushButton:hover {
        #                                             background-color: darkred;
        #                                         }
        #                                         QPushButton:pressed {
        #                                             background-color: #1c5980;
        #                                         }
        #                                     """)
        
        self.videos = ["Select Format", "mp4", "avi", "mov", "mkv", "webm"]
        self.dropdown = QComboBox(self)
        self.dropdown.setMinimumSize(window_height // 5, window_height // 5)
        self.dropdown.hide()

        self.layout2 = QHBoxLayout()

        self.layout2.addWidget(self.select_file_button)

        self.layout1 = QHBoxLayout()
        self.layout1.addLayout(self.layout2)
        # layout1.addWidget(self.dropdown)
        # self.layout1.addWidget(self.download_converted_button)


        main_layout = QVBoxLayout()
        main_layout.addLayout(self.layout1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect signals
        self.select_file_button.clicked.connect(self.openFileDialog)

        self.download_converted_button.clicked.connect(self.handle_conversion)

        self.clear_file_button.clicked.connect(self.clear_file)

    def openFileDialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)

        if file_dialog.exec():
            self.selected_file = os.path.splitext(file_dialog.selectedFiles()[0])[0]
            self.selected_file_extension = os.path.splitext(file_dialog.selectedFiles()[0])[1]
            print(f"Selected File: {self.selected_file}{self.selected_file_extension}")

            self.layout2.insertWidget(0, self.clear_file_button)
            self.clear_file_button.show()
            self.select_file_button.setEnabled(False)

            self.layout1.insertWidget(1, self.dropdown)
            if self.selected_file_extension[1:] in self.videos:
                self.dropdown.addItems(self.videos)
                self.dropdown.removeItem(self.dropdown.findText(self.selected_file_extension[1:]))
            self.dropdown.show()

            self.layout1.insertWidget(2, self.download_converted_button)
            self.download_converted_button.show()

    def clear_file(self):
        self.layout2.removeWidget(self.clear_file_button)
        self.clear_file_button.hide()
        self.clear_file_button.setParent(None)

        self.selected_file = None
        self.select_file_button.setEnabled(True)

        self.layout1.removeWidget(self.dropdown)
        self.dropdown.clear()
        self.dropdown.hide()
        self.dropdown.setParent(None)

        self.layout1.removeWidget(self.download_converted_button)
        self.download_converted_button.hide()
        self.download_converted_button.setParent(None)


    def convert_video(self, output_format):
        try:
            output_file = f"{self.selected_file}_converted.{output_format}"

            video = VideoFileClip(self.selected_file)
            video.write_videofile(output_file)


            return output_file

        except Exception as  e:
            print(f"Conversion Failed {e}")

    def handle_conversion(self):
        if not self.selected_file:
            print("no file selected")

        output_format = self.dropdown.currentText()
        if output_format in ["mp4", "avi", "mov", "mkv", "webm"]:
            output_file = self.convert_video(output_format)

        return output_file

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.primaryScreen()

    window = Main(screen)
    window.show()

    sys.exit(app.exec())
