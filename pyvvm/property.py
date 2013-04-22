import weakref

def identity(x):
    return x

# TODO what about hooking up custom storage easily, like property(**foo)?
# TODO and .getter, .setter, .deleter?

class Property(object):
    '''An extended property object that supports interesting stuff.

    Property(storage, **kwargs) -> extended property object 

    Arguments:
    - storage (required):
        An object that describes where to keep this property's value.
        Examples:
        - `Field(name) - a backing field in same object (`.name`)
        - `ModelField(name, model) - a field in another object (`.model.name`)

    - event_storage (default: None)
        Where to keep this object's event jar (see `storage`).
        If not provided, the object doesn't allow subscribing for change notification.
        `Field('_events')` looks like a good choice. (TODO: make it default?)

    - read (default: identity)
        A callable; how to convert from this field's value to stored value.
    - show (default: identity)
        A callable; how to convert from stored value to this field's value.

    Decorate methods with the property to provide additional functionality. See help(property.__call__)

    '''

    def __init__(self, storage, event_storage=None, read=identity, show=identity):
        self._storage = storage
        self._event_storage = event_storage
        self._read, self._show = read, show
        # Provide the `subscribe` method only if there's storage for the events
        if event_storage is not None:
            self.subscribe = self._subscribe

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        uvalue = self._storage[obj]
        return self._show(uvalue) if self._mshow is None else self._mshow(obj, uvalue)

    def __set__(self, obj, uvalue):
        value = self._read(uvalue) if self._mread is None else self._mread(obj, uvalue)
        value_prev = self._storage[obj]
        if value != value_prev:
            self._storage[obj] = value
            self.notify(obj)

    def __delete__(self, obj):
        del self._storage[obj]
        self.notify(obj)

    def notify(self, obj, *args, **kwargs):
        '''
        notify(obj, *args, **kwargs) -- notifies all listeners subscribed to an object
        '''
        if not self._event_storage:
            # Return silently; there are no listeners anyway
            return

        for cb in self._event_storage[obj] or ():
            cb(*args, **kwargs)

    def _subscribe(self, obj, cb):
        assert self._event_storage
        if self._event_storage[obj] is None:
            # Prepare a default event
            self._event_storage[obj] = weakref.WeakSet()
        self._event_storage[obj].add(cb)

    def __call__(self, name):
        '''
        Intended to be used with decorator syntax. 
        Allows to enrich this this property with more callbacks.

        The following are supported:

        - @my_property('enabled')
            Provides an `is_enabled` implementation for this property.
        
        - @my_property('read')
            Provides a converter from this field's value to stored value.

            This is different than the constructor's `read` parameter;
            this callback is called with (object, value) so it can be a method.

        - @my_property('show')
            Provides a converter from stored value to this field's value.

            This is different than the constructor's `show` parameter;
            this callback is called with (object, value) so it can be a method.

        '''
        return getattr(self, 'def_'+name)

    def def_show(self, cb):
        self._mshow = cb
        return cb

    def def_read(self, cb):
        self._mread = cb
        return cb

    def def_enabled(self, cb):
        self.is_enabled = cb
        return cb


    _mread = None
    _mshow = None


def property_a(name, model=None, cn=False, **kwargs):
    # WHAT SHOULD THE DEFAULT BE?
    if model is None:
        storage = Field(name)
    else:
        storage = ModelField(name, model)
    if cn:
        event_storage = EventStorage(name)
    else:
        event_storage = None
    return Property(storage, event_storage, **kwargs)


class Field(object):

    def __init__(self, name):
        self.name = name

    def __getitem__(self, object):
        return getattr(object, self.name)

    def __setitem__(self, object, value):
        setattr(object, self.name, value)

    def __delitem__(self, object):
        delattr(object, self.name)


class ModelField(object):

    def __init__(self, name, modelname):
        self.name = name
        self.modelname = modelname

    def __getitem__(self, object):
        return getattr(getattr(object, self.modelname), self.name)

    def __setitem__(self, object, value):
        setattr(getattr(object, self.modelname), self.name, value)
        
    def __delitem__(self, object):
        delattr(getattr(object, self.modelname), self.name)

class EventStorage(object):

    # TODO revamp to use one dict

    def __init__(self, name):
        self.name = name
        self.propname = '_events_{0}'.format(name)

    def __getitem__(self, object):
        return getattr(object, self.propname, None)

    def __setitem__(self, object, value):
        setattr(object, self.propname, value)

    def __delitem__(self, object):
        delattr(object, self.name)
