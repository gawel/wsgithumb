# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from wsgithumb import get_file_response
from wsgithumb import make_file_app
from wsgithumb import make_thumb_app
from pyramid import testing
from webtest import TestApp
from glob import glob
import unittest
import tempfile
import shutil
import os


class TestAccel(unittest.TestCase):

    def test_nginx(self):
        filename = os.path.abspath(__file__).replace('.pyc', '.py')
        document_root = filename.split('tests')[0]
        resp = get_file_response(filename,
                                 accel_header='x-Accel-Redirect',
                                 document_root=document_root)
        self.assertIn('X-Accel-Redirect',  resp.headers)
        self.assertEqual(resp.headers['X-Accel-Redirect'],
                         '/tests/test_wsgithumb.py')

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
    try:
        resp.body = url
    except TypeError:
        resp.body = url.encode('utf8')
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
        config.add_file_view('files', document_root=document_root)
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

    def test_file(self):
        resp = self.app.get('/files/tests/test_wsgithumb.py')
        self.assertEqual(resp.status_int, 200)

    def test_not_found(self):
        self.app.get('/files/none.txt', status=404)

        self.app.get('/thumbs/small/tests/imag.jpg', status=404)

        self.app.get('/thumbs/small/tests/file.pdf', status=404)

    def test_route_url(self):
        resp = self.app.get('/route_url?path=tests&path=image.png')
        self.assertEqual(resp.body,
                         b'http://localhost/thumbs/small/tests/image.png')


class TestThumbWithFactor(unittest.TestCase):

    def setUp(self):
        self.wd = wd = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, wd)

        filename = os.path.abspath(__file__)
        document_root = filename.split('tests')[0]
        config = testing.setUp()
        config.include("wsgithumb")
        config.add_thumb_view('thumbs',
                              sizes=dict(small=(100, 100), original=None),
                              factors=(100, 75),
                              document_root=document_root,
                              cache_directory=wd)
        config.add_file_view('files', document_root=document_root)
        config.add_route('route_url', '/route_url')
        config.add_view(route_url, route_name='route_url')
        self.app = TestApp(config.make_wsgi_app())

    def test_thumb(self):
        original = self.app.get('/thumbs/original/100/tests/image.jpg')
        self.assertEqual(original.status_int, 200)

        thumb = self.app.get('/thumbs/small/75/tests/image.jpg')
        self.assertEqual(thumb.status_int, 200)

        self.assertTrue(original.content_length > thumb.content_length)

        thumb2 = self.app.get('/thumbs/small/75/tests/image.jpg')
        self.assertEqual(thumb.last_modified, thumb2.last_modified)

        files = glob(os.path.join(self.wd, '*', '*', '*', '*.jpg'))
        self.assertEqual(len(files), 1, files)

    def test_404(self):
        thumb = self.app.get('/thumbs/small/70/tests/image.jpg', status='*')
        self.assertEqual(thumb.status_int, 404)


class TestFile(unittest.TestCase):

    def setUp(self):
        filename = os.path.abspath(__file__)
        document_root = filename.split('tests')[0]
        self.app = TestApp(make_file_app({}, document_root=document_root))

    def test_file(self):
        self.app.get('/tests/tests.pic', status=404)

        resp = self.app.get('/tests/test_wsgithumb.py')
        self.assertEqual(resp.status_int, 200)


class TestImage(unittest.TestCase):

    def setUp(self):
        self.wd = wd = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, wd)
        filename = os.path.abspath(__file__)
        document_root = filename.split('tests')[0]
        self.app = TestApp(make_thumb_app({},
                           cache_directory=wd,
                           document_root=document_root))

    def test_image(self):
        resp = self.app.get('/small/tests/image.jpg')
        self.assertEqual(resp.status_int, 200)

    def test_invalid_path(self):
        self.app.get('/small/', status=404)
        self.app.get('/small/tests', status=404)
        self.app.get('/ssmall/tests/image.jpg', status=404)


class TestImageAccel(unittest.TestCase):

    def setUp(self):
        self.wd = wd = tempfile.mkdtemp()
        self.dirname = os.path.basename(wd)
        self.addCleanup(shutil.rmtree, wd)
        filename = os.path.abspath(__file__)
        document_root = filename.split('tests')[0]
        self.app = TestApp(make_thumb_app({},
                           cache_directory=wd,
                           document_root=document_root,
                           accel_header='x-accel-redirect'))

    def test_thumb(self):
        resp = self.app.get('/small/tests/image.jpg')
        self.assertEqual(resp.status_int, 200)
        self.assertIn('X-Accel-Redirect',  resp.headers)
        self.assertTrue(resp.headers['X-Accel-Redirect'].startswith(
                        '/' + self.dirname))
        self.assertTrue(resp.headers['X-Accel-Redirect'].endswith(
                        '/image.jpg'), resp)

    def test_original(self):
        resp = self.app.get('/original/tests/image.jpg')
        self.assertEqual(resp.status_int, 200)
        self.assertIn('X-Accel-Redirect',  resp.headers)
        self.assertEqual(resp.headers['X-Accel-Redirect'],
                         '/wsgithumb/tests/image.jpg')
