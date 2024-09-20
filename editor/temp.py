from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import * 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
# from editor.auto import editor
from auto import editor
import sys

app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = editor.Ui_MainWindow()


def main():
    ui.setupUi(MainWindow)
    setup_initial_state()
    setup_actions()
    MainWindow.show()
    sys.exit(app.exec_())


def setup_initial_state():
    with open('./editor/externals/styleSheet.qss') as f:
        style = f.read()
        app.setStyleSheet(style)
    scintilla = QsciScintilla()
    scintilla.setStyleSheet("background-color: rgb(50, 50, 50);")
    scintilla.setGeometry(scintilla.parentWidget().geometry())
    scintilla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    

def setup_actions():
    ...


if __name__ == "__main__":
    main()