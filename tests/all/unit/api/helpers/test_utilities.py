import datetime
import re
import string

import pytest

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.utilities import (
    dasherize,
    dict_to_snake_case,
    get_filename_from_cd,
    monthdelta,
    represents_int,
    require_relationship,
    str_generator,
    string_empty,
)


def test_get_filename_from_cd():
    """Test the method get_filename_from_cd"""

    test_data_first = 'attachment; filename="image.png"'
    test_data_none = None
    expected_response_first = ('"image', '.png"')
    expected_response_none = ('', '')

    response_first = get_filename_from_cd(test_data_first)
    response_none = get_filename_from_cd(test_data_none)

    assert expected_response_first == response_first
    assert expected_response_none == response_none


def test_dasherize():
    """Method to test whether an attribute dasherizes or not"""

    field = "starts_at"
    dasherized_field = "starts-at"
    result = dasherize(field)
    assert result == dasherized_field


def test_represents_int():
    """Method to test representation of int"""

    assert represents_int(4) is True
    assert represents_int('test') is False


def test_string_empty():
    """Method to test whether an empty string is correctly identified."""

    assert string_empty('') is True
    assert string_empty(' ') is True
    assert string_empty('\t') is True
    assert string_empty('\n') is True
    assert string_empty(None) is False
    assert string_empty('some value') is False
    assert string_empty('  some   value ') is False
    assert string_empty(0) is False
    assert string_empty([]) is False
    assert string_empty(False) is False


def test_str_generator():
    """Method to test str_generator."""

    generated_string = str_generator()
    assert len(generated_string) == 6
    assert re.match(r'^[A-Z0-9]+$', generated_string) is not None
    assert re.match(r'^[a-z]+$', generated_string) is None

    generated_string = str_generator(8, chars=string.ascii_lowercase)
    assert len(generated_string) == 8
    assert re.match(r'^[A-Z0-9]+$', generated_string) is None
    assert re.match(r'^[a-z]+$', generated_string) is not None

    generated_string = str_generator(chars='ABC253')
    assert re.match(r'^[ABC253]+$', generated_string) is not None


def test_require_relationship():
    """Method to test relationship in request data"""

    with pytest.raises(UnprocessableEntityError):
        data = ['event']
        require_relationship(['sponsor', 'event'], data)


def test_monthdelta():
    """Method to test difference in months result"""

    test_date = datetime.datetime(2000, 6, 18)
    test_future_date = monthdelta(test_date, 3)
    assert test_future_date == datetime.datetime(2000, 9, 18)

    test_date = datetime.datetime(2000, 1, 1)
    test_past_date = monthdelta(test_date, -1)
    assert test_past_date == datetime.datetime(1999, 12, 1)

    test_date = datetime.datetime(2000, 3, 1)
    test_past_date = monthdelta(test_date, -1)
    assert test_past_date == datetime.datetime(2000, 2, 1)


def test_dict_to_snake_case():
    assert dict_to_snake_case(None) is None
    assert dict_to_snake_case({}) == {}
    assert dict_to_snake_case({'name': 'Areeb', 'age': 432}) == {
        'name': 'Areeb',
        'age': 432,
    }
    assert dict_to_snake_case({'is_admin': True, 'full_name': 'Areeb Jamal'}) == {
        'is_admin': True,
        'full_name': 'Areeb Jamal',
    }

    expected = {'is_admin': True, 'full_name': 'Areeb Jamal', 'age': 432}
    assert (
        dict_to_snake_case({'is-admin': True, 'full-name': 'Areeb Jamal', 'age': 432})
        == expected
    )
    assert (
        dict_to_snake_case({'isAdmin': True, 'fullName': 'Areeb Jamal', 'age': 432})
        == expected
    )

    assert dict_to_snake_case(
        {
            'name': 'Areeb',
            'isSuperAdmin': True,
            'job-title': 'Software Engineer',
            'field_level': 'Super',
        }
    ) == {
        'name': 'Areeb',
        'is_super_admin': True,
        'job_title': 'Software Engineer',
        'field_level': 'Super',
    }

    assert dict_to_snake_case(
        {'is-superAdmin': True, 'isMega_level-event': True, 'isSuper_admin': False}
    ) == {'is_super_admin': False, 'is_mega_level_event': True}
