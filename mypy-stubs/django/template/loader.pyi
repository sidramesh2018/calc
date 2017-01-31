from typing import Optional, Dict, Any

from django.http import HttpRequest
from django.utils.safestring import SafeString


def render_to_string(
        template_name: str,
        context: Optional[Dict[str, Any]]=None,
        request: Optional[HttpRequest]=None,
        using: Optional[str]=None) -> SafeString:
    ...
