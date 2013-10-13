#!/usr/bin/env python3

import sys, os
from PyQt4.QtGui import QMainWindow, QApplication, QPixmap, QImage, QListWidget, QListWidgetItem, QIcon, QLabel
from PyQt4.QtCore import SIGNAL, QThread, QSize

threads = []
library = {}

extensions = ['.jpg', '.jpeg', '.png']

class LeapFlow (QMainWindow):

	def __init__ (self):
		QMainWindow.__init__ (self)

		self.list_view = QListWidget ()
		self.list_view.setFlow (0)

		self.setCentralWidget (self.list_view)
		self.resize (500, 400)
		self.show ()

		scan = ScanLibrary ("/home/chris/Pictures")
		threads.append (scan)
		self.connect (scan, SIGNAL (scan.signal), self.add_images_to_list)
		scan.start ()

	def add_images_to_list (self):
		for image in library:
			item = QListWidgetItem ()
			pixmap = QPixmap.fromImage (QImage (library[image]))
			label = QLabel ()
			label.setPixmap (pixmap.scaled (200, 200))
			item.setSizeHint (label.sizeHint ())
			self.list_view.addItem (item)
			self.list_view.setItemWidget (item, label)

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