import sys
import cv2
import time
import os
import numpy as np
from scipy.special import softmax
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon, QColor, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGroupBox, QCheckBox, QFileDialog, QMessageBox,QLineEdit
from akida import Model
from akida import devices
from PyQt5.QtCore import pyqtSignal, QObject


# Global variables (yeah I know)
mode_objdet = True
mode_classify = True

akida_device = None
akida_model_objectdet = None
akida_model_classify = None
akida_model_objectdet_inshape = None
akida_model_classify_inshape = None
counter =0

result_frame = np.ones((280, 280, 3), dtype=np.uint8) * 255

class VideoDisplay(QLabel):

    frame_updated = pyqtSignal(object)

    def __init__(self, parent=None):
        super(VideoDisplay, self).__init__(parent)
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        border_color_1 = QColor(0, 0, 0)  # Black color
        border_width_1 = 2  # You can adjust the border width
        

        # Check if the webcam is opened successfully
        if not self.video_capture.isOpened():
            self.setText("No camera detected")
            QMessageBox.warning(self, "Warning", "No camera detected.", QMessageBox.Ok)
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.inspection_enabled = False
            self.akida_power = 0  # Placeholder for Akida Power value
            #self.stats_label = QLabel("No statistics available", self)  # Empty stats_label
            self.diagnostics_label = QLabel("No diagnostics available", self)  # Empty diagnostics_label
            self.timer.start(30)

    def add_border_to_pixmap(self, pixmap, color, width):
            # Convert the QPixmap to a QImage
            image = pixmap.toImage()
            image.convertToFormat(QImage.Format_ARGB32)

            # Create a QPainter to draw on the image
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)

            # Draw a border around the image
            pen = QPen(color, width)
            painter.setPen(pen)
            painter.drawRect(image.rect())

            painter.end()

            pixmap_with_border = QPixmap.fromImage(image)

            return pixmap_with_border

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            #pixmap = self.add_border_to_pixmap(pixmap, border_color_1, border_width_1)
            self.setPixmap(pixmap)

            if self.inspection_enabled:
                self.inspect_frame(frame)

    def inspect_frame(self, frame):
        global counter, result_frame
        # This is where we perform the inference in case you are looking for it
        height, width, _ = frame.shape
        print("Height" + str(height) + "Width" + str(width))

        offset = abs(width -height)/2
        print(offset)
        #input_frame = cv2.resize(frame,(akida_model_objectdet_inshape[0],akida_model_objectdet_inshape[1]) ) # We need to resize the frame to the input layer of the Akida
        input_frame_temp = frame[0:480,80:(80+480) ]

        input_frame = cv2.resize(input_frame_temp,(akida_model_objectdet_inshape[0],akida_model_objectdet_inshape[1]) )
        input_frame_class = cv2.resize(input_frame_temp,(160,160) )

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_frame_akida = np.expand_dims(input_frame, axis=0) # this needed to create the correct input tesnsor for the Akida which includes a batch size of 1 in this case
        input_frame_akida_class= np.expand_dims(input_frame_class, axis=0)

        #Object Detection
        if mode_objdet:
            akida_model_objectdet.map(akida_device)

            fomo_out_objdet = akida_model_objectdet.predict(input_frame_akida)
            pred = softmax(fomo_out_objdet, axis=-1).squeeze()
            result = fill_result_struct_f32_fomo_obj(pred,1,0.85, categories = ['gear'])
            print("result")
            print(result)
            if int(result['bounding_boxes_count']) > 0:
                print("object detected")
                for detection in result['bounding_boxes']:
                    label, x,y,width,height, value = detection.values()
                    input_w, input_h, _ = frame.shape
                    ml_w, ml_h, _ = input_frame.shape
                    scale_w = int(input_w/ml_w)
                    scale_h = int(input_h/ml_h)
                    cv2.circle(frame,((scale_w*x)+100,(scale_h*y)+20),10,(255,255,255),-1 )
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap_postprocesing = QPixmap.fromImage(image)
                    self.setPixmap(pixmap_postprocesing)
                    #self.frame_updated.emit(input_frame) #slows down performance
                    result_frame = input_frame
                    self.akida_power = akida_device.soc.power_meter.floor
                    #print(f'Floor power: {floor_power:.2f} mW')
                    model_stats_obj = akida_model_objectdet.statistics
                    print(model_stats_obj)
                    window.video_display_2.display_frame(result_frame)

                      
            
        
        #Classification
        if mode_classify: 
            akida_model_classify.map(akida_device)
            classify_out = akida_model_classify.predict(input_frame_akida_class)
            print(classify_out)

       
        #print("===============START=================")
        #print(results_objdet)
        #print("==================STOP===============")
        #time.sleep(3)
        #akida_in = np.expand_dims(akida_frame, axis=0)
        #output_obj = softmax(results_objdet, axis=-1).squeeze()
        #input_shape1 = (1,) + tuple(akida_model_objectdet.input_shape)
        #input_objdet = np.ones(input_shape1, dtype=np.uint8)

        #input_shape2 = (1,) + tuple(akida_model_classify.input_shape)
        #input_class = np.ones(input_shape2, dtype=np.uint8)
        
        #objdet_output = akida_model_objectdet.forward(input_objdet)
        #class_output = akida_model_classify.forward(input_class)
        #print("OD ======================" + str(counter))
        #print(objdet_output)
        
        #print("Classify======================" + str(counter))
        #print(objdet_output)
        
        # Diagnostics Info to be displayed in UI
        self.akida_power += 1  # Placeholder logic, update Akida Power value
        self.diagnostics()

    def diagnostics(self):
        # Update diagnostics information
        diagnostics_text = f"Akida Power: {self.akida_power:.2f} mW"
        self.diagnostics_label.setText(diagnostics_text)

    def stop_video(self):
        self.timer.stop()

    def start_video(self):
        self.timer.start(30)



