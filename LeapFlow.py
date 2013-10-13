#!/usr/bin/env python3

import sys, os
from PyQt4.QtGui import (QMainWindow, QApplication, QPixmap, QImage, QListWidget, QListWidgetItem, QIcon, QLabel, QStackedWidget,
						QGraphicsScene, QGraphicsView)
from PyQt4.QtCore import SIGNAL, QThread, QSize

threads = []
library = {}

extensions = ['.jpg', '.jpeg', '.png']

class LeapFlow (QMainWindow):

	def __init__ (self):
		QMainWindow.__init__ (self)

		self.list_view = QListWidget ()
		self.list_view.setFlow (0)
		self.list_view.setHorizontalScrollMode (1)
		self.list_view.itemClicked.connect (self.show_image)
		self.list_view.setStyleSheet ("""
				QListWidget::item:hover {background: transparent;}
				QListWidget::item:disabled:hover {background: transparent;}
				QListWidget::item:hover:!active {background: transparent;}
				QListWidget::item:selected:active {background: transparent;}
	            QListWidget::item:selected:!active {background: transparent;}
	            QListWidget::item:selected:disabled {background: transparent;}
	            QListWidget::item:selected:!disabled {background: transparent;}
	            QListWidget {background: #2C3539}
			""")

		self.scene = QGraphicsScene ()
		self.viewer = QGraphicsView (self.scene)

		self.stackedWidget = QStackedWidget ()
		self.stackedWidget.addWidget (self.list_view)
		self.stackedWidget.addWidget (self.viewer)

		self.setCentralWidget (self.stackedWidget)
		self.resize (500, 400)
		self.showMaximized ()

		scan = ScanLibrary ("/home/chris/Example")
		threads.append (scan)
		self.connect (scan, SIGNAL (scan.signal), self.add_images_to_list)
		scan.start ()

	def add_images_to_list (self):
		for image in library:
			item = QListWidgetItem ()
			pixmap = QPixmap.fromImage (QImage (library[image]))
			label = QLabel ()
			label.setPixmap (pixmap.scaled (600, 400))
			item.setSizeHint (label.sizeHint ())
			item.setData (0, library[image])
			self.list_view.addItem (item)
			self.list_view.setItemWidget (item, label)

	def show_image (self, item):
		pass

class ScanLibrary (QThread):

	def __init__ (self, location):
		QThread.__init__ (self)
		self.location = location
		self.signal = "scan_finished"

	def run (self):
		for path, subdirs, files in os.walk(self.location):
			for f in files:
				location = os.path.join(path, f)
				extension = os.path.splitext(f)[1]
				if extension in extensions:
					name = os.path.basename(location)
					library[name] = location

		print (library)
		self.emit (SIGNAL(self.signal), 'Collection scan finished')

app = QApplication (sys.argv)
leapflow = LeapFlow ()
sys.exit (app.exec_())