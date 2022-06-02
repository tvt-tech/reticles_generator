from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sys
import time


# Main window class
# class MainWindow(QMainWindow):
class CameraPreview(QWidget):

    # constructor
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            pass

        self.save_path = ""

        self.viewfinder = QCameraViewfinder()
        self.gridLayout = QGridLayout()

        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridLayout)

        self.gridLayout.addWidget(self.viewfinder, 0, 0)

        self.layout().setAlignment(Qt.AlignCenter)

        self.select_camera(0)

        self.camera_selector = QComboBox()

        self.camera_selector.setStatusTip("Choose camera to take pictures")
        self.camera_selector.setToolTip("Select Camera")
        self.camera_selector.setToolTipDuration(2500)
        self.camera_selector.addItems([camera.description()
                                       for camera in self.available_cameras])
        self.camera_selector.currentIndexChanged.connect(self.select_camera)

        self.layout().addWidget(self.camera_selector)

    # method to select camera
    def select_camera(self, i):

        # getting the selected camera
        try:
            self.camera = QCamera(self.available_cameras[i])

        except:
            return

        # setting view finder to the camera
        self.camera.setViewfinder(self.viewfinder)

        # setting capture mode to the camera
        self.camera.setCaptureMode(QCamera.CaptureStillImage)

        # if any error occur show the alert
        self.camera.error.connect(lambda: self.alert(self.camera.errorString()))

        # start the camera
        self.camera.start()

        # creating a QCameraImageCapture object
        self.capture = QCameraImageCapture(self.camera)

        # showing alert if error occur
        self.capture.error.connect(lambda error_msg, error,
                                          msg: self.alert(msg))

        # when image captured showing message
        self.capture.imageCaptured.connect(lambda d, i: self.status.showMessage("Image captured : "
                                                                                + str(self.save_seq)))

        # getting current camera name
        self.current_camera_name = self.available_cameras[i].description()

        # initial save sequence
        self.save_seq = 0

    # method to take photo
    def click_photo(self):

        # time stamp
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")

        # capture the image and save it on the save path
        self.capture.capture(os.path.join(self.save_path,
                                          "%s-%04d-%s.jpg" % (
                                              self.current_camera_name,
                                              self.save_seq,
                                              timestamp
                                          )))

        self.save_seq += 1

    def change_folder(self):
        path = QFileDialog.getExistingDirectory(self,
                                                "Picture Location", "")

        if path:
            self.save_path = path
            self.save_seq = 0

    def alert(self, msg):
        error = QErrorMessage(self)
        error.showMessage(msg)
