pngcanvas
=========

[![Build Status](https://travis-ci.org/rcarmo/pngcanvas.png?branch=master)](https://travis-ci.org/rcarmo/pngcanvas)
[![PyPI Version](https://img.shields.io/pypi/v/pngcanvas.svg)](https://pypi.python.org/pypi/pngcanvas/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/rcarmo/pngcanvas.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/rcarmo/pngcanvas/context:python)

A minimalist library to render PNG images using pure Python inspired by [Thomas Fuchs'][madrobby] [spark_pr][spark_pr] library, originally published [here][tom] in 2005.

Given that I get a couple of mails about it every quarter or so, and that it's been consistently popular with the [Google App Engine][gae] crowd, I decided to release it under the MIT license and welcome any contributions towards speeding it up, cleaning it up and making it generally more useful.

So ping me if you want commit access (or just send me a pull request with any enhancements).

## Features

As it stands, you can do the following things with a `PNGCanvas` instance:

* Set single pixels
* Draw antialiased lines and polylines
* Draw rectangles (outlined and filled)
* Draw vertical gradients
* Copy (and blend) a rectangular segment of the image onto another location
* Save it as a PNG file
* Load a PNG file into it (with some restrictions)

...all of it in pure Python.

[tom]: http://the.taoofmac.com/space/projects/PNGCanvas
[gae]: https://cloud.google.com/products/app-engine/
[madrobby]: https://github.com/madrobby
[spark_pr]: https://github.com/madrobby/spark_pr/blob/master/spark_pr.rb
