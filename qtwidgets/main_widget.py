import os
from PyQt5.QtWidgets import *
#QWidget, QMainWindow, QAction, QGridLayout, QPushButton, QLabel, QListWidget, QTextEdit, QFileDialog, QMessageBox, QAbstractItemView...
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QTimer, QThreadPool, QRunnable, pyqtSlot
#from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPalette, QTextCursor 
import re
import sys 
import time
import traceback

from ebook_image_extractor import extract_image


class MainWidget(QMainWindow):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.last_dir = os.path.expanduser(self.get_last_dir())
        #sys.stdout = EmittingStream(text_written=self.normal_output_written)
        QMainWindow.__init__(self)
        self.init_ui()

    def init_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle('EIX Ebook Image Extractor')    

        '''Actions'''

        self.extract_cov_action = QAction('&Extract Covers', self)
        #self.extract_cov_action.setShortcut('Ctrl+U')
        self.extract_cov_action.setStatusTip('Extract Cover Images from eBooks')
        self.extract_cov_action.triggered.connect(self.extract_covers)


        self.exit_action = QAction('&Close', self)
        #self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')
        self.exit_action.triggered.connect(self.exit)


        self.help_action = QAction('&Help', self)
        self.help_action.setShortcut('Ctrl+H')
        self.help_action.setStatusTip('Help')
        self.help_action.triggered.connect(self.help)

        '''Menubar'''

        menubar = self.menuBar()
        #menubar = QMenuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(self.extract_cov_action)

        tools_menu = menubar.addMenu('&Tools')
        tools_menu.addAction(self.extract_cov_action)

        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(self.help_action)

        grid = QGridLayout()
        self.main_widget.setLayout(grid)

        '''Buttons on left'''

        buttons = (
            {'title': 'Extract Covers', 'action': self.extract_covers},
            None,
            {'title': 'Exit', 'action': self.exit}
            )

        self.button_dict = {}
        row = 0
        for button in buttons:
            if button:
                #print 'button %s' % row
                button['widget'] = QPushButton(button['title'])
                try:
                    button['widget'].setStyleSheet(button['style'])
                except KeyError:
                    pass
                try:
                    button['widget'].setEnabled(button['enabled'])
                except KeyError:
                    pass
                self.button_dict[button['title']] = (button['widget'])
                grid.addWidget(button['widget'], row, 0)
                button['widget'].clicked.connect(button['action'])
                row += 1
            else:
                #print 'No button %s' % row
                row += 1


    def help(self):
        self.help_window = HelpWidget()
        self.help_window.show()


    def __del__(self):
        '''Restore sys.stdout'''
        sys.stdout = sys.__stdout__

    def extract_covers(self):
        '''A tool for extracting ebook covers'''
        ebook_list, _ = QFileDialog.getOpenFileNames(self, 'Epub Files', self.last_dir, '(*.epub *.pdf)')
        if ebook_list:
            self.last_dir = os.path.dirname(str(ebook_list[0]))
            start_time = time.time()
            skipped = created = failed = 0
            image_path = None
            for file_name in ebook_list:
                s, c, f = extract_image(file_name)
                skipped += s
                created += c
                failed += f
            elapsed_time = time.time() - start_time
            QMessageBox.information(self, 'Finished', 'Finished Extracting Cover Images.\n Success: %s; Failed: %s; Skipped: %s;\n Time: %.2f sec.' % (created, failed, skipped, elapsed_time), QMessageBox.Ok)


    def get_last_dir(self):
        return os.path.expanduser('.')
        #return self.last_dir
    #def save_log(self):
    #    '''
    #    -- add log dir to config.
    #    -- add date to file name
    #    -- save automatically on exit?
    #    '''
    #    log_dir = self.eu.get_log_dir()
    #    log_filename = self.eu.get_log_file()
    #    
    #    #filename = QFileDialog.getSaveFileName(self, 'Save File', os.path.expanduser('~/eBookUploads.log'), 'Text (*.log *.txt)' )
    #    #if filename:
    #    ''' We just store the contents of the text file along with the format in html, which Qt does in a very nice way for us'''
    #    self.eu.write_to_log_file(log_filename, text_edit)

    def exit(self):
        self.close()
