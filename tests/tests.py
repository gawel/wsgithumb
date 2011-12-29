# -*- coding: utf-8 -*-
from wsgithumb import get_file_response
from pyramid import testing
from webtest import TestApp
import unittest2 as unittest
from glob import glob
import tempfile
import shutil
import os


class TestAccel(unittest.TestCase):

    def test_nginx(self):
        filename = os.path.abspath(__file__).replace('.pyc', '.py')
        document_root = filename.split('tests')[0]
        resp = get_file_response(filename,
                                 accel_header='x-Accel-Redirect:/accel/',
                                 document_root=document_root)
        self.assertIn('X-Accel-Redirect',  resp.headers)
        self.assertEqual(resp.headers['X-Accel-Redirect'],
                        '/accel/tests/tests.py')

    def test_apache(self):
        filename = os.path.abspath(__file__)
        document_root = filename.split('tests')[0]
        resp = get_file_response(filename,
                                 accel_header='x-Sendfile',
                                 document_root=document_root)
        self.assertIn('X-Sendfile',  resp.headers)
        self.assertEqual(resp.headers['X-Sendfile'], filename)


def route_url(request):
    url = request.route_url('thumbs', size='small',
                             path=request.GET.getall('path'))
    resp = request.response
    resp.body = url
    return resp


class TestThumb(unittest.TestCase):

    def setUp(self):
        self.wd = wd = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, wd)

        filename = os.path.abspath(__file__)
        document_root = filename.split('tests')[0]
        config = testing.setUp()
        config.include("wsgithumb")
        config.add_thumb_view('thumbs',
                       sizes=dict(small=(100, 100), original=None),
                       document_root=document_root,
                       cache_directory=wd)
        config.add_route('route_url', '/route_url')
        config.add_view(route_url, route_name='route_url')
        self.app = TestApp(config.make_wsgi_app())

    def test_thumb(self):
        original = self.app.get('/thumbs/original/tests/image.jpg')
        self.assertEqual(original.status_int, 200)

        thumb = self.app.get('/thumbs/small/tests/image.jpg')
        self.assertEqual(thumb.status_int, 200)

        self.assertTrue(original.content_length > thumb.content_length)

        thumb2 = self.app.get('/thumbs/small/tests/image.jpg')
        self.assertEqual(thumb.last_modified, thumb2.last_modified)

        files = glob(os.path.join(self.wd, '*', '*', '*', '*.jpg'))
        self.assertEqual(len(files), 1, files)

    def test_not_found(self):
        self.app.get('/thumbs/small/tests/imag.jpg', status=404)

        self.app.get('/thumbs/small/tests/file.pdf', status=404)

    def test_route_url(self):
        resp = self.app.get('/route_url?path=tests&path=image.png')
        self.assertEqual(resp.body,
                         'http://localhost/thumbs/small/tests/image.png')
