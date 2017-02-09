from typing import Dict, Any


class QuerySet:
    def filter(self, **kwargs: Any) -> QuerySet:
        ...
