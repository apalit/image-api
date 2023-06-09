from io import BytesIO
from unittest import mock

from django.urls import reverse
from override_storage import override_storage
from override_storage.storage import LocMemStorage
from PIL import Image

from api.tests.utils import create_expiring_link, create_image


def test_list_image_user_no_plan(db, auto_login_user):
    client, user = auto_login_user()
    response = client.get(reverse('image-list'))
    data = response.json()
    assert response.status_code == 403
    assert data['detail'] == 'You need to be subscribed to a plan to use this API'
    client.logout()


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_list_image_no_access_original_image(
    mock_task, db, auto_login_user, create_plan
):
    client, user = auto_login_user()
    # create plan
    create_plan(user, thumbnail_heights=[200])
    # create an image for the user
    create_image(user)

    response = client.get(reverse('image-list'))
    assert response.status_code == 200
    data = response.json()['results']
    assert len(data) == 1
    assert data[0]['image_url'] is None


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_list_image_access_to_original_image(
    mock_task, db, auto_login_user, create_plan
):
    client, user = auto_login_user()
    # create plan
    create_plan(user, thumbnail_heights=[200], include_original_image=True)
    # create an image for the user
    create_image(user)
    response = client.get(reverse('image-list'))
    assert response.status_code == 200
    data = response.json()['results']
    assert len(data) == 1
    assert data[0]['image_url']


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_get_image_detail(mock_task, db, auto_login_user, create_plan):
    client, user = auto_login_user()
    # create plan
    create_plan(user, thumbnail_heights=[50], include_original_image=True)
    # create an image for the user
    image_upload = create_image(user)
    response = client.get(reverse('image-detail', kwargs={'pk': image_upload.pk}))
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'test image'
    assert data['image_url']


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_create_image(mock_task, db, auto_login_user, create_plan):
    client, user = auto_login_user()
    # create plan
    create_plan(user, thumbnail_heights=[50], include_original_image=True)
    # image file
    image_file = BytesIO()
    image = Image.new('RGB', size=(400, 400), color=(155, 0, 0))
    image.save(image_file, 'JPEG')
    image_file.name = 'test1.jpg'
    image_file.seek(0)
    data = {'name': 'Test image upload', 'image': image_file}

    response = client.post(reverse('image-list'), data, format='multipart/format')
    assert response.status_code == 201
    assert response.json()['name'] == 'Test image upload'


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_expiry_link_no_access(mock_task, db, auto_login_user, create_plan):
    client, user = auto_login_user()
    # create plan with no right to expiring links
    create_plan(user, thumbnail_heights=[50], include_original_image=True)
    # create an image for the user
    image_upload = create_image(user)
    # attempt to get expiring links
    response = client.get(reverse('expiring-link-list'))
    assert response.status_code == 403

    # attempt to create an expiring link
    data = {'expiry_in_seconds': 600, 'base_image': image_upload.pk}
    response = client.post(reverse('expiring-link-list'), data)
    assert response.status_code == 403


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_expiry_link_list(mock_task, db, auto_login_user, create_plan):
    client, user = auto_login_user()
    # create plan with rights to expiring links
    create_plan(
        user, thumbnail_heights=[50], include_original_image=True, expiring_link=True
    )
    # create images and expiring links for the user
    for i in range(2):
        image_upload = create_image(user)
        create_expiring_link(image_upload)

    response = client.get(reverse('expiring-link-list'))
    assert response.status_code == 200
    data = response.json()['results']
    assert len(data) == 2

    # filter by image
    image_upload_id = data[0]['base_image']
    response = client.get(
        reverse('expiring-link-list'), {'base_image': image_upload_id}
    )
    assert response.status_code == 200
    data = response.json()['results']
    assert len(data) == 1


@override_storage(storage=LocMemStorage())
@mock.patch('api.tasks.create_thumbnails_task')
def test_expiry_link_create(mock_task, db, auto_login_user, create_plan):
    client, user = auto_login_user()
    # create plan with rights to expiring links
    create_plan(
        user, thumbnail_heights=[50], include_original_image=True, expiring_link=True
    )
    image_upload = create_image(user)
    data = {
        'description': 'Expiring link test',
        'expiry_in_seconds': 60000,
        'base_image': image_upload.pk,
    }
    # attempt to create with expiration period out of range
    response = client.post(reverse('expiring-link-list'), data)
    assert response.status_code == 400
    assert 'expiry_in_seconds' in response.json()

    # create with valid expiry value
    data['expiry_in_seconds'] = 1000
    response = client.post(reverse('expiring-link-list'), data)
    assert response.status_code == 201

    # retrieve object
    expiring_link_id = response.json()['id']
    response = client.get(
        reverse('expiring-link-detail', kwargs={'pk': expiring_link_id})
    )
    assert response.status_code == 200
