import pytest
import uuid
from api.models import Plan, UserPlan


@pytest.fixture
def test_password():
    return str(uuid.uuid4())


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
    def make_auto_login(user=None):
        if not user:
            user = create_user()
        client.login(username=user.username, password=test_password)
        return client, user
    return make_auto_login


@pytest.fixture
def create_plan(db, create_user, test_password):
    def make_user_plan(
        user=None,
        thumbnail_heights=[200],
        include_original_image=False,
        expiring_link=False
    ):
        if not user:
            user = create_user()
        plan = Plan(
            name='PlanA',
            thumbnail_heights=thumbnail_heights,
            include_original_image=include_original_image,
            expiring_link=expiring_link
        )
        plan.save()
        user_plan = UserPlan(
            user=user,
            plan=plan
        )
        user_plan.save()
        return plan, user_plan
    return make_user_plan
