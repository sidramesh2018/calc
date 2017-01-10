from typing import Dict

DEFAULT_DB_ALIAS = ...  # type: str

class _StubConnection:
    def ensure_connection(self) -> None: ...

connections = ...  # type: Dict[str, _StubConnection]
