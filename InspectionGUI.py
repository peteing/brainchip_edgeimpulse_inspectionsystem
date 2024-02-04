import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGroupBox, QSizePolicy

class VideoDisplay(QLabel):
    def __init__(self, parent=None):
        super(VideoDisplay, self).__init__(parent)
        self.video_capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.inspection_enabled = False
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

            if self.inspection_enabled:
                self.inspect_frame(frame)

    def inspect_frame(self, frame):
        # Placeholder function to inspect each frame
        print("Frame Size:", frame.shape)

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
        self.exit_button = QPushButton(QIcon.fromTheme('SP_TitleBarCloseButton'), 'Exit', self)
        self.stats_group_box = QGroupBox("Statistics and Diagnostics", self)
        self.stats_label = QLabel("No statistics available", self)
        self.output_group_box = QGroupBox("Object Detection Output", self)
        self.output_label = QLabel("No output available", self)

        self.init_ui()

    def init_ui(self):
        # Set the button sizes and styles
        button_size = 150
        self.start_stop_button.setFixedSize(button_size, button_size)
        self.load_model_button.setFixedSize(button_size, button_size)
        self.exit_button.setFixedSize(button_size, button_size)

        # Create layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_stop_button)
        button_layout.addWidget(self.load_model_button)
        button_layout.addWidget(self.exit_button)

        stats_layout = QVBoxLayout(self.stats_group_box)
        stats_layout.addWidget(self.stats_label)

        output_layout = QVBoxLayout(self.output_group_box)
        output_layout.addWidget(self.output_label)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.video_display, 1)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stats_group_box)
        main_layout.addWidget(self.output_group_box)

        # Connect signals
        self.start_stop_button.clicked.connect(self.toggle_inspection)
        self.load_model_button.clicked.connect(self.load_new_model)

    def toggle_inspection(self):
        self.video_display.inspection_enabled = not self.video_display.inspection_enabled

    def load_new_model(self):
        print("Load new Model button clicked")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Edge Impulse inspection")
    window.setGeometry(0, 0, 1920, 1080)
    window.show()
    sys.exit(app.exec_())
