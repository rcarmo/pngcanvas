pngcanvas
=========

A minimalist library to render PNG images using pure Python, originally published [here][tom] in 2005.

Given that I get a couple of mails about it every quarter or so, and that it's been consistently popular with the [Google App Engine][gae] crowd, I decided to release it under the MIT license and welcome any contributions towards speeding it up, cleaning it up and making it generally more useful.

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
