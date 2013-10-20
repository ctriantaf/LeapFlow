#!/usr/bin/env python3

import sys, os
from PyQt4.QtGui import (QMainWindow, QApplication, QPixmap, QImage, QListWidget, QListWidgetItem, QIcon, QLabel, QStackedWidget,
						QGraphicsScene, QGraphicsView)
from PyQt4.QtCore import SIGNAL, QThread, QSize
from Leap import Controller
from LeapListener import LeapListener

threads = []
library = {}

extensions = ['.jpg', '.jpeg', '.png']

class LeapFlow (QMainWindow):

	def __init__ (self):
		QMainWindow.__init__ (self)

		self.controller = Controller ()
		self.listener = LeapListener (self)
		self.controller.add_listener (self.listener)

		self.mode = "gallery"
		self.scroll = False
		self.direction = ""
		self.direction_x = 0
		self.scroll_velocity = 0
		self.current_index = 0

		# List containing images for the gallery
		self.list_view = QListWidget ()
		self.list_view.setFlow (0)
		self.list_view.setHorizontalScrollMode (1)
		self.list_view.setMouseTracking (True)
		self.list_view.itemClicked.connect (self.show_image)

		# Setting the style of the ListView, background, item selected, etc
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

		# Image viewer
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

		self.connect (self, SIGNAL ("scrollChanged(bool)"), self.scroll_view)

	def setScroll (self, scroll):
		"""Emit signal to scroll the view"""
		if (self.scroll != scroll):
			self.scroll = scroll
			self.emit (SIGNAL("scrollChanged(bool)"), scroll)

	def scroll_view (self):
		"""Scroll the view based on scroll velocity and direction"""

		x = self.direction_x * self.scroll_velocity / 100
		bar_x = self.list_view.horizontalScrollBar ().value ()
		self.list_view.horizontalScrollBar ().setValue (bar_x + x)

	def add_images_to_list (self):
		"""To add a widget to the listview you must add a QListWidgetItem
		and replace with your widget"""

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
		""""Display the selected image"""

		self.current_index = self.list_view.indexFromItem (item).row ()
		self.scene.addPixmap ((QPixmap.fromImage (QImage (item.text()))).scaled (self.viewer.size()))

		self.stackedWidget.setCurrentIndex (1)
		self.mode = "viewer"

	def previous_image (self):
		"""Load previous image"""

		if self.current_index - 1 >= 0:
			self.current_index -= 1
			self.load_image ()

	def next_image (self):
		"""Load next image"""

		if self.current_index + 1 <= len(library.keys ()) - 1:
			self.current_index += 1
			self.load_image ()

	def load_image (self):
		"""Load the image in self.current_index"""

		self.scene.addPixmap (QPixmap.fromImage (QImage (library[library.keys()[self.current_index]])))

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