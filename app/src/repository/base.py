import re
import uuid
from collections.abc import Sequence
from typing import TypeAlias

from asyncpg import Connection, Record

from src.exceptions import map_asyncpg_errors

SpRow: TypeAlias = dict[str, object]
SpRows: TypeAlias = list[SpRow]
SpMultiResult: TypeAlias = dict[str, SpRows]
SpResult: TypeAlias = SpRows | SpMultiResult

_FUNCTION_NAME_RE = re.compile(
    r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$"
)
_CURSOR_PLACEHOLDER_RE = re.compile(r"^@cur\d*$")


class BaseRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def fetchrow(self, query: str, *args: object) -> Record | None:
        with map_asyncpg_errors():
            return await self.connection.fetchrow(query, *args)

    async def fetch(self, query: str, *args: object) -> list[Record]:
        with map_asyncpg_errors():
            return await self.connection.fetch(query, *args)

    async def execute(self, query: str, *args: object) -> str:
        with map_asyncpg_errors():
            return await self.connection.execute(query, *args)

    async def call_sp(
        self,
        method: str,
        *args: object,
        cursor: bool = False,
        session_user_id: int | None = None,
        module_code: str = "MYSPACE",
    ) -> SpResult:
        """
        Call a PostgreSQL stored function.

        - Pass arguments directly: call_sp("public.fn", id)
        - For refcursor reads use cursor=True or pass "@cur"
        """
        self._validate_function_name(method)

        call_args = list(args)
        if cursor and not any(self._is_cursor_placeholder(arg) for arg in call_args):
            call_args.insert(0, "@cur")

        unique_suffix = uuid.uuid4().hex[:8]
        bound_args: list[object] = []
        cursor_names: list[str] = []
        for arg in call_args:
            if self._is_cursor_placeholder(arg):
                cursor_name = self._resolve_cursor_placeholder(arg, unique_suffix)
                bound_args.append(cursor_name)
                cursor_names.append(cursor_name)
            else:
                bound_args.append(arg)

        query = self._build_select_function_sql(method, len(bound_args))

        with map_asyncpg_errors():
            await self._set_db_session(session_user_id, module_code)

            if not cursor_names:
                rows = await self.connection.fetch(query, *bound_args)
                return self._rows_to_dicts(rows)

            await self.connection.execute(query, *bound_args)

            if len(cursor_names) == 1:
                return await self._fetch_refcursor(cursor_names[0])

            return {
                f"data_{index}": await self._fetch_refcursor(name)
                for index, name in enumerate(cursor_names, start=1)
            }

    async def _set_db_session(
        self,
        session_user_id: int | None,
        module_code: str,
    ) -> None:
        if session_user_id is not None:
            await self.connection.fetchval(
                "select set_config('myapp.user_id', $1, false)",
                str(session_user_id),
            )
        await self.connection.fetchval(
            "select set_config('myapp.module_code', $1, false)",
            module_code,
        )

    async def _fetch_refcursor(self, cursor_name: str) -> SpRows:
        rows = await self.connection.fetch(f'fetch all in "{cursor_name}"')
        return self._rows_to_dicts(rows)

    @staticmethod
    def _build_select_function_sql(method: str, args_count: int) -> str:
        if args_count == 0:
            return f"select {method}()"
        placeholders = ", ".join(f"${index}" for index in range(1, args_count + 1))
        return f"select {method}({placeholders})"

    @staticmethod
    def _validate_function_name(method: str) -> None:
        if not _FUNCTION_NAME_RE.fullmatch(method):
            raise ValueError(f"Invalid stored function name: {method}")

    @staticmethod
    def _resolve_cursor_placeholder(arg: str, unique_suffix: str) -> str:
        if not _CURSOR_PLACEHOLDER_RE.fullmatch(arg):
            raise ValueError(f"Invalid refcursor argument: {arg}")
        return f"{arg}_{unique_suffix}"

    @staticmethod
    def _is_cursor_placeholder(arg: object) -> bool:
        return isinstance(arg, str) and arg.startswith("@cur")

    @staticmethod
    def _rows_to_dicts(rows: Sequence[Record]) -> SpRows:
        return [dict(row) for row in rows]
