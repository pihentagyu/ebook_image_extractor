#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# GUI for Ebook Cover Extractor 
import sys

from PyQt5.QtWidgets import QApplication

from qtwidgets.main_widget import MainWidget

def main():
    app = QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    ret = app.exec_()
    #sys.exit(ret)


if __name__ == '__main__':
    main()    
