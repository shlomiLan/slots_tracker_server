import pytest

from slots_tracker_server.models import Categories


@pytest.fixture(scope="function", autouse=True)
def categories():
    user_added_categories = Categories(name='user_added_categories - 1').save()
    not_user_added_categories = Categories(name='not_user_added_categories - 1', added_by_user=False).save()
    return dict(user_added_categories=user_added_categories, not_user_added_categories=not_user_added_categories)


def test_field_does_not_exist():
    new_category_name = 'Very random cat name 23432'
    # Verify category doesn't exists yet
    category = Categories.objects(name=new_category_name)
    assert not category

    # Create the new category
    category, is_new = Categories.get_or_create_category_by_business_name(new_category_name)
    assert category
    assert is_new is True

    # Verify we get the "same" category, no new category again
    category2, is_new2 = Categories.get_or_create_category_by_business_name(new_category_name)
    assert category.id == category2.id
    assert is_new2 is False

    category_name_to_ignore = 'colu'
    category, is_new = Categories.get_or_create_category_by_business_name(category_name_to_ignore)
    assert not category
    assert is_new is False

    category_name_with_match = 'eatmeat'
    category, is_new = Categories.get_or_create_category_by_business_name(category_name_with_match)
    assert category
    assert is_new is False


def test_merge_categories(categories):
    assert categories['not_user_added_categories'].merge_categories(categories['user_added_categories'].id)


def test_merge_categories_wrong_type(categories):
    with pytest.raises(Exception):
        assert categories['user_added_categories'].merge_categories(categories['user_added_categories'].id)

    with pytest.raises(Exception):
        assert categories['not_user_added_categories'].merge_categories(categories['not_user_added_categories'].id)
