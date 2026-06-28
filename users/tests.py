"""Tests for users app: registration, login, logout, profile."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from users.models import UserProfile


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="john",
        email="john@example.com",
        password="strongpass123",
    )


# ---------------------------------------------------------------------------
# UserProfile Model Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUserProfile:
    def test_profile_auto_created(self, user):
        """Profile should be created automatically via signal."""
        assert hasattr(user, "profile")
        assert isinstance(user.profile, UserProfile)

    def test_profile_str(self, user):
        assert "john" in str(user.profile)

    def test_profile_fields_blank(self, user):
        """Optional fields start blank."""
        profile = user.profile
        assert profile.bio == ""
        assert profile.phone == ""


# ---------------------------------------------------------------------------
# Registration Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRegistration:
    def test_register_page_loads(self, client):
        response = client.get(reverse("register"))
        assert response.status_code == 200

    def test_register_creates_user(self, client, db):
        response = client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "TestPass!234",
                "password2": "TestPass!234",
            },
        )
        assert response.status_code in (200, 302)
        assert User.objects.filter(username="newuser").exists()

    def test_register_mismatched_passwords(self, client, db):
        response = client.post(
            reverse("register"),
            {
                "username": "failuser",
                "email": "fail@example.com",
                "password1": "TestPass!234",
                "password2": "WrongPass!234",
            },
        )
        # Should stay on register page with form errors
        assert response.status_code == 200
        assert not User.objects.filter(username="failuser").exists()


# ---------------------------------------------------------------------------
# Login / Logout Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAuth:
    def test_login_page_loads(self, client):
        response = client.get(reverse("login"))
        assert response.status_code == 200

    def test_valid_login(self, client, user):
        response = client.post(
            reverse("login"),
            {"username": "john", "password": "strongpass123"},
        )
        assert response.status_code in (200, 302)

    def test_invalid_login(self, client, db):
        response = client.post(
            reverse("login"),
            {"username": "nobody", "password": "wrongpass"},
        )
        assert response.status_code == 200  # stays on login page

    def test_logout(self, client, user):
        client.login(username="john", password="strongpass123")
        response = client.post(reverse("logout"))
        assert response.status_code in (200, 302)


# ---------------------------------------------------------------------------
# Account / Profile Page
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAccountPage:
    def test_account_requires_login(self, client):
        response = client.get(reverse("account"))
        assert response.status_code in (301, 302)
        assert "login" in response.url

    def test_account_accessible_when_logged_in(self, client, user):
        client.login(username="john", password="strongpass123")
        response = client.get(reverse("account"))
        assert response.status_code == 200
