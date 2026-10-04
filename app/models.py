from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


class Config(Base):
    __tablename__ = "config"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)


class IndexFolder(Base):
    __tablename__ = "index_folders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExcludedPath(Base):
    __tablename__ = "excluded_paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'path' | 'extension'


class FileTypeConfig(Base):
    __tablename__ = "file_type_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    extension = Column(String, nullable=False, unique=True)
    chunker = Column(String, nullable=False)  # 'excel' | 'heading' | 'slide' | 'generic'
    enabled = Column(Integer, nullable=False, default=1)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    path_patterns = Column(Text, nullable=False)  # JSON array string


class DocType(Base):
    __tablename__ = "doc_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    path_patterns = Column(Text, nullable=False)  # JSON array string


class Synonym(Base):
    __tablename__ = "synonyms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term = Column(String, nullable=False, unique=True)
    synonyms = Column(Text, nullable=False)  # JSON array string


class IndexRun(Base):
    __tablename__ = "index_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="running")  # running | completed | stopped | failed
    changed_xml_path = Column(Text, nullable=True)
    deleted_xml_path = Column(Text, nullable=True)
    # ``total_files`` is retained for old records and clients.  New runs use
    # discovered/processed counters because discovery is intentionally lazy.
    total_files = Column(Integer, default=0)
    discovered_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    discovery_complete = Column(Boolean, default=False)
    indexed_files = Column(Integer, default=0)
    skipped_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    deleted_files = Column(Integer, default=0)
    details_complete = Column(Boolean, default=True)
    detail_rows_retained = Column(Integer, default=0)
    lease_owner = Column(String, nullable=True)
    lease_expires_at = Column(DateTime, nullable=True)

    files = relationship("IndexRunFile", back_populates="run", cascade="all, delete-orphan")


class IndexRunFile(Base):
    __tablename__ = "index_run_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("index_runs.id"), nullable=False, index=True)
    file_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    chunks_indexed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    run = relationship("IndexRun", back_populates="files")


class IncrementalXmlConfig(Base):
    __tablename__ = "incremental_xml_config"

    id = Column(Integer, primary_key=True, default=1)
    changed_xml_path = Column(Text, nullable=True)
    deleted_xml_path = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("id = 1", name="singleton_id_check"),
    )
