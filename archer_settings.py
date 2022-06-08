import os
import sys

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def run(self):
        """Long-running task."""
        # os.system(r'dist\reticle_designer\reticle_designer.exe -exec')
        os.system(r'python reticle_designer.py -exec')
        self.finished.emit()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.reticles = QtWidgets.QPushButton('Reticles')
        self.gridLayout.addWidget(self.reticles)

        MainWindow.setCentralWidget(self.centralwidget)


class Window(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Archer Bar')
        self.resize(300, 100)

        self.reticles.worker = Worker
        self.reticles.clicked.connect(self.open_reticle)

    def open_reticle(self):
        if not isinstance(self.thread, QtCore.QThread):
            # Step 2: Create a QThread object
            self.thread = QtCore.QThread()
            # Step 3: Create a worker object
            self.worker = self.sender().worker()
            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(lambda: self.__setattr__('thread', None))
            self.thread.start()
            self.sender().is_thread = True


if __name__ == '__main__':

    App = QApplication(sys.argv)

    # NATIVE DARK THEME
    from dark_theme import DarkTheme
    DarkTheme().setup(App)

    _id = QtGui.QFontDatabase.addApplicationFont("Bank Gothic Light BT.ttf")
    fid = QtGui.QFontDatabase.applicationFontFamilies(_id)
    window = Window()
    window.show()
    sys.exit(App.exec())
