from setuptools import setup

from setuputils import find_version

setup(
    name='pngcanvas',
    version=find_version('pngcanvas.py'),
    description='A minimalist library to render PNG images using pure Python.',
    py_modules=['pngcanvas', 'setuputils'],
    author='Rui Carmo',
    author_email='rcarmo@gmail.com',
    url='https://github.com/rcarmo/pngcanvas',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: MIT License',
    ],
)
