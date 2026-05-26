from collections.abc import Generator
from contextlib import contextmanager

from asyncpg.exceptions import (
    CheckViolationError,
    ForeignKeyViolationError,
    IntegrityConstraintViolationError,
    PostgresError,
    UndefinedColumnError,
    UndefinedTableError,
    UniqueViolationError,
)

from .infra import (
    CheckConstraintError,
    DatabaseConfigurationError,
    DataIntegrityError,
    DuplicateKeyError,
    ForeignKeyError,
    InfrastructureError,
    UnexpectedDatabaseError,
)


@contextmanager
def map_asyncpg_errors() -> Generator[None, None, None]:
    try:
        yield

    except UniqueViolationError as e:
        raise DuplicateKeyError() from e

    except ForeignKeyViolationError as e:
        raise ForeignKeyError() from e

    except CheckViolationError as e:
        raise CheckConstraintError() from e

    except IntegrityConstraintViolationError as e:
        raise DataIntegrityError() from e

    except (UndefinedColumnError, UndefinedTableError) as e:
        raise DatabaseConfigurationError() from e

    except InfrastructureError:
        raise

    except PostgresError as e:
        raise UnexpectedDatabaseError() from e
