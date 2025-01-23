import pytest

from bili_jeans.core.constants import (
    FormatNumberValue,
    QualityNumber
)


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


def test_format_number_value_get_dash_full_fnval():
    assert FormatNumberValue.get_dash_full_fnval() == 4048  # 111111010000


def test_format_number_value_get_dash_fnval_for_hdr():
    assert FormatNumberValue.get_dash_fnval(
        QualityNumber.HDR.value,
        False
    ) == 208  # 000011010000


def test_format_number_value_get_dash_fnval_for_dolby_vision_and_audio():
    assert FormatNumberValue.get_dash_fnval(
        QualityNumber.DOLBY.value,
        True
    ) == 912  # 001110010000


def test_format_number_value_get_dash_fnval_for_eight_k():
    assert FormatNumberValue.get_dash_fnval(
        QualityNumber.EIGHT_K.value,
        False
    ) == 1168  # 010010010000
