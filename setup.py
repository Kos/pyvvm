from setuptools import setup

# Workaround for
# http://www.eby-sarna.com/pipermail/peak/2010-May/003355.html
import multiprocessing; multiprocessing

# Oh, I'm supposed to name this thing.
# Later, OK?

setup(name='pyvvm',
      version='0.1',
      description='An MVVM microframework',
      url='http://github.com/KosGD/pyvvm',
      author='Tomasz Wesolowski',
      author_email='kosashi@gmail.com',
      license='MIT',
      packages=['pyvvm'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      )

