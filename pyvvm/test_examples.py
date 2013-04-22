from PySide import QtGui
from pyvvm import property as pr, pyside, demoutil


def example_view():
	return demoutil.make_window([
		('text',   QtGui.QLineEdit()),
		('switch', QtGui.QCheckBox()),
		('action', QtGui.QPushButton(text='fire')),
	])



@demoutil.pyside_test
def test_example1():
	'''
	The simplest case that shows how a view model can be 
	automatically connected with a view (window).
	'''

	class Model(object):

		def __init__(self):
			self._text = 'initial text'
			self._switch = True

		text = pr.property_a('_text')
		switch = pr.property_a('_switch')

		def action(self):
			print 'Action fired', self.text, self.switch


	# Create a model and a Qt window.
	# Link them automatically via object names and property names

	model = Model()
	view = example_view()
	pyside.hookup_all(model, view)

	# The initial model value is propagated to the view

	assert view.text.text() == 'initial text'

	# Changes in the view go back to the model
	
	view.text.setText('changed')
	view.text.editingFinished.emit()
	assert model._text == 'changed'
	


@demoutil.pyside_test
def test_example2():
	'''
	This case shows how properties with change notification
	allow for 2-way data binding.
	'''

	class Model(object):

		def __init__(self):
			self._text = 'text'
			self._switch = True
			self._count = 0

		text   = pr.property_a('_text', cn=True)
		switch = pr.property_a('_switch', cn=True)

		def action(self):
			self.text += ' ... and more'

	model = Model()
	view = example_view()
	pyside.hookup_all(model, view)

	# Likewise, the view is initialised to the initial values from the model
	# However, further model edits now get propagated too

	assert view.text.text() == 'text'

	view.action.click()
	assert view.text.text() == model._text == 'text ... and more'

	# Change notification is automatically triggered when setting the property,
	# but not when directly editing the backing field, of course:

	model._text = 'something else'
	assert view.text.text() == 'text ... and more'

	# But you can fire the change notification manually anytime

	Model.text.notify(model)
	assert view.text.text() == 'something else'



@demoutil.pyside_test
def test_converters():
	'''
	We'll show two things in this example:
	- how the property data can be sourced externally,
	- how to do some conversions
	'''

	class Model(object):

		value = 10

	class ViewModel(object):

		text    = pr.property_a('value', '_model', show=str, read=int)


	model = Model()
	viewmodel = ViewModel()
	viewmodel._model = model

	view = example_view()
	pyside.hookup_all(viewmodel, view)

	# Now the property is accessible as `text` in the viewmodel,
	# but the value is sourced from `._model.value`
	# and also converted using given functions (`str` and `read` respectively).

	assert model.value == 10
	assert viewmodel.text == view.text.text() == '10'

	view.text.setText('  20  ')
	view.text.editingFinished.emit()

	assert model.value == 20
	assert viewmodel.text == '20'
	assert view.text.text() == '  20  '

	# Note: The value in the view still has the spaces, just as typed.
	# But the viewmodel doesn't know of these spaces - 
	# - when asked about the value, converts and gives the current model's value.

	# Interestingly, if the viewmodel's property had change notification,
	# the view-triggered change would ring a callback back to the view, 
	# and the view would update with the converted '20' without spaces.

	# Let us verify that:
	ViewModel.text = pr.property_a('value','_model', cn=True, show=str, read=int)

	view = example_view()
	pyside.hookup_all(viewmodel, view)

	view.text.setText('  30 ')
	view.text.editingFinished.emit()

	assert model.value == 30
	assert viewmodel.text == view.text.text() == '30'


@demoutil.pyside_test
def test_enabled():
	'''
	Metadata example. Plug a method to indicate when a property is "enabled". 
	'''

	class Model(object):

		switch = pr.property_a('_switch', cn=True)
		text   = pr.property_a('_text', cn=True)

		_switch = True
		_text = 'text'

		@text('enabled')
		def textbox_enabled(self):
			return self.switch


	model = Model()

	# The above setup allows to check if 'text' is enabled at a given moment

	model.switch = False
	assert not Model.text.is_enabled(model)
	model.switch = True
	assert Model.text.is_enabled(model)

	# However, the view will need to be notified that
	# something about property 'text' changes whenever the property 'switch' changes.
	# But that's why we have change notification:

	def callback():
		Model.text.notify(model)

	Model.switch.subscribe(model, callback)

	# We're basically telling the property `switch` to call the callback whenever it changes,
	# in order to instruct the property `text` to tell all interested views that it changed too.

	# Let's see it in action:

	view = example_view()
	pyside.hookup_all(model, view)

	assert model.switch == True
	assert view.text.isEnabled()

	view.switch.setChecked(False)
	assert not view.text.isEnabled()


# demo : variants