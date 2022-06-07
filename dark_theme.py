# ALTER DARK THEME
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets


class DarkTheme(object):
    def setup(self, App):
        try:
            settings = QtCore.QSettings(
                "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                QtCore.QSettings.NativeFormat
            )
            if settings.value("AppsUseLightTheme") == 0:

                App.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
                darkPalette = QtGui.QPalette()
                darkColor = QtGui.QColor(45, 45, 45)
                disabledColor = QtGui.QColor(127, 127, 127)

                darkPalette.setColor(QtGui.QPalette.Window, darkColor)
                darkPalette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
                darkPalette.setColor(QtGui.QPalette.Base, QtGui.QColor(18, 18, 18))
                darkPalette.setColor(QtGui.QPalette.AlternateBase, darkColor)
                darkPalette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
                darkPalette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
                darkPalette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
                darkPalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabledColor)
                darkPalette.setColor(QtGui.QPalette.Button, darkColor)
                darkPalette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
                darkPalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabledColor)
                darkPalette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
                darkPalette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
                darkPalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
                darkPalette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
                darkPalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, disabledColor)
                App.setPalette(darkPalette)
                App.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
        except Exception('Something went wrong') as exeption:
            print(exeption)
