#!/usr/bin/env python

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import io
import logging
import unittest

from pngcanvas import *


BUFSIZE = 8*1024  # Taken from filecmp module
HEIGHT = WIDTH = 512


class CanvasTest(unittest.TestCase):
    @staticmethod
    def compare(s1, s2):
        while True:
            b1 = s1.read(BUFSIZE)
            b2 = s2.read(BUFSIZE)
            if b1 != b2:
                return False
            if not b1:
                return True

    def test_generation(self):
        logging.debug("Creating canvas: %d, %d", WIDTH, HEIGHT)
        c = PNGCanvas(WIDTH, HEIGHT, color=(0xff, 0, 0, 0xff))
        c.rectangle(0, 0, WIDTH - 1, HEIGHT - 1)

        logging.debug("Generating gradient...")
        c.vertical_gradient(1, 1, WIDTH - 2, HEIGHT - 2,
                            (0xff, 0, 0, 0xff), (0x20, 0, 0xff, 0x80))

        logging.debug("Drawing some lines...")
        c.color = bytearray((0, 0, 0, 0xff))
        c.line(0, 0, WIDTH - 1, HEIGHT - 1)
        c.line(0, 0, WIDTH / 2, HEIGHT - 1)
        c.line(0, 0, WIDTH - 1, HEIGHT / 2)

        logging.debug("Copy rect to self...")
        c.copy_rect(1, 1, WIDTH / 2 - 1, HEIGHT / 2 - 1, 1, HEIGHT / 2, c)

        logging.debug("Blend rect to self...")
        c.blend_rect(1, 1, WIDTH / 2 - 1, HEIGHT / 2 - 1, WIDTH / 2, 0, c)

        with io.open('reference.png', 'rb') as reference:
            with io.BytesIO() as test:
                logging.debug("Writing to file...")
                test.write(c.dump())
                test.seek(0)

                logging.debug("Comparing with the reference...")
                self.assertTrue(self.compare(reference, test))

    def test_read_consistency(self):
        c = PNGCanvas(WIDTH, HEIGHT, color=(0xff, 0, 0, 0xff))

        with io.open('reference.png', 'rb') as reference:
            with io.BytesIO() as test:
                logging.debug("Loading the reference...")
                c.load(reference)

                logging.debug("Writing what is read to file...")
                test.write(c.dump())

                reference.seek(0)
                test.seek(0)

                logging.debug("Comparing with the reference...")
                self.assertTrue(self.compare(reference, test))

    def test_multi_idat(self):
        ref = PNGCanvas(WIDTH, HEIGHT, color=(0xff, 0, 0, 0xff))
        ref_multi = PNGCanvas(WIDTH, HEIGHT, color=(0xff, 0, 0, 0xff))

        with io.open('reference-multi-idat.png', 'rb') as f:
            ref_multi.load(f)

        with io.open('reference.png', 'rb') as f:
            ref.load(f)

        self.assertEqual(ref_multi.canvas, ref.canvas)



if __name__ == '__main__':
    unittest.main()