class ImageDisplay(QLabel):
    def __init__(self, parent=None):
        super(ImageDisplay, self).__init__(parent)
        self.setMinimumSize(280, 280)
        self.setMaximumSize(280, 280)

    def display_frame(self, frame):
        pixmap = self.create_pixmap_from_frame(frame)
        self.setPixmap(pixmap)

    def create_pixmap_from_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        # Resize the pixmap to fit the desired size
        pixmap = pixmap.scaled(280, 280, aspectRatioMode=Qt.KeepAspectRatio)

        
        border_color = QColor(0, 0, 0)  # Black color
        border_width = 2  # You can adjust the border width
        pixmap = self.add_border_to_pixmap(pixmap, border_color, border_width)

        return pixmap

    def add_border_to_pixmap(self, pixmap, color, width):
        # Convert the QPixmap to a QImage
        image = pixmap.toImage()
        image.convertToFormat(QImage.Format_ARGB32)

        # Create a QPainter to draw on the image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a border around the image
        pen = QPen(color, width)
        painter.setPen(pen)
        painter.drawRect(image.rect())

        painter.end()

        # Convert the QImage back to a QPixmap
        pixmap_with_border = QPixmap.fromImage(image)

        return pixmap_with_border

# Main window
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.banner_label = QLabel(self)
        self.banner_label.setPixmap(QPixmap("media/ei_bc_logo.png")) 


        self.video_display = VideoDisplay(self)
        self.video_display_2 = ImageDisplay(self)
        #self.video_display.frame_updated.connect(self.video_display_2.display_frame) # too slow


        self.objdet_textbox = QLineEdit(self)
        self.objdet_textbox.setPlaceholderText("Enter target for Object Detection")
        self.objdet_textbox.textChanged.connect(self.update_target_objdet)

        # Add Classification text box
        self.classify_textbox = QLineEdit(self)
        self.classify_textbox.setPlaceholderText("Enter target for Classification")
        self.classify_textbox.textChanged.connect(self.update_target_classify)

        self.start_stop_button = QPushButton("Start/Stop\nInspection", self)
        self.load_detection_model_button = QPushButton("Load\nObject Detection\nModel", self)
        self.load_classification_model_button = QPushButton("Load\nClassification\nModel", self)
        self.exit_button = QPushButton(QIcon.fromTheme('SP_TitleBarCloseButton'), 'Exit', self)
        self.stats_group_box = QGroupBox("Akida Power Statistics", self)
        self.stats_label = QLabel("No statistics available", self)
        self.output_group_box = QGroupBox("Logs", self)
        self.results_model_box = QGroupBox("Results",self)
        self.output_label = QLabel("No output available", self)
        self.mode_group_box = QGroupBox("Mode", self)
        self.object_detection_checkbox = QCheckBox("Object Detection", self)
        self.classification_checkbox = QCheckBox("Classification", self)

        self.class_res_label = QLabel("No results yet", self)
        self.objc_res_label = QLabel("No results yet", self)
        self.object_count = QLabel("No objects detected", self)
        self.pass_rej = QLabel("None detected", self)

        self.init_ui()

    def init_ui(self):
        # Set the button sizes and styles
        button_size = 150
        self.setStyleSheet("background-color: white;")

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

        results_layout = QVBoxLayout(self.results_model_box)
        results_layout.addWidget(self.object_count)
        results_layout.addWidget(self.objc_res_label)
        results_layout.addWidget(self.class_res_label)
        results_layout.addWidget(self.pass_rej)

        stats_layout = QVBoxLayout(self.stats_group_box)
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.video_display.diagnostics_label)  # Add the diagnostics label

        output_layout = QVBoxLayout(self.output_group_box)
        output_layout.addWidget(self.output_label)

        #mode_layout = QHBoxLayout(self.mode_group_box)
        #mode_layout.addWidget(self.object_detection_checkbox)
        #mode_layout.addWidget(self.classification_checkbox)

        mode_layout = QHBoxLayout(self.mode_group_box)
        mode_layout.addWidget(self.object_detection_checkbox)
        mode_layout.addWidget(self.objdet_textbox)  # Add Object Detection text box
        mode_layout.addWidget(self.classification_checkbox)
        mode_layout.addWidget(self.classify_textbox)  # Add Classification text box


        # Add the banner label at the top center
        

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.banner_label, alignment=Qt.AlignTop | Qt.AlignHCenter)
        main_layout.addWidget(self.video_display, 1)

        
        # Create a horizontal layout for the main VideoDisplay and the new VideoDisplay
        video_displays_layout = QHBoxLayout()
        video_displays_layout.addWidget(self.video_display, 1)

        
        video_displays_layout.addWidget(self.video_display_2, 1)
        video_displays_layout.addWidget(self.results_model_box,1)

        main_layout.addLayout(video_displays_layout)


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

    def update_target_objdet(self, text):
        global target_objdet
        target_objdet = text
        print("Target for Object Detection:", target_objdet)

    def update_target_classify(self, text):
        global target_classify
        target_classify = text
        print("Target for Classification:", target_classify)

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

