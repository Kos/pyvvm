import functools
from PySide import QtGui

def make_window(elements):

	wnd = QtGui.QWidget(None)
	layout = QtGui.QVBoxLayout(wnd)

	def add_widget(name, widget):
		widget.setParent(wnd)
		widget.setObjectName(name)
		layout.addWidget(widget)
		setattr(wnd, name, widget)

	for element in elements:
		add_widget(*element)

	return wnd

def pyside_test(func):
	@functools.wraps(func)
	def wrapped():
		app = QtGui.QApplication.instance() or QtGui.QApplication([])
		try:
			func()
		finally:
			app.quit()
	return wrapped