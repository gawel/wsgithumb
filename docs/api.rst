======================
:mod:`wsgithumb` API
======================

WSGI Applications
==================

.. autofunction:: wsgithumb.make_thumb_app

.. autofunction:: wsgithumb.make_file_app

Pyramid
========

.. autofunction:: wsgithumb.add_thumb_view

Helpers
========

Serving files
-------------

While it's not it's primary function, **wsgithumb** allow to efficiently serve a
file with the :func:`~wsgithumb.get_file_response` helper::

    >>> from wsgithumb import get_file_response
    >>> from tests import document_root
    >>> from tests import filename
    >>> resp = get_file_response(filename, document_root=document_root,
    ...                          accel_header=None)
    >>> print(resp)
    200 OK
    Content-Type: text/x-python; charset=UTF-8
    Last-Modified: ... GMT
    ETag: "..."
    Content-Length: 114
    ...

.. autofunction:: wsgithumb.get_file_response

Generating thumbnails
----------------------

You want to serve images located in ``document_root``. Use the
:func:`~wsgithumb.get_image_response` helper::

    >>> from wsgithumb import get_image_response
    >>> from tests import document_root
    >>> resp = get_image_response(document_root=document_root,
    ...                           cache_directory='/tmp/www/cache',
    ...                           size=(500, 500), path='tests/image.jpg',
    ...                           accel_header=None)
    >>> print(resp)
    200 OK
    Content-Type: image/jpeg
    Last-Modified: ... GMT
    ETag: "..."
    Content-Length: ...
    ...

This will return a ``webob.Response`` containing a resized version of
``document_root/tests/image.jpg``. If size is None then the file is returned without resizing.

.. autofunction:: wsgithumb.get_image_response

..
    >>> import shutil
    >>> shutil.rmtree('/tmp/www')
