# -*- coding: utf-8 -*-
import os
from hashlib import sha1
import stat
from wsgithumb.utils import get_file_response

try:
    from pyramid.httpexceptions import HTTPNotFound
except ImportError:
    from webob.exc import HTTPNotFound  # NOQA

try:
    import PIL.Image as Image
except ImportError:
    import Image  # NOQA

DEFAULT_SIZES = {
    'icon': (16, 16),
    'small': (50, 50),
    'thumb': (100, 100),
    'medium': (300, 300),
    'large': (500, 500),
    'xlarge': (800, 800),
    'original': None,
    }


def resize(src, dst, size, mode='r'):
    """resize an image to size"""
    image = Image.open(src, mode)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(dst)
    return dst


def get_image_response(document_root=None, cache_directory=None,
                       size=(500, 500), path=None, accel_header=None):
    """helper the get an image response"""

    dummy, ext = os.path.splitext(path)

    # make sure we got an image
    if ext.lower() not in ('.png', '.jpg', '.jpeg', '.gif'):
        return HTTPNotFound()

    filename = os.path.join(document_root, path)
    if not os.path.isfile(filename):
        return HTTPNotFound()

    if size is None:
        # get original
        return get_file_response(filename, accel_header=accel_header,
                                           document_root=document_root)

    # generate cached direname
    h = sha1('%s-%s' % (path, size)).hexdigest()
    d1, d2, d3 = h[0:3], h[3:6], h[:6]

    cached = os.path.join(cache_directory, d1, d2, d3)
    if not os.path.isdir(cached):
        os.makedirs(cached)

    cached = os.path.join(cached, os.path.basename(filename))

    if os.path.isfile(cached):
        last_modified = os.stat(filename)[stat.ST_MTIME]
        last_cached = os.stat(cached)[stat.ST_MTIME]
        if last_modified > last_cached:
            os.remove(cached)

    # generate cached thumb if not yet done
    if not os.path.isfile(cached):
        resize(filename, cached, size)

    return get_file_response(cached, accel_header=accel_header,
                                       document_root=cache_directory)


def add_thumb_view(config, route_name, sizes=DEFAULT_SIZES,
                   document_root=None, cache_directory=None, **view_args):
    """add a view to serve thumbnails in pyramid"""
    settings = config.registry.settings

    if not document_root:
        document_root = settings['thumbs.document_root']
    document_root = os.path.abspath(document_root)

    if not cache_directory:
        cache_directory = settings['thumbs.cache_directory']
    cache_directory = os.path.abspath(cache_directory)

    if not os.path.isdir(cache_directory):
        os.makedirs(cache_directory)

    accel_header = settings.get('thumbs.accel_header', None)

    def view(request):
        size = sizes[request.matchdict['size']]
        path = request.matchdict['path']
        path = '/'.join(path)
        return get_image_response(
            document_root=document_root,
            cache_directory=cache_directory,
            size=size, path=path, accel_header=accel_header
        )

    config.add_route(route_name, '/%s/{size}/*path' % route_name)
    config.add_view(view, route_name=route_name, **view_args)


def includeme(config):
    """pyramid include. declare the add_thumb_view"""
    config.add_directive('add_thumb_view', add_thumb_view)


def make_app(global_conf, **settings):
    """paste.deploy factory"""
    document_root = settings['document_root']
    document_root = os.path.abspath(document_root)

    cache_directory = settings['cache_directory']
    cache_directory = os.path.abspath(cache_directory)

    if not os.path.isdir(cache_directory):
        os.makedirs(cache_directory)

    accel_header = settings.get('accel_header', None)

    def application(environ, start_response):
        path_info = environ['PATH_INFO'].strip('/')
        size, path = path_info.split('/', 1)
        path = '/'.join(path)
        return get_image_response(
            document_root=document_root,
            cache_directory=cache_directory,
            size=size, path=path, accel_header=accel_header
        )

    return application
