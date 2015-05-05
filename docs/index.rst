.. wsgithumb documentation master file, created by
   sphinx-quickstart on Thu Dec 29 15:13:50 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to wsgithumb's documentation!
=====================================

Installation
-------------

Use easy_install or pip::

    $ pip install Pillow wsgithumb

About X-Sendfile
-----------------

Moderns web servers like NGinx or Apache implement the ``X-Sendfile`` feature.
This allow your application to only return the file path in a response header
then the web server will use this path to serve the file without blocking your
application.

**wsgithumb** allow you to use this feature. Just use the accel_header parameter.

For NGinx, set ``accel_header="x-accel-redirect"``

For Apache, set ``accel_header="x-sendfile"``

Here is an example with a thumb::

    >>> from wsgithumb import get_image_response
    >>> from tests import document_root
    >>> resp = get_image_response(document_root=document_root,
    ...                           cache_directory='/tmp/www/cache',
    ...                           size=(500, 500), path='tests/image.jpg',
    ...                           accel_header='x-accel-redirect')
    >>> print(resp)
    200 OK
    Content-Type: image/jpeg
    Last-Modified: ... GMT
    ETag: "..."
    X-Accel-Redirect: /cache/.../image.jpg

So you just need to add this to your nginx configuration::

    location /cache/ {
      internal;
      root   /tmp/www;
    }

So nginx can serve ``/tmp/www/cache/.../image.jpg``

WSGI Applications
------------------

**wsgithumb** provide 2 entry points for PasteDeploy:

.. sourcecode:: ini

    [app:thumbs]
    use = wsgithumb#thumbs
    document_root = /var/www/images
    cache_directory = /var/www/thumbs
    # for production
    #accel_header = x-accel-redirect

    [app:files]
    use = wsgithumb#files
    document_root = /var/www/files
    # for production
    #accel_header = x-accel-redirect

See :func:`~wsgithumb.make_thumb_app` and :func:`~wsgithumb.make_file_app` for
available options.

You'll need the following NGinx configuration in production mode::

    location /images/ {
        internal;
        root /var/www;
    }
    location /thumbs/ {
        internal;
        root /var/www;
    }
    location /files/ {
        internal;
        root /var/www;
    }


Using wsgithumb in Pyramid
--------------------------

There is an helper in **wsgithumb** to help you to serve thumnails in your application.

Add this to your ``.ini`` file:

.. sourcecode:: ini

    [app:main]
    use = egg:MyApp

    # wsgithumb config
    thumbs.document_root = %(here)s/www/images
    thumbs.cache_directory = %(here)s/www/cache
    # if you want to use the accel_header when in production
    #thumbs.accel_header = x-accel-redirect

..
    >>> from pyramid import testing
    >>> config = testing.setUp()
    >>> config.registry.settings.update({
    ...   'thumbs.document_root': '/tmp/www/images',
    ...   'thumbs.cache_directory': '/tmp/www/cache',
    ... })

Add a :func:`~wsgithumb.add_thumb_view` to your ``__init__.py``::

    >>> sizes = {
    ...     'thumb': (100, 100),
    ...     'large': (500, 500),
    ...     'original': None,
    ...     }
    >>> config.include('wsgithumb')
    >>> config.add_thumb_view('thumbs', sizes=sizes)

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

    >>> print(request.route_url('thumbs', size='small',
    ...                         path='tests/image.png']
    ...                        )) #doctest: +SKIP
    'http://localhost/thumbs/small/tests/image.png'


API
===

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

..
    >>> import shutil
    >>> shutil.rmtree('/tmp/www')
