import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton

class VideoDisplay(QLabel):
    def __init__(self, parent=None):
        super(VideoDisplay, self).__init__(parent)
        self.video_capture = cv2.VideoCapture(0)  # You can change the index to the desired camera
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.setPixmap(pixmap)

    def stop_video(self):
        self.timer.stop()

    def start_video(self):
        self.timer.start(30)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.video_display = VideoDisplay(self)
        self.start_stop_button = QPushButton("Start/Stop Inspection", self)
        self.load_model_button = QPushButton("Load new Model", self)

        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.video_display, 1)
        layout.addWidget(self.start_stop_button)
        layout.addWidget(self.load_model_button)

        self.start_stop_button.clicked.connect(self.start_stop_inspection)
        self.load_model_button.clicked.connect(self.load_new_model)

    def start_stop_inspection(self):
        # Placeholder for inspection logic
        print("Start/Stop Inspection button clicked")

    def load_new_model(self):
        # Placeholder for model loading logic
        print("Load new Model button clicked")

    def resizeEvent(self, event):
        self.setGeometry(0, 0, 1920, 1080)  # Set the window size to 1920x1080

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("OpenCV PyQt5 Application")
    window.show()
    sys.exit(app.exec_())
