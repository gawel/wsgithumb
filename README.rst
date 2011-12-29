wsgithumb
=========

wsgithumb provide some utilities to serve files and images for WebOb based applications.


Installation
-------------

Use easy_install or pip::

    $ pip install wsgithumb

Generating thumbnails
----------------------

You want to serve images located in ``/foo``. Use the ``get_image_response`` helper::

    >>> def get_image_response(document_root='/foo', cache_directory='/tmp/cache',
    ...                        size=(500, 500), path='/image.png', accel_header=None)

This will return a ``webob.Response`` containing a resized version of
``/foo/image.png``. If size is None then the file is returned without resizing.

Serving files
-------------

While it's not it's primary function, wsgithumb allow to efficiently serve a file::

    >>> get_file_response(filename, accel_header=accel_header,
    ...                   document_root=document_root)

Accel headers
--------------

Moderns web servers like NGinx or Apache implement the ``X-Sendfile`` feature.
This allow your application to only return the file path in a response header
the the web server will use this path to serve the file without blocking your
application.

wsgithumb allow you to use this feature. Just use the accel_header parameter.

For NGinx, set ``accel_header="x-accel-redirect:/path/bound/by/nginx"``

For Apache, set ``accel_header="x-sendfile"``

Using wsgithumb in Pyramid
--------------------------

There is an helper in wsgithumb to help you to serve thumnails in your application.

Add this to your ``.ini`` file::

    [app:main]
    ...
    thumbs.document_root = %(here)s/www/images
    thumbs.cache_directory = %(here)s/www/cache
    # if you want to use the accel_header when in production
    #thumbs.accel_header = x-accel-redirect:/thumbs/cache

Add this to your ``__init__.py``::

    sizes = {
        'thumb': (100, 100),
        'large': (500, 500),
        'original': None,
        }
    config.add_thumb_view('thumbs', sizes=DEFAULT_SIZES)

If you do not provide some sizes then those are used::

    DEFAULT_SIZES = {
        'icon': (16, 16),
        'small': (50, 50),
        'thumb': (100, 100),
        'medium': (300, 300),
        'large': (500, 500),
        'xlarge': (800, 800),
        'original': None,
        }

You can now retrieve your images with::

    >>> print request.route_url('thumbs', size='small',
    ...                         path=['tests', 'image.png')
    'http://localhost/thumbs/small/tests/image.png'

