"""
Use wsgithumb in your Django application.
"""
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from wsgithumb import get_image_response
from wsgithumb import DEFAULT_SIZES
import tempfile
import os


IMAGE_SIZES = getattr(settings, 'IMAGE_SIZES', DEFAULT_SIZES)
CACHE_DIRECTORY = getattr(settings, 'CACHE_DIRECTORY', None)
ACCEL_HEADER = getattr(settings, 'ACCEL_HEADER', False)

if not CACHE_DIRECTORY:
    CACHE_DIRECTORY = os.path.join(tempfile.gettempdir(), 'wsgithumb-cache')


def serve(request, size, path, factor=100,
          document_root=None, cache_directory=None):
    """Use an url like::

        url(r'^thumbs/(?P<size>[^/]*)/(?P<path>.*)$', django_view.serve)
        url(r'^thumbs/(?P<size>[^/]*)/(?P<factor>[^/]*)/(?P<path>.*)$',
            django_view.serve)
    """
    cache_directory = cache_directory or CACHE_DIRECTORY
    if not os.path.isdir(cache_directory):
        os.makedirs(cache_directory)

    if not os.path.isdir(document_root):
        raise OSError('No such directory %s' % document_root)

    if size not in IMAGE_SIZES:
        return HttpResponseBadRequest()

    size = IMAGE_SIZES[size]
    thumb = get_image_response(
        document_root=document_root,
        cache_directory=cache_directory,
        size=size,
        factor=factor,
        path=path,
        accel_header=ACCEL_HEADER,
    )
    if thumb.status_int > 400:
        response = HttpResponse(status=thumb.status_int)
    else:
        response = HttpResponse(thumb.app_iter,
                                status=thumb.status_int,
                                content_type=thumb.content_type)
        for key, value in thumb.headers.iteritems():
            response[key] = value
    return response
