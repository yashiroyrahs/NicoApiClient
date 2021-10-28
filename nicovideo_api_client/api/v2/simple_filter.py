import re
from datetime import datetime
from typing import Dict, List, Union, Optional

from nicovideo_api_client.api.v2.limit import SnapshotSearchAPIV2Limit
from nicovideo_api_client.constants import (
    FieldType,
    MatchDict,
    RangeDict,
    MatchValue,
    RangeValue
)


class SnapshotSearchAPIV2SimpleFilter:
    def __init__(self, query: Dict[str, str]):
        self._query: Dict[str, str] = query
        self._filters: Dict[str, List[str]] = {}

    def _set_filter(
        self, field_type: FieldType, value: Union[int, str, datetime]
    ) -> str:
        if field_type == FieldType.START_TIME:
            if not isinstance(value, datetime):
                raise TypeError("FieldType.START_TIMEを指定した時の型は datetime であるべきです")
            v = value.strftime("%Y-%m-%dT%H:%M:%S+09:00")
        elif field_type == FieldType.CONTENT_ID:
            if isinstance(value, int):
                v = f"sm{value}"
            elif isinstance(value, str):
                if not re.compile(r"sm\d+").fullmatch(value):
                    raise TypeError("FieldType.CONTENT_IDはsm(数字)の形で表されるべきです")
                v = value
            else:
                raise TypeError("FieldType.CONTENT_IDを指定した時の型は int または str であるべきです")
        else:
            raise NotImplementedError("未知のTypeが指定されました")

        if field_type.value not in self._filters:
            self._filters[field_type.value] = []

        self._filters[field_type.value].append(v)
        return v

    def _match_filter(self, field_type: FieldType, match_value: MatchValue):
        for value in match_value:
            v = self.set_filter(field_type, value)

            self._query[
                f"filters[{field_type.value}][{len(self._filters[field_type.value]) - 1}]"
            ] = v
        return self

    def _range_filter(self, field_type: FieldType, range_value: RangeValue):
        for literal, value in range_value.items():
            v = self.set_filter(field_type, value)

            self._query[f"filters[{field_type}][{literal}]"] = v
        return self

    def filter(
        self, value: Optional[Union[MatchDict, RangeDict]]
    ) -> SnapshotSearchAPIV2Limit:
        if isinstance(value, MatchDict):
            for k, v in value.items():
                self._match_filter(k, v)
        elif isinstance(value, RangeDict):
            for k, v in value.items():
                self._range_filter(k, v)
        else:
            raise TypeError("検索には特定の型を指定する必要があります")
        return SnapshotSearchAPIV2Limit(self._query)
