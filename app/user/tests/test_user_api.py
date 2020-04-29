from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test the users api (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating an user with a valid payload is successful"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpassword',
            'name': 'test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpassword',
            'name': 'Test'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password is longer than 8 characters"""
        payload = {
            'email': 'test@test.com',
            'password': 'test',
            'name': 'Test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test that a token is created for user"""
        payload = {
            'email': 'test@test.com',
            'password': 'test',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invaild_credentials(self):
        """Test token is not created if invalid credentials are given"""
        create_user(email='test@test.com', password='test')
        payload = {
            'email': 'test@test.com',
            'password': 'wrong',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test no token is created if user does not exist"""
        payload = {
            'email': 'test@test.com',
            'password': 'test',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_password_field(self):
        """Test that no token is created if there is no password"""
        res = self.client.post(
            TOKEN_URL, {'email': 'test@test.com', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_email_field(self):
        """Test that no token is created if there is no email"""
        res = self.client.post(
            TOKEN_URL, {'email': '', 'password': 'test'})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
