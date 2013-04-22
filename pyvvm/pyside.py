from PySide import QtGui, QtCore

import logging
logger = logging.getLogger(__name__)


class Listener(QtCore.QObject): 
    '''
    Use this as slot when you need a listener
    that will be persisted as long as the signalling object lives.

    Ctor adds this object as the child of the signalling object.
    '''

    def __init__(self, parent, callback):
        QtCore.QObject.__init__(self, parent)
        self.callback = callback

    def __call__(self, *args, **kwargs):
        self.callback(*args, **kwargs)


def hookup(model, control):
    field_name = control.objectName()

    # Combo box hack - allow the value to be encoded in the combo box
    # field_name, _, field_value = field_name.partition('__')
    
    field_property = getattr(type(model), field_name)

    if isinstance(control, QtGui.QCheckBox):
        hookQCheckBox(control, model, field_property)

    elif isinstance(control, QtGui.QPushButton):
        hookQPushButton(control, model, field_property)

    #elif isinstance(control, QtGui.QDialogButtonBox):
    #    hookQDialogButtonBox(control, getattr(model, field_name))

    #elif isinstance(control, QtGui.QRadioButton):
    #    hookQRadioButton(control, field_value, **field(model, field_name))

    elif isinstance(control, QtGui.QLineEdit):
        hookQLineEdit(control, model, field_property)

    # elif isinstance(control, QtGui.QSpinBox):       
    #    hookQSpinBox(control, **field(model, field_name))

    #elif isinstance(control, QtGui.QDoubleSpinBox):     
    #    hookQSpinBox(control, double=True, **field(model, field_name))

    #elif isinstance(control, QtGui.QComboBox):
    #    hookQComboBox(control, _variants_for(model, field_name), **field(model, field_name))

    else:
        raise ValueError('Unknown control type: {}'.format(type(control)))


def hookup_all(model, ui):
    for control in _all_children(ui):
        field_name = control.objectName()
        if not field_name:
            continue
        if '__' in field_name:
            field_name, _, _ = field_name.partition('__')
        if hasattr(model, field_name):
            hookup(model, control)



def _all_children(control):
    for child in control.children():
        yield child
        #yield from _all_children(child) # 3.3 <3
        for subchild in _all_children(child):
            yield subchild



def is_enabled(property, model):
    try:
        return property.is_enabled(model)
    except:
        return True

def hookQLineEdit(e, model, property):

    def update_model():
        property.__set__(model, e.text())
    def update_view():
        e.setText(property.__get__(model))
        e.setEnabled(is_enabled(property, model))

    update_view()

    e.editingFinished.connect(Listener(e, update_model))
    if hasattr(property, 'subscribe'):
        property.subscribe(model, Listener(e, update_view))


def hookQComboBox(e, items, initial=-1, cb=None):
    model = QtGui.QStringListModel(items, e)
    e.setModel(model)
    e.setCurrentIndex(initial if initial is not None else -1)
    if cb:
        def cb2(n):
            return cb(n) if n != -1 else cb(None)
        e.currentIndexChanged.connect(Listener(e, cb2))
    return e


def hookQComboBox2(e, items, initial=None, cb=None, fmt=unicode):
    model = QtGui.QStringListModel(map(fmt, items), e)
    e.setModel(model)
    try:
        e.setCurrentIndex(items.index(initial))
    except:
        e.setCurrentIndex(-1)
    if cb:
        def cb2(n):
            return cb(items[n])
        e.currentIndexChanged.connect(Listener(e, cb2))
    return e


def hookQCheckBox(e, model, property):

    def update_model(arg):
        property.__set__(model, e.isChecked())
    def update_view():
        e.setChecked(property.__get__(model))

    update_view()

    e.toggled.connect(Listener(e, update_model))
    if hasattr(property, 'subscribe'):
        property.subscribe(model, Listener(e, update_view))

def makeQSpinBox(parent, range, double=False, decimals=None, step=None, initial=None, cb=None):
    if not double:
        e = QtGui.QSpinBox(parent)
    else:
        e = QtGui.QDoubleSpinBox(parent)
    return hookQSpinBox(e, range, double, decimals, step, initial, cb)

def hookQSpinBox(e, range=None, double=False, decimals=None, step=None, initial=None, cb=None):
    if range is not None:
        e.setRange(*range)
    if decimals is not None:
        e.setDecimals(decimals)
    if step is not None:
        e.setSingleStep(step)
    e.setValue(initial)
    if cb:
        # TODO is that correct?
        e.valueChanged[float if double else int].connect(Listener(e, cb))
    return e


from functools import partial
makeQDoubleSpinBox=partial(makeQSpinBox, double=True)
hookQDoubleSpinBox=partial(hookQSpinBox, double=True)

def hookQPushButton(e, model, property):

    def action():
        # Yeah, look up the actual callback on every click.
        # It might change.
        property.__get__(model)()

    # Change subscription will be useful when handling .enabled()

    e.clicked.connect(Listener(e, action))


def hookQRadioButton(e, val, initial=None, cb=None):

    e.setChecked(initial == val)

    def clicked(checked):
        if checked:
            cb(val)
        else:
            raise ValueError("not checked? on a radio?")
    if cb:
        e.connect(QtCore.SIGNAL('clicked(bool)'), Listener(e, clicked))
        #TODO how about this?
        #e.clicked[bool].connect(Listener(e, clicked))

    return e




def prop_setter(obj, prop, conv=None): # This un goes to utils
    def set(val):
        try:
            val = conv(val) if conv else val
        except:
            logger.info('Conversion error with',val)
        else:
            logger.info('setting {} of {} to {!r}'.format(prop, obj, val))
            setattr(obj, prop, val)
    return set

def item_setter(obj, item, conv=None): # This un goes to utils
    def set(val):
        try:
            val = conv(val) if conv else val
        except:
            logger.info('Conversion error with',val)
        else:
            logger.info('setting item {} of {} to {!r}'.format(item, obj, val))
            obj[item] = val
    return set


def field(obj, prop, conv=None):
    return {'initial': getattr(obj, prop), 'cb': prop_setter(obj, prop, conv) }

def item(obj, idx, conv=None):
    return {'initial': obj[idx], 'cb': item_setter(obj, idx, conv) }    
