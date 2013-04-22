import mock
import pyvvm.property as p

def test_bf():
    '''Create a property with a backing field'''

    class A(object):
        _foo = 0
        foo = p.property_a('_foo')

    a = A()

    a.foo = 10
    assert a.foo == a._foo == 10
    a._foo = 20
    assert a.foo == a._foo == 20

    assert A.foo.__get__(a) == 20

    A.foo.__set__(a, 30)
    assert a.foo == a._foo == 30

def test_conv():
    '''Have some fun with converters'''

    conv_read = mock.Mock(return_value='read')
    conv_show = mock.Mock(return_value='show')

    class A(object):
        foo = p.property_a('_foo', show=conv_show, read=conv_read)
        _foo = 'initial'

    a = A()

    # Reading
    assert a.foo == 'show'
    conv_show.assert_called_with('initial')

    # Writing
    assert a._foo == 'initial'
    a.foo = 'written'
    assert a._foo == 'read'
    conv_read.assert_called_with('written')

def test_backing():
    '''Try a viewmodel with a backing model'''

    class M(object):
        foo = 'initial'

    class A(object):

        foo = p.property_a('foo', '_model')

    model = M()
    a = A()
    a._model = model

    assert a.foo == model.foo == 'initial'
    a.foo = 20
    assert a.foo == model.foo == 20

def test_notify():
    '''Change notification, here we go!'''

    class A(object):

        _events = None
        _foo = 0
        foo = p.property_a('_foo', cn=True)

    cb = mock.Mock()
    cb.assert_called()

    a = A()

    A.foo.notify(a)

    A.foo.subscribe(a, cb)

    A.foo.notify(a)
    a.foo = 123
    del a.foo

    assert cb.call_count == 3


def test_enabled():
    '''Hook up a callback method for 'is_enabled' '''

    m = mock.Mock(return_value=False)

    class A(object):

        bar = p.property_a('_bar')

        @bar('enabled')
        def is_bar_enabled(self):
            return m(self)

    a = A()

    assert not A.bar.is_enabled(a)
    m.assert_called_with(a)

def test_plug_conv():
    '''Use a decorator to plug a member function converter!'''

    conv = mock.Mock()
    read = mock.Mock()

    class A(object):

        foo = p.property_a('_foo')
        _foo = 10

        @foo('show')
        def show_foo(self, value):
            return conv(self, value)

        @foo('read')
        def read_foo(self, value):
            return read(self, value)

    a = A()
    a.foo
    conv.assert_called_with(a, 10)
    a.foo = 20
    read.assert_called_with(a, 20)


