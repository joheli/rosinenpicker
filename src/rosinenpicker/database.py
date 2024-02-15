from typing import List
from sqlalchemy import ForeignKey
from time import time_ns
from sqlalchemy import String, CHAR, create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class DbRun(Base):
    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(40))
    yml_filename: Mapped[str] = mapped_column(String(40))
    yml_sha256: Mapped[str] = mapped_column(String(64))
    timepoint: Mapped[int] = mapped_column(default=time_ns())
    strategies: Mapped[List["DbStrategy"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    def __repr__(self) -> str:
        return f"Run(id={self.id!r}, title={self.title!r}, yml_sha256={self.yml_sha256!r})"

class DbStrategy(Base):
    __tablename__ = "strategy"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("run.id"))
    name: Mapped[str] = mapped_column(String(100))
    processed_directory: Mapped[str] = mapped_column(String(200))
    file_name_pattern: Mapped[str] = mapped_column(String(100))
    file_content_pattern: Mapped[str] = mapped_column(String(100), nullable=True)
    export_format: Mapped[str] = mapped_column(String(10), nullable=True)
    export_path: Mapped[str] = mapped_column(String(200))
    export_csv_divider: Mapped[str] = mapped_column(CHAR, nullable=True)
    run: Mapped["DbRun"] = relationship(back_populates="strategies")
    processed_files: Mapped[List["DbProcessedFile"]] = relationship(back_populates="strategy", cascade="all, delete-orphan")
    def __repr__(self) -> str:
        return f"Strategy(id={self.id!r}, export_path={self.export_path!r})"
    
class DbProcessedFile(Base):
    __tablename__ = "processed_file"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategy.id"))
    filename: Mapped[str] = mapped_column(String(40))
    sha256: Mapped[str] = mapped_column(String(64))
    strategy: Mapped["DbStrategy"] = relationship(back_populates="processed_files")
    matches: Mapped[List["DbMatch"]] = relationship(back_populates="processed_file")
    def __repr__(self) -> str:
        return f"File(id={self.id!r}, name={self.name!r}, sha256={self.sha256!r})"
    
class DbMatch(Base):
    __tablename__ = "match"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("processed_file.id"))
    term: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(String(100), nullable = True)
    processed_file: Mapped["DbProcessedFile"] = relationship(back_populates="matches")
    def __repr__(self) -> str:
        return f"Match(id={self.id!r}, term={self.term!r}, content={self.content!r})"
    