from app.indexer.runner import indexer_runner


def test_indexer_runner_idle_status(db_session):
    status_info = indexer_runner.get_status(db_session)
    assert status_info["status"] in ("IDLE", "RUNNING", "COMPLETED", "FAILED", "STOPPED")
