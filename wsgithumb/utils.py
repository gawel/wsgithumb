# -*- coding: utf-8 -*-
# this came from http://docs.webob.org/en/latest/file-example.html
import mimetypes
import os

try:
    from pyramid.response import Response
except ImportError:
    from webob import Response  # NOQA

try:
    from pyramid.httpexceptions import HTTPNotFound
except ImportError:
    from webob.exc import HTTPNotFound  # NOQA

try:
    import PIL.Image as Image
except ImportError:
    import Image  # NOQA


def resize(src, dst, size, mode='r'):
    """resize an image to size"""
    image = Image.open(src, mode)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(dst)
    return dst


class FileIterable(object):

    def __init__(self, filename, start=None, stop=None):
        self.filename = filename
        self.start = start
        self.stop = stop

    def __iter__(self):
        return FileIterator(self.filename, self.start, self.stop)

    def app_iter_range(self, start, stop):
        return self.__class__(self.filename, start, stop)


class FileIterator(object):

    chunk_size = 4096

    def __init__(self, filename, start, stop):
        self.filename = filename
        self.fileobj = open(self.filename, 'rb')
        if start:
            self.fileobj.seek(start)
        if stop is not None:
            self.length = stop - start
        else:
            self.length = None

    def __iter__(self):
        return self

    def next(self):
        if self.length is not None and self.length <= 0:
            try:
                self.fileobj.close()
            finally:
                raise StopIteration
        chunk = self.fileobj.read(self.chunk_size)
        if not chunk:
            try:
                self.fileobj.close()
            finally:
                raise StopIteration
        if self.length is not None:
            self.length -= len(chunk)
            if self.length < 0:
                # Chop off the extra:
                chunk = chunk[:self.length]
        return chunk
    __next__ = next  # py3 compat


def get_mimetype(filename):
    type, encoding = mimetypes.guess_type(filename)
    # We'll ignore encoding, even though we shouldn't really
    return type or 'application/octet-stream'


def get_file_response(filename, document_root=None, accel_header=None):
    """helper the get a file response"""
    if not os.path.isfile(filename):
        return HTTPNotFound()
    resp = Response(content_type=get_mimetype(filename),
                    conditional_response=True)
    resp.content_length = os.path.getsize(filename)
    resp.last_modified = os.path.getmtime(filename)
    resp.etag = '%s-%s-%s' % (os.path.getmtime(filename),
                              os.path.getsize(filename), hash(filename))
    if accel_header:
        if accel_header.lower() == "x-accel-redirect":
            # return full path
            filename = filename[len(os.path.dirname(document_root)):]
            filename = '/%s' % filename.strip('/')
            resp.headers[accel_header.title()] = filename
        elif accel_header.lower() == "x-sendfile":
            # return full path
            resp.headers[accel_header.title()] = filename
        else:
            raise RuntimeError(
                    "Can't find a way to use your %s header" % accel_header)
        resp.app_iter = ['']
    else:
        resp.app_iter = FileIterable(filename)
    return resp
