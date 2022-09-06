import sys
from PyQt5 import QtCore, QtGui, QtSvg
from PyQt5.QtSvg import QGraphicsWebView
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    scene = QtGui.QGraphicsScene()
    view = QtGui.QGraphicsView(scene)

    br = QtSvg.QGraphicsSvgItem("C:\your_interactive_svg.svg").boundingRect()

    webview = QGraphicsWebView()
    webview.load(QtCore.QUrl("C:\your_interactive_svg.svg"))
    webview.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
    webview.setCacheMode(QtGui.QGraphicsItem.NoCache)
    webview.resize(br.width(), br.height())

    scene.addItem(webview)
    view.resize(br.width()+10, br.height()+10)
    view.show()
    sys.exit(app.exec_())