def ei_cube_check_overlap(c, x, y, width, height, confidence):
    is_overlapping = not ((c['x'] + c['width'] < x) or (c['y'] + c['height'] < y) or (c['x'] > x + width) or (c['y'] > y + height))

    if not is_overlapping:
         return False
    if x < c['x']:
        c['x'] = x
        c['width'] += c['x'] - x
    if y < c['y']:
        c['y'] = y
        c['height'] += c['y'] - y
    if (x + width) > (c['x'] + c['width']):
        c['width'] += (x + width) - (c['x'] + c['width'])
    if (y + height) > (c['y'] + c['height']):
        c['height'] += (y + height) - (c['y'] + c['height'])
    if confidence > c['confidence']:
        c['confidence'] = confidence

    return True

def ei_handle_cube(cubes, x, y, vf, label, detection_threshold):
    if vf < detection_threshold:
        return
    has_overlapping = False
    width = 1
    height = 1
    for c in cubes:
        # not cube for same class? continue
        if c['label'] != label:
             continue
        if ei_cube_check_overlap(c, x, y, width, height, vf):
            has_overlapping = True
            break

    if not has_overlapping:
        cube = {}
        cube['x'] = x
        cube['y'] = y
        cube['width'] = 1
        cube['height'] = 1
        cube['confidence'] = vf
        cube['label'] = label
        cubes.append(cube)

