from slots_tracker_server.models import Categories


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
