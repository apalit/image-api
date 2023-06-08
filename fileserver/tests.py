from unittest import mock

from django.urls import reverse
from override_storage import override_storage
from override_storage.storage import LocMemStorage

from api.tests.utils import create_expiring_link, create_image


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_retrieve_image(mock_task, db, auto_login_user, create_plan):
    client, user = auto_login_user()
    # create plan
    create_plan(user, thumbnail_heights=[200], include_original_image=True)
    # create an image for the user
    image_upload = create_image(user)
    # get image details
    response = client.get(reverse('image-detail', kwargs={'pk': image_upload.pk}))
    assert response.status_code == 200
    data = response.json()
    # get image
    response = client.get(data['image_url'])
    assert response.status_code == 200
    # attempt to access with anonymous access
    user.logout()
    response = client.get(data['image_url'])
    assert response.status_code == 404


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_retrieve_expiry_link(mock_task, db, auto_login_user, create_plan):
    client, user = auto_login_user()
    # create plan
    create_plan(
        user, thumbnail_heights=[200], include_original_image=True, expiring_link=True
    )
    image_upload = create_image(user)
    expiring_link = create_expiring_link(image_upload)
    response = client.get(
        reverse('expiring-link-detail', kwargs={'pk': expiring_link.pk})
    )
    assert response.status_code == 200
    # retrieve as anonymous user
    user.logout()
    image_response = client.get(response.json()['link_url'])
    assert image_response.status_code == 200
