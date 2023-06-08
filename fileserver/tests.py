from unittest import mock

from django.urls import reverse
from override_storage import override_storage
from override_storage.storage import LocMemStorage

from api.tests.utils import create_image


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_get_image(mock_task, db, auto_login_user, create_plan):
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
