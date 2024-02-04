import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGroupBox, QFileDialog, QMessageBox, QDialog

class CustomLoadModelDialog(QDialog):
    def __init__(self, parent=None):
        super(CustomLoadModelDialog, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Load New Model")

        load_model_button = QPushButton("Load New Model", self)
        load_model_button.clicked.connect(self.load_new_model)

        layout = QVBoxLayout()
        layout.addWidget(load_model_button)

        self.setLayout(layout)

    def load_new_model(self):
        print("Loading new model")

class VideoDisplay(QLabel):
    def __init__(self, parent=None):
        super(VideoDisplay, self).__init__(parent)
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Check if the webcam is opened successfully
        if not self.video_capture.isOpened():
            self.setText("No camera detected")
            QMessageBox.warning(self, "Warning", "No camera detected.", QMessageBox.Ok)
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.inspection_enabled = False
            self.akida_power = 0  # Placeholder for Akida Power value
            self.stats_label = QLabel("No statistics available", self)  # Empty stats_label
            self.diagnostics_label = QLabel("No diagnostics available", self)  # Empty diagnostics_label
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
        self.akida_power += 1  # Placeholder logic, update Akida Power value
        self.diagnostics()

    def diagnostics(self):
        # Update diagnostics information
        diagnostics_text = f"Akida Power: {self.akida_power}"
        self.diagnostics_label.setText(diagnostics_text)

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
        stats_layout.addWidget(self.video_display.diagnostics_label)  # Add the diagnostics label

        output_layout = QVBoxLayout(self.output_group_box)
        output_layout.addWidget(self.output_label)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.video_display, 1)

        # Create a horizontal layout for buttons and stats
        buttons_stats_layout = QHBoxLayout()
        buttons_stats_layout.addLayout(button_layout)
        buttons_stats_layout.addWidget(self.stats_group_box)

        main_layout.addLayout(buttons_stats_layout)
        main_layout.addWidget(self.output_group_box)

        # Connect signals
        self.start_stop_button.clicked.connect(self.toggle_inspection)
        self.load_model_button.clicked.connect(self.load_new_model)
        self.exit_button.clicked.connect(self.close_application)

    def toggle_inspection(self):
        self.video_display.inspection_enabled = not self.video_display.inspection_enabled

    def load_new_model(self):
        custom_dialog = CustomLoadModelDialog(self)
        custom_dialog.exec_()

    def close_application(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Updated PyQt5 Application")
    window.setGeometry(0, 0, 1920, 1080)
    window.show()
    sys.exit(app.exec_())
