"""
resource quality
"""
from typing import Optional, Set, Type

from ...core.constants import QualityId


def filter_avail_quality_id(
    quality_class: Type[QualityId],
    quality_set: Set[int],
    quality_id: Optional[int] = None,
    reverse: bool = False
) -> int:
    """
    filter out the target quality ID
    1. when no declared quality ID, choose one from quality set
       if reverse is True, prefer the greatest one on order which represents the highest quality
       else the least one
    2. when given quality ID doesn't match anyone in quality set
       find the nearest one which lesser first, then greater one
    3. when given quality ID exists in quality set, return it
    """
    if len(quality_set) <= 0:
        raise ValueError('No alternative quality IDs')

    if quality_id is not None:
        try:
            _ = quality_class.from_value(quality_id)
        except ValueError:
            quality_id = None

    quality_ids = [
        quality_class.from_value(_quality_id)
        for _quality_id in quality_set
    ]

    if quality_id is None:
        avail_quality_items = sorted(
            quality_ids,
            key=lambda _q_item: _q_item.quality_order,
            reverse=reverse
        )
        quality_item, *_ = avail_quality_items
        return quality_item.quality_id

    if quality_id not in quality_set:
        greater: Optional[QualityId] = None
        lesser: Optional[QualityId] = None
        quality_id_obj = quality_class.from_value(quality_id)
        for item in quality_ids:
            if item > quality_id_obj:
                greater = item if greater is None or greater > item else greater
            else:
                lesser = item if lesser is None or lesser < item else lesser
        if lesser is not None:
            quality_id_obj = lesser
        elif greater is not None:
            quality_id_obj = greater
        return quality_id_obj.quality_id

    return quality_id
