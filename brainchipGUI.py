import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QTextEdit

class OpenCVQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCV Qt App")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.text_box = QTextEdit(self)
        self.text_box.setReadOnly(True)
        self.text_box.setStyleSheet(
            "background-color: black; color: lime; font-family: Courier, monospace; font-size: 12pt;")

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_box)
        self.layout.addWidget(self.image_label)

        self.button_layout = QHBoxLayout()
        self.uno_button = QPushButton("UNO")
        self.rps_button = QPushButton("ROCK PAPER SCISSORS")
        self.reset_button = QPushButton("RESET")

        self.uno_button.setCheckable(True)
        self.rps_button.setCheckable(True)

        self.uno_button.clicked.connect(self.toggle_uno)
        self.rps_button.clicked.connect(self.toggle_rps)
        self.reset_button.clicked.connect(self.reset_game)

        self.button_layout.addWidget(self.uno_button)
        self.button_layout.addWidget(self.rps_button)
        self.button_layout.addWidget(self.reset_button)

        self.layout.addLayout(self.button_layout)
        self.central_widget.setLayout(self.layout)

        # OpenCV setup
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 milliseconds

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            q_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)

    def display_message(self, message):
        self.text_box.append(message)

    def toggle_uno(self):
        if self.uno_button.isChecked():
            self.rps_button.setChecked(False)
            self.display_message("UNO button ON")
            self.display_message("ROCK PAPER SCISSORS button OFF (reset)")
            self.uno_button.setStyleSheet("background-color: orange; color: black; font-weight: bold;")
            self.rps_button.setStyleSheet("")
        else:
            self.display_message("UNO button OFF")
            self.uno_button.setStyleSheet("")

    def toggle_rps(self):
        if self.rps_button.isChecked():
            self.uno_button.setChecked(False)
            self.display_message("ROCK PAPER SCISSORS button ON")
            self.display_message("UNO button OFF (reset)")
            self.rps_button.setStyleSheet("background-color: orange; color: black; font-weight: bold;")
            self.uno_button.setStyleSheet("")
        else:
            self.display_message("ROCK PAPER SCISSORS button OFF")
            self.rps_button.setStyleSheet("")

    def reset_game(self):
        self.text_box.clear()
        self.uno_button.setChecked(False)
        self.rps_button.setChecked(False)
        self.display_message("Game reset")
        self.uno_button.setStyleSheet("")
        self.rps_button.setStyleSheet("")

    def closeEvent(self, event):
        self.capture.release()
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = OpenCVQtApp()
    main_window.show()
    sys.exit(app.exec_())
