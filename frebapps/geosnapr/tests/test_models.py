from django.test import TestCase
from geosnapr.models import Profile
from django.contrib.auth.models import User


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

    # Create success

    def test_create_profile(self):
        p,err = Profile.create(username='jlbrooks', email='test@example.com', password='test', 
            first_name='jacob', last_name='brooks')

        self.assertEqual(err, None)
        self.assertEqual(p.user.username, 'jlbrooks')
        self.assertEqual(p.user.first_name, 'jacob')
        self.assertEqual(p.user.last_name, 'brooks')
        self.assertEqual(p.user.password, 'test')
        self.assertEqual(p.user.email, 'test@example.com')