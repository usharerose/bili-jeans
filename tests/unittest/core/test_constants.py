import pytest

from bili_jeans.core.constants import QualityNumber


def test_quality_number_is_login_required():
    assert QualityNumber.P720.is_login_required is True


def test_quality_number_not_login_required():
    assert QualityNumber.P360.is_login_required is False


def test_quality_number_is_vip_required():
    assert QualityNumber.P1080_60.is_vip_required is True


def test_quality_number_not_vip_required():
    assert QualityNumber.P360.is_vip_required is False


def test_quality_number_from_value():
    assert QualityNumber.from_value(127) == QualityNumber.EIGHT_K


def test_quality_number_from_invalid_value():
    with pytest.raises(
        ValueError,
        match='Invalid given quality number : 0'
    ):
        QualityNumber.from_value(0)
