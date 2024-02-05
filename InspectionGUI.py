import sys
import cv2
import time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGroupBox, QCheckBox, QFileDialog, QMessageBox
from akida import Model
from akida import devices


# Global variables
mode_objdet = False
mode_classify = False
model_objdet = Model("models/objdetection.fbz")
model_objdet.summary()

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
        time.sleep(2)
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
        self.load_detection_model_button = QPushButton("Load Object Detection Model", self)
        self.load_classification_model_button = QPushButton("Load Classification Model", self)
        self.exit_button = QPushButton(QIcon.fromTheme('SP_TitleBarCloseButton'), 'Exit', self)
        self.stats_group_box = QGroupBox("Statistics and Diagnostics", self)
        self.stats_label = QLabel("No statistics available", self)
        self.output_group_box = QGroupBox("Object Detection Output", self)
        self.output_label = QLabel("No output available", self)
        self.mode_group_box = QGroupBox("Mode", self)
        self.object_detection_checkbox = QCheckBox("Object Detection", self)
        self.classification_checkbox = QCheckBox("Classification", self)

        self.init_ui()

    def init_ui(self):
        # Set the button sizes and styles
        button_size = 150
        self.start_stop_button.setFixedSize(button_size, button_size)
        self.load_detection_model_button.setFixedSize(button_size, button_size)
        self.load_classification_model_button.setFixedSize(button_size, button_size)
        self.exit_button.setFixedSize(button_size, button_size)

        # Create layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_stop_button)
        button_layout.addWidget(self.load_detection_model_button)
        button_layout.addWidget(self.load_classification_model_button)
        button_layout.addWidget(self.exit_button)

        stats_layout = QVBoxLayout(self.stats_group_box)
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.video_display.diagnostics_label)  # Add the diagnostics label

        output_layout = QVBoxLayout(self.output_group_box)
        output_layout.addWidget(self.output_label)

        mode_layout = QHBoxLayout(self.mode_group_box)
        mode_layout.addWidget(self.object_detection_checkbox)
        mode_layout.addWidget(self.classification_checkbox)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.video_display, 1)

        # Create a horizontal layout for buttons and stats
        buttons_stats_layout = QHBoxLayout()
        buttons_stats_layout.addLayout(button_layout)
        buttons_stats_layout.addWidget(self.stats_group_box)
        buttons_stats_layout.addWidget(self.mode_group_box)

        main_layout.addLayout(buttons_stats_layout)
        main_layout.addWidget(self.output_group_box)

        # Connect signals
        self.start_stop_button.clicked.connect(self.toggle_inspection)
        self.load_detection_model_button.clicked.connect(self.load_new_model)
        self.load_classification_model_button.clicked.connect(self.load_new_classification_model)
        self.exit_button.clicked.connect(self.close_application)
        self.object_detection_checkbox.stateChanged.connect(self.update_objdet_mode)
        self.classification_checkbox.stateChanged.connect(self.update_classify_mode)

    def toggle_inspection(self):
        self.video_display.inspection_enabled = not self.video_display.inspection_enabled

    def load_new_model(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog(self, options=options)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("FBZ Models (*.fbz)")

        if file_dialog.exec_():
            model_files = file_dialog.selectedFiles()

            if model_files:
                model_path = model_files[0]
                self.save_model(model_path, "objdetection.fbz")

    def load_new_classification_model(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog(self, options=options)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("FBZ Models (*.fbz)")

        if file_dialog.exec_():
            model_files = file_dialog.selectedFiles()

            if model_files:
                model_path = model_files[0]
                self.save_model(model_path, "classifier.fbz")

    def save_model(self, source_path, destination_name):
        models_folder = "models"
        destination_path = f"{models_folder}/{destination_name}"

        try:
            import os
            os.makedirs(models_folder, exist_ok=True)
            import shutil
            shutil.copy2(source_path, destination_path)
            QMessageBox.information(self, "Model Uploaded", "Model uploaded successfully.", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to upload model: {str(e)}", QMessageBox.Ok)

    def update_objdet_mode(self, state):
        global mode_objdet
        mode_objdet = state == Qt.Checked
        print("Object Detection Mode:", mode_objdet)

    def update_classify_mode(self, state):
        global mode_classify
        mode_classify = state == Qt.Checked
        print("Classification Mode:", mode_classify)

    def close_application(self):
        self.close()

def brainchip_akida_detect():
    device = devices()[0]
    print(device.version)
    


if __name__ == '__main__':
    brainchip_akida_detect()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Updated PyQt5 Application")
    window.setGeometry(0, 0, 1920, 1080)
    window.show()
    sys.exit(app.exec_())
