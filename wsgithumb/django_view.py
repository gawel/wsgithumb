"""
Use wsgithumb in your Django application.
"""
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from wsgithumb import get_image_response

def serve(request, size, path):
    """
    Use an url like :
    url(r'^thumbs/(?P<size>[^/]*)/(?P<path>.*)$', django_view.serve)
    """
    if not settings.IMAGE_SIZE.has_key(size):
        return HttpResponseBadRequest()
    size = settings.IMAGE_SIZE[size]
    accel_header = getattr(settings, 'ACCEL_HEADER', False)
    thumb = get_image_response(
        document_root = settings.UPLOAD_ROOT,
        cache_directory = '/tmp',
        size = size,
        path = path,
        accel_header = accel_header
    )
    if hasattr(thumb, 'content_type'): #FIXME need a neutral class
        response = HttpResponse(thumb.app_iter, mimetype = thumb.content_type)
        for key, value in thumb.headers.iteritems():
            response[key] = value
    else:
        response = HttpResponseNotFound()
    return response
