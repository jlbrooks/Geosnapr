from django.test import TestCase
from geosnapr.models import Profile, Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

class ProfileCreateTestCase(TestCase):

    def setUp(self):
        User.objects.create(username='foobar', first_name='foo', last_name='bar', 
            email='foo@bar.com', password='password')

    # Create failures

    def test_create_no_username(self):
        p,err = Profile.create(username='', email='test@example.com', password='test', 
            first_name='jacob', last_name='brooks')

        self.assertEqual(p, None)

    def test_create_no_first_name(self):
        p,err = Profile.create(username='jlbrooks', email='test@example.com', password='test', 
            first_name='', last_name='brooks')

        self.assertEqual(p, None)

    def test_create_no_last_name(self):
        p,err = Profile.create(username='jlbrooks', email='test@example.com', password='test', 
            first_name='jacob', last_name='')

        self.assertEqual(p, None)

    def test_create_no_password(self):
        p,err = Profile.create(username='jlbrooks', email='test@example.com', password='', 
            first_name='jacob', last_name='brooks')

        self.assertEqual(p, None)

    def test_create_no_email(self):
        p,err = Profile.create(username='jlbrooks', email='', password='test', 
            first_name='jacob', last_name='brooks')

        self.assertEqual(p, None)

    def test_create_username_exists(self):
        p,err = Profile.create(username='foobar', email='test@example.com', password='test', 
            first_name='jacob', last_name='brooks')

        self.assertEqual(p, None)

    def test_create_email_exists(self):
        p,err = Profile.create(username='jlbrooks', email='foo@bar.com', password='test', 
            first_name='jacob', last_name='brooks')

        self.assertEqual(p, None)

    # Create success

    def test_create_profile(self):
        p,err = Profile.create(username='jlbrooks', email='test@example.com', password='test', 
            first_name='jacob', last_name='brooks')

        self.assertEqual(err, None)
        self.assertEqual(p.user.username, 'jlbrooks')
        self.assertEqual(p.user.first_name, 'jacob')
        self.assertEqual(p.user.last_name, 'brooks')
        self.assertEqual(p.user.email, 'test@example.com')

class ImageCreateTestCase(TestCase):

    def setUp(self):
        p,err = Profile.create(username='jlbrooks', email='test@example.com', password='test', 
            first_name='jacob', last_name='brooks')


        self.file_mock = SimpleUploadedFile('best_file_eva.txt', bytes('these are the file contents!', 'utf-8'))

    # Create failures

    def test_create_no_username(self):
        i,err = Image.create(username='', image=self.file_mock, lat=15.0, lng=10.0, caption='hey')

        self.assertEqual(i, None)

    def test_create_username_no_exist(self):
        i,err = Image.create(username='foobar', image=self.file_mock, lat=15.0, lng=10.0, caption='hey')

        self.assertEqual(i, None)

    def test_create_no_file(self):
        i,err = Image.create(username='jlbrooks', image=None, lat=15.0, lng=10.0, caption='hey')

        self.assertEqual(i, None)

    def test_create_no_lat(self):
        i,err = Image.create(username='jlbrooks', image=self.file_mock, lat=None, lng=10.0, caption='hey')

        self.assertEqual(i, None)

    def test_create_no_lng(self):
        i,err = Image.create(username='jlbrooks', image=self.file_mock, lat=10.0, lng=None, caption='hey')

        self.assertEqual(i, None)

    def test_create_no_lng(self):
        i,err = Image.create(username='jlbrooks', image=self.file_mock, lat=10.0, lng=None, caption='hey')

        self.assertEqual(i, None)

    # Don't test success until I find a way to mock file saving...
    # def test_create_full(self):
    #     i,err = Image.create(username='jlbrooks', image=self.file_mock, lat=10.0, lng=15.0, caption='hey')

    #     self.assertEqual(err, None)
    #     self.assertEqual(i.user.username, 'jlbrooks')
    #     self.assertEqual(i.lat, 10.0)
    #     self.assertEqual(i.lng, 15.0)
    #     self.assertEqual(i.caption, 'hey')

    # def test_create_no_caption(self):
    #     i,err = Image.create(username='jlbrooks', image=self.file_mock, lat=10.0, lng=15.0, caption=None)

    #     self.assertEqual(err, None)
    #     self.assertEqual(i.user.username, 'jlbrooks')
    #     self.assertEqual(i.lat, 10.0)
    #     self.assertEqual(i.lng, 15.0)
    #     self.assertEqual(i.caption, '')