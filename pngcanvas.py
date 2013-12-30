"""Simple PNG Canvas for Python - updated for bytearray()"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

__version__ = "1.0.3"
__license__ = "MIT"


import struct
import sys
import zlib


# Py2 - Py3 compatibility
if sys.version < '3':
    range = xrange  # NOQA


SIGNATURE = struct.pack(b"8B", 137, 80, 78, 71, 13, 10, 26, 10)


def force_int(*args):
    return tuple(int(x) for x in args)


def blend(c1, c2):
    """Alpha blends two colors, using the alpha given by c2"""
    return [c1[i] * (0xFF - c2[3]) + c2[i] * c2[3] >> 8 for i in range(3)]


def intensity(c, i):
    """Compute a new alpha given a 0-0xFF intensity"""
    return [c[0], c[1], c[2], (c[3] * i) >> 8]


def grayscale(c):
    """Compute perceptive grayscale value"""
    return int(c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11)


def gradient_list(start, end, steps):
    """Compute gradient colors"""
    delta = [end[i] - start[i] for i in range(4)]
    return [bytearray(start[j] + (delta[j] * i) // steps for j in range(4))
            for i in range(steps + 1)]


class PNGCanvas(object):
    def __init__(self, width, height,
                 bgcolor=(0xff, 0xff, 0xff, 0xff),
                 color=(0, 0, 0, 0xff)):
        self.width = width
        self.height = height
        self.color = bytearray(color)  # rgba
        self.bgcolor = bytearray(bgcolor)
        self.canvas = bytearray(self.bgcolor * width * height)

    def _offset(self, x, y):
        """Helper for internal data"""
        x, y = force_int(x, y)
        return y * self.width * 4 + x * 4

    def point(self, x, y, color=None):
        """Set a pixel"""
        if x < 0 or y < 0 or x > self.width - 1 or y > self.height - 1:
            return
        if color is None:
            color = self.color
        o = self._offset(x, y)

        self.canvas[o:o + 3] = blend(self.canvas[o:o + 3], bytearray(color))

    @staticmethod
    def rect_helper(x0, y0, x1, y1):
        """Rectangle helper"""
        x0, y0, x1, y1 = force_int(x0, y0, x1, y1)
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        return x0, y0, x1, y1

    def vertical_gradient(self, x0, y0, x1, y1, start, end):
        """Draw a vertical gradient"""
        x0, y0, x1, y1 = self.rect_helper(x0, y0, x1, y1)
        grad = gradient_list(start, end, y1 - y0)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.point(x, y, grad[y - y0])

    def rectangle(self, x0, y0, x1, y1):
        """Draw a rectangle"""
        x0, y0, x1, y1 = self.rect_helper(x0, y0, x1, y1)
        self.polyline([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]])

    def filled_rectangle(self, x0, y0, x1, y1):
        """Draw a filled rectangle"""
        x0, y0, x1, y1 = self.rect_helper(x0, y0, x1, y1)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.point(x, y, self.color)

    def copy_rect(self, x0, y0, x1, y1, dx, dy, destination):
        """Copy (blit) a rectangle onto another part of the image"""
        x0, y0, x1, y1 = self.rect_helper(x0, y0, x1, y1)
        dx, dy = force_int(dx, dy)

        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                d = destination._offset(dx + x - x0, dy + y - y0)
                o = self._offset(x, y)
                destination.canvas[d:d + 4] = self.canvas[o:o + 4]

    def blend_rect(self, x0, y0, x1, y1, dx, dy, destination, alpha=0xff):
        """Blend a rectangle onto the image"""
        x0, y0, x1, y1 = self.rect_helper(x0, y0, x1, y1)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                o = self._offset(x, y)
                rgba = self.canvas[o:o + 4]
                rgba[3] = alpha
                destination.point(dx + x - x0, dy + y - y0, rgba)

    def line(self, x0, y0, x1, y1):
        """Draw a line using Xiaolin Wu's antialiasing technique"""
        # clean params
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        if y0 > y1:
            y0, y1, x0, x1 = y1, y0, x1, x0
        dx = x1 - x0
        if dx < 0:
            sx = -1
        else:
            sx = 1
        dx *= sx
        dy = y1 - y0

        # 'easy' cases
        if dy == 0:
            for x in range(x0, x1, sx):
                self.point(x, y0)
            return
        if dx == 0:
            for y in range(y0, y1):
                self.point(x0, y)
            self.point(x1, y1)
            return
        if dx == dy:
            for x in range(x0, x1, sx):
                self.point(x, y0)
                y0 += 1
            return

        # main loop
        self.point(x0, y0)
        e_acc = 0
        if dy > dx:  # vertical displacement
            e = (dx << 16) // dy
            for i in range(y0, y1 - 1):
                e_acc_temp, e_acc = e_acc, (e_acc + e) & 0xFFFF
                if e_acc <= e_acc_temp:
                    x0 += sx
                w = 0xFF-(e_acc >> 8)
                self.point(x0, y0, intensity(self.color, w))
                y0 += 1
                self.point(x0 + sx, y0, intensity(self.color, (0xFF - w)))
            self.point(x1, y1)
            return

        # horizontal displacement
        e = (dy << 16) // dx
        for i in range(x0, x1 - sx, sx):
            e_acc_temp, e_acc = e_acc, (e_acc + e) & 0xFFFF
            if e_acc <= e_acc_temp:
                y0 += 1
            w = 0xFF-(e_acc >> 8)
            self.point(x0, y0, intensity(self.color, w))
            x0 += sx
            self.point(x0, y0 + 1, intensity(self.color, (0xFF-w)))
        self.point(x1, y1)

    def polyline(self, arr):
        """Draw a set of lines"""
        for i in range(0, len(arr) - 1):
            self.line(arr[i][0], arr[i][1], arr[i + 1][0], arr[i + 1][1])

    def dump(self):
        """Dump the image data"""
        scan_lines = bytearray()
        for y in range(self.height):
            scan_lines.append(0)  # filter type 0 (None)
            scan_lines.extend(
                self.canvas[(y * self.width * 4):((y + 1) * self.width * 4)]
            )
        # image represented as RGBA tuples, no interlacing
        return SIGNATURE + \
            self.pack_chunk(b'IHDR', struct.pack(b"!2I5B",
                                                 self.width, self.height,
                                                 8, 6, 0, 0, 0)) + \
            self.pack_chunk(b'IDAT', zlib.compress(bytes(scan_lines), 9)) + \
            self.pack_chunk(b'IEND', b'')

    @staticmethod
    def pack_chunk(tag, data):
        """Pack a PNG chunk for serializing to disk"""
        to_check = tag + data
        return (struct.pack(b"!I", len(data)) + to_check +
                struct.pack(b"!I", zlib.crc32(to_check) & 0xFFFFFFFF))

    def load(self, f):
        """Load a PNG image"""
        assert f.read(8) == SIGNATURE

        chunks = iter(self.chunks(f))
        header = next(chunks)
        assert header[0] == b'IHDR'

        (width, height, bit_depth, color_type, compression,
         filter_type, interlace) = struct.unpack(b"!2I5B", header[1])

        if (bit_depth, color_type, compression,
                filter_type, interlace) != (8, 6, 0, 0, 0):
            raise TypeError('Unsupported PNG format')

        self.width = width
        self.height = height
        self.canvas = bytearray(self.bgcolor * width * height)
        row_size = width * 4
        step_size = 1 + row_size

        # Python 2 requires the encode for struct.unpack
        row_fmt = ('!%dB' % step_size).encode('ascii')

        for tag, data in chunks:
            # we ignore tRNS for the moment
            if tag != b'IDAT':
                continue

            raw_data = zlib.decompress(data)
            old_row = None
            cursor = 0
            for i in range(0, height * step_size, step_size):
                unpacked = struct.unpack(row_fmt, raw_data[i:i + step_size])
                old_row = self.defilter(unpacked[1:], old_row, filter_type)
                self.canvas[cursor:cursor + row_size] = old_row
                cursor += row_size

    @staticmethod
    def defilter(cur, prev, filter_type, bpp=4):
        """Decode a chunk"""
        if filter_type == 0:  # No filter
            return cur
        elif filter_type == 1:  # Sub
            xp = 0
            for xc in range(bpp, len(cur)):
                cur[xc] = (cur[xc] + cur[xp]) % 256
                xp += 1
        elif filter_type == 2:  # Up
            for xc in range(len(cur)):
                cur[xc] = (cur[xc] + prev[xc]) % 256
        elif filter_type == 3:  # Average
            xp = 0
            for xc in range(len(cur)):
                cur[xc] = (cur[xc] + (cur[xp] + prev[xc]) // 2) % 256
                xp += 1
        elif filter_type == 4:  # Paeth
            xp = 0
            for i in range(bpp):
                cur[i] = (cur[i] + prev[i]) % 256
            for xc in range(bpp, len(cur)):
                a = cur[xp]
                b = prev[xc]
                c = prev[xp]
                p = a + b - c
                pa = abs(p - a)
                pb = abs(p - b)
                pc = abs(p - c)
                if pa <= pb and pa <= pc:
                    value = a
                elif pb <= pc:
                    value = b
                else:
                    value = c
                cur[xc] = (cur[xc] + value) % 256
                xp += 1
            else:
                raise TypeError('Unrecognized scanline filter type')
        return cur

    @staticmethod
    def chunks(f):
        """Split read PNG image data into chunks"""
        while 1:
            try:
                length = struct.unpack(b"!I", f.read(4))[0]
                tag = f.read(4)
                data = f.read(length)
                crc = struct.unpack(b"!I", f.read(4))[0]
            except struct.error:
                return
            if zlib.crc32(tag + data) & 0xFFFFFFFF != crc:
                raise IOError('Checksum fail')
            yield tag, data
