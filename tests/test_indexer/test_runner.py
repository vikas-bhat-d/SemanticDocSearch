from datetime import datetime, timedelta

from app.indexer.runner import indexer_runner, _pending_files_from_previous_stopped_run
from app.models import IndexRun, IndexRunFile


def test_indexer_runner_idle_status(db_session):
    status_info = indexer_runner.get_status(db_session)
    assert status_info["status"] in ("IDLE", "RUNNING", "COMPLETED", "FAILED", "STOPPED")


def test_status_reconciles_expired_running_run(db_session):
    run = IndexRun(
        status="running",
        lease_owner="abandoned-process",
        lease_expires_at=datetime.utcnow() - timedelta(seconds=1),
    )
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)

    runner = type(indexer_runner)()
    runner.current_run_id = run.id

    status_info = runner.get_status(db_session)

    assert status_info["status"] == "FAILED"
    db_session.refresh(run)
    assert run.stopped_at is not None
    assert run.lease_owner is None
    assert run.lease_expires_at is None


def test_resume_uses_only_immediately_previous_stopped_run(db_session):
    stopped_run = IndexRun(status="stopped")
    db_session.add(stopped_run)
    db_session.commit()
    db_session.refresh(stopped_run)
    db_session.add(IndexRunFile(
        run_id=stopped_run.id,
        file_path=r"C:\docs\old-pending.docx",
        status="pending"
    ))
    db_session.commit()

    completed_run = IndexRun(status="completed")
    db_session.add(completed_run)
    db_session.commit()
    db_session.refresh(completed_run)

    current_run = IndexRun(status="running")
    db_session.add(current_run)
    db_session.commit()
    db_session.refresh(current_run)

    assert _pending_files_from_previous_stopped_run(db_session, current_run.id) == []


def test_resume_returns_pending_files_from_immediately_previous_stopped_run(db_session):
    stopped_run = IndexRun(status="stopped")
    db_session.add(stopped_run)
    db_session.commit()
    db_session.refresh(stopped_run)
    db_session.add(IndexRunFile(
        run_id=stopped_run.id,
        file_path=r"C:\docs\pending.docx",
        status="pending"
    ))
    db_session.commit()

    current_run = IndexRun(status="running")
    db_session.add(current_run)
    db_session.commit()
    db_session.refresh(current_run)

    assert _pending_files_from_previous_stopped_run(db_session, current_run.id) == [
        r"C:\docs\pending.docx"
    ]
