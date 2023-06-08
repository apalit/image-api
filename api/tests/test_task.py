import pytest
from api.tests.utils import create_image
from override_storage.storage import LocMemStorage
from override_storage import override_storage
from django.test.utils import override_settings


# needs fixing
@pytest.mark.skip
@override_storage(storage=LocMemStorage())
@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
def test_create_thumbnail(db, auto_login_user, create_plan):
    from api.models import ImageUpload
    client, user = auto_login_user()
    # create plan
    create_plan(user, thumbnail_heights=[100], include_original_image=True)
    # create an image for the user
    image_upload = create_image(user)
    updated_image = ImageUpload.objects.get(pk=image_upload.pk)
    assert updated_image.thumbnails.count() == 1
