from django.test import TestCase
from django.conf import settings
from geosnapr.models import Profile, Image, Album
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
        # See if we created an album
        a = Album.objects.filter(user=p.user)
        self.assertNotEqual(a, None)
        self.assertEqual(a[0].name, "All Images")

class ProfileUpdateTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(username='foobar', first_name='foo', last_name='bar', 
            email='foo@bar.com', password='password')
        Profile.objects.create(user=user)
        self.old_pass_hash = user.password

        other_user = User.objects.create(username='test', first_name='test', last_name='testy', 
            email='test@test.com', password='password')
        Profile.objects.create(user=other_user)

    # Update failures

    def test_update_no_username(self):
        p,err = Profile.update(username='', first_name='foo', last_name='bar', 
            email='foo@bar.com', password='password')

        self.assertEqual(p, None)

    def test_update_username_doesnt_exist(self):
        p,err = Profile.update(username='jlbrooks', first_name='foo', last_name='bar', 
            email='foo@bar.com', password='password')

        self.assertEqual(p, None)

    def test_update_no_first_name(self):
        p,err = Profile.update(username='foobar', first_name='', last_name='bar', 
            email='foo@bar.com', password='password')

        self.assertEqual(p.user.first_name, 'foo')

    def test_update_no_last_name(self):
        p,err = Profile.update(username='foobar', first_name='foo', last_name='', 
            email='foo@bar.com', password='password')

        self.assertEqual(p.user.last_name, 'bar')

    def test_update_no_password(self):
        p,err = Profile.update(username='foobar', first_name='foo', last_name='bar', 
            email='foo@bar.com', password='')

        self.assertEqual(p.user.password, self.old_pass_hash)

    def test_update_no_email(self):
        p,err = Profile.update(username='foobar', first_name='foo', last_name='bar', 
            email='', password='password')

        self.assertEqual(p.user.email, 'foo@bar.com')

    def test_update_email_exists(self):
        p,err = Profile.update(username='foobar', first_name='foo', last_name='bar', 
            email='test@test.com', password='password')

        self.assertEqual(p, None)

    # Update success

    def test_update_no_change(self):
        p,err = Profile.update(username='foobar', first_name='foo', last_name='bar', 
            email='foo@bar.com', password='password')

        self.assertEqual(err, None)
        self.assertEqual(p.user.username, 'foobar')
        self.assertEqual(p.user.first_name, 'foo')
        self.assertEqual(p.user.last_name, 'bar')
        self.assertEqual(p.user.email, 'foo@bar.com')

    def test_update_change(self):
        p,err = Profile.update(username='foobar', first_name='jacob', last_name='brooks', 
            email='jacobbro@andrew.cmu.edu', password='other')

        self.assertEqual(err, None)
        self.assertEqual(p.user.username, 'foobar')
        self.assertEqual(p.user.first_name, 'jacob')
        self.assertEqual(p.user.last_name, 'brooks')
        self.assertEqual(p.user.email, 'jacobbro@andrew.cmu.edu')
        self.assertNotEqual(p.user.password, self.old_pass_hash)

class ProfileAPITestCase(TestCase):

    def setUp(self):
        p,err = Profile.create(username='jlbrooks', email='test@example.com', password='test', 
            first_name='jacob', last_name='brooks')
        self.p = p

    def test_create_new_key(self):
        uuid = self.p.get_or_create_api_key()

        self.assertNotEqual(uuid, '')

    def test_get_key_same(self):
        uuid = self.p.get_or_create_api_key()
        uuid_2 = self.p.get_or_create_api_key()

        self.assertEqual(uuid, uuid_2)


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

    def test_create_bad_lat(self):
        i,err = Image.create(username='jlbrooks', image=self.file_mock, lat="foo", lng=15.0, caption='hey')

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

class AlbumCreateTestCase(TestCase):

    def setUp(self):
        p,err = Profile.create(username='jlbrooks', email='test@example.com', password='test', 
            first_name='jacob', last_name='brooks')

    def test_create_no_name(self):
        a,err = Album.create(username='jlbrooks', name='')

        self.assertEqual(err,None)
        self.assertEqual(a.name, 'Untitled Album')
        self.assertEqual(a.user.username, 'jlbrooks')

    def test_create_no_user(self):
        a,err = Album.create(username='foobar', name='test')

        self.assertEqual(a, None)

    def test_create_with_name(self):
        a,err = Album.create(username='jlbrooks', name='my album!')

        self.assertEqual(a.name, 'my album!')

class AlbumDefaultTestCase(TestCase):

    def setUp(self):
        # Create a user without a default album
        self.user = User.objects.create(username='foobar', first_name='foo', last_name='bar', 
            email='foo@bar.com', password='password')
        self.user.save()

    def test_get_bad_user(self):
        a = Album.get_or_create_default_for_user(username='jlbrooks')

        self.assertEqual(a, None)

    def test_get_no_album(self):
        a = Album.get_or_create_default_for_user(username='foobar')

        self.assertEqual(a.name, settings.DEFAULT_ALBUM_NAME)
        self.assertEqual(a.user, self.user)

    def test_get_album_exists(self):
        a = Album.get_or_create_default_for_user(username='foobar')

        self.assertEqual(a.name, settings.DEFAULT_ALBUM_NAME)
        self.assertEqual(a.user, self.user)

        # Try to create again
        other_a = Album.get_or_create_default_for_user(username='foobar')

        self.assertEqual(other_a, a)