def fill_result_struct_from_cubes(cubes, out_width_factor):
    result = {}
    bbs = []
    results = []
    added_boxes_count = 0

    for sc in cubes:
        has_overlapping = False
        for c in bbs:
            # not cube for same class? continue
            if c['label'] != sc['label']:
                continue
            if ei_cube_check_overlap(c, sc['x'], sc['y'], sc['width'], sc['height'], sc['confidence']):
                has_overlapping = True
                break

        if has_overlapping:
            continue

        bbs.append(sc)
        results.append({
            'label'  : sc['label'],
            'x'      : int(sc['x'] * out_width_factor),
            'y'      : int(sc['y'] * out_width_factor),
            'width'  : int(sc['width'] * out_width_factor),
            'height' : int(sc['height'] * out_width_factor),
            'value'  : sc['confidence']
        })
        added_boxes_count += 1
        
    result['bounding_boxes'] = results
    result['bounding_boxes_count'] = len(results)
    return result

def fill_result_struct_f32_fomo_obj(data,  label_count, thresh, categories):
    cubes = []
    out_factor = int(akida_model_objectdet_inshape[0]/8)
    out_width_factor = akida_model_objectdet_inshape[0] / out_factor
    for y in range(out_factor):
        for x in range(out_factor):
            for ix in range(1, label_count + 1):
                vf = data[y][x][ix]
                ei_handle_cube(cubes, x, y, vf, categories[ix - 1], thresh)

    result = fill_result_struct_from_cubes(cubes, out_width_factor)
    return result

def fill_result_struct_f32_fomo_class(data,label_count, thresh, categories):
    cubes = []
    out_factor = int(akida_model_classify_inshape[0]/8)
    out_width_factor = akida_model_classify_inshape[0] / out_factor
    for y in range(out_factor):
        for x in range(out_factor):
            for ix in range(1, label_count + 1):
                vf = data[y][x][ix]
                ei_handle_cube(cubes, x, y, vf, categories[ix - 1], thresh)

    result = fill_result_struct_from_cubes(cubes, out_width_factor)
    return result
def brainchip_akida_detect():
    global akida_device
    if len(devices()) != 0:
        print("Akida device found")
        akida_device = devices()[0]
        print(akida_device.version)
        akida_device.soc.power_measurement_enabled = True

    else:
        print("No Akida devices found")
    
def brainchip_load_models():
    global akida_model_objectdet, akida_model_classify, akida_model_objectdet_inshape, akida_model_classify_inshape
    
    if os.path.isfile("models/objdetection.fbz"):
        akida_model_objectdet = Model("models/objdetection.fbz")
        akida_model_objectdet_inshape = akida_model_objectdet.input_shape

        print("======================Object Detection Model Summary======================")
        #akida_model_objectdet.summary()
    else:
        print("No Object Detection model found")
    
    if os.path.isfile("models/classifier.fbz"):
        akida_model_classify = Model("models/classifier.fbz")

        akida_model_classify_inshape = akida_model_classify.input_shape
        print("======================Classification Model Summary========================")
        #akida_model_classify.summary()
    else:
        print("No Classification model found")




if __name__ == '__main__':

    
    brainchip_akida_detect()
    brainchip_load_models()
    
    print("please be hardware")
    akida_model_objectdet.summary()
    #akida_model_classify.map(akida_device)
    print("input")
    print(akida_model_objectdet.input_shape)
    print("output")
    print(akida_model_objectdet.output_shape)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("NeuroInspect - Powered by Brainchip and Edge Impulse")
    window.setGeometry(0, 0, 1920, 1080)
    window.show()
    sys.exit(app.exec_())
