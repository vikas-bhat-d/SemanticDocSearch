import os
import threading

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Database path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "config.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
SQLITE_BUSY_TIMEOUT_MS = 30_000

# SQLite permits only one writer at a time.  Indexing uses several worker
# threads, so keep application writes from competing with each other while
# the database-level busy timeout handles external processes.
db_write_lock = threading.RLock()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": SQLITE_BUSY_TIMEOUT_MS / 1000,
    },
)


@event.listens_for(engine, "connect")
def _configure_sqlite_connection(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
    finally:
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def upgrade_schema(db_engine=engine):
    """Apply small, additive, idempotent schema migrations.

    ``create_all`` cannot add columns to an existing SQLite table.  The
    migration deliberately only adds run metadata and never removes the
    historical ``index_run_files`` table or its rows.
    """
    migrations = {
        "index_run_counters_v1": {
            "discovered_files": "INTEGER DEFAULT 0",
            "processed_files": "INTEGER DEFAULT 0",
            "discovery_complete": "BOOLEAN DEFAULT 0",
            "details_complete": "BOOLEAN DEFAULT 1",
            "detail_rows_retained": "INTEGER DEFAULT 0",
        },
        "index_run_leases_v2": {
            "lease_owner": "VARCHAR(128)",
            "lease_expires_at": "DATETIME",
        }
    }

    with db_engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE IF NOT EXISTS schema_migrations "
            "(version VARCHAR(128) PRIMARY KEY, applied_at DATETIME NOT NULL)"
        ))

        inspector = inspect(connection)
        existing_tables = set(inspector.get_table_names())
        applied = {
            row[0]
            for row in connection.execute(text("SELECT version FROM schema_migrations"))
        }

        for version, columns in migrations.items():
            if version in applied:
                continue

            if "index_runs" in existing_tables:
                existing_columns = {
                    col["name"] for col in inspect(connection).get_columns("index_runs")
                }
                added_discovery_column = "discovery_complete" not in existing_columns
                for column, definition in columns.items():
                    if column not in existing_columns:
                        connection.execute(text(
                            f"ALTER TABLE index_runs ADD COLUMN {column} {definition}"
                        ))
                if added_discovery_column:
                    # Existing terminal rows already had a complete, known
                    # total.  New runs explicitly start at false in the ORM.
                    connection.execute(text(
                        "UPDATE index_runs SET discovery_complete = 1 "
                        "WHERE status != 'running'"
                    ))

            connection.execute(
                text("INSERT INTO schema_migrations(version, applied_at) "
                     "VALUES (:version, CURRENT_TIMESTAMP)"),
                {"version": version},
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
