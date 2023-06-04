from django.urls import reverse
import pytest


def test_list_image_user_no_plan(db, auto_login_user):
    client, user = auto_login_user()
    response = client.get(reverse('images'))
    data = response.json()
    assert response.status_code == 400
    assert data['userplan'] == 'This functionality needs subscription to a plan'


def test_list_image_no_access_original_image():
    pass


def test_list_image_access_to_original_image():
    pass


def test_list_image_expiring_link():
    pass
