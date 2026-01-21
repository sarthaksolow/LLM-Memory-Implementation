from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pgvector.sqlalchemy import Vector
import numpy as np
import config

Base = declarative_base()

# ======================
# Short-term Memory (STM)
# ======================
class ShortTermMessage(Base):
    __tablename__ = "stm_messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


# ======================
# Long-term Memory (LTM)
# ======================
class LongTermMemory(Base):
    __tablename__ = "ltm_memories"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    memory_type = Column(String(50), nullable=False)
    importance = Column(Integer, nullable=False)
    embedding = Column(Vector(config.EMBEDDING_DIM))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)


# ======================
# Database Manager
# ======================
class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)

        # ✅ IMPORTANT: enable pgvector BEFORE creating tables
        with self.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()

        # ✅ Now safe to create tables using VECTOR
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)

    # ==================
    # STM Operations
    # ==================
    def add_stm_message(self, user_id, session_id, role, content):
        session = self.Session()
        try:
            msg = ShortTermMessage(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
            )
            session.add(msg)
            session.commit()
        finally:
            session.close()

    def get_stm_messages(self, session_id, limit=None):
        session = self.Session()
        try:
            q = (
                session.query(ShortTermMessage)
                .filter(ShortTermMessage.session_id == session_id)
                .order_by(ShortTermMessage.timestamp.desc())
            )
            if limit:
                q = q.limit(limit)
            return list(reversed(q.all()))
        finally:
            session.close()

    # ==================
    # LTM Operations
    # ==================
    def store_ltm(self, user_id, content, memory_type, importance, embedding):
        session = self.Session()
        try:
            mem = LongTermMemory(
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
                embedding=embedding.tolist(),
            )
            session.add(mem)
            session.commit()
            return mem.id
        finally:
            session.close()

    def search_ltm(self, user_id, query_embedding, top_k=5, min_similarity=0.7):
        session = self.Session()
        try:
            similarity_expr = (
                1 - LongTermMemory.embedding.cosine_distance(query_embedding.tolist())
            ).label("similarity")

            q = (
                session.query(LongTermMemory, similarity_expr)
                .filter(LongTermMemory.user_id == user_id)
                .order_by(LongTermMemory.embedding.cosine_distance(query_embedding.tolist()))
                .limit(top_k)
            )

            results = []
            for mem, similarity in q.all():
                if similarity >= min_similarity:
                    results.append(
                        {
                            "id": mem.id,
                            "content": mem.content,
                            "memory_type": mem.memory_type,
                            "importance": mem.importance,
                            "similarity": float(similarity),
                            "created_at": mem.created_at,
                            "access_count": mem.access_count,
                        }
                    )
            return results
        finally:
            session.close()

    def update_memory_access(self, memory_id):
        session = self.Session()
        try:
            mem = session.query(LongTermMemory).get(memory_id)
            if mem:
                mem.access_count += 1
                mem.last_accessed = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def get_all_ltm(self, user_id):
        session = self.Session()
        try:
            return (
                session.query(LongTermMemory)
                .filter(LongTermMemory.user_id == user_id)
                .order_by(LongTermMemory.created_at.desc())
                .all()
            )
        finally:
            session.close()

    def delete_ltm(self, memory_id):
        session = self.Session()
        try:
            session.query(LongTermMemory).filter(
                LongTermMemory.id == memory_id
            ).delete()
            session.commit()
        finally:
            session.close()

    def clear_user_data(self, user_id):
        session = self.Session()
        try:
            session.query(ShortTermMessage).filter(
                ShortTermMessage.user_id == user_id
            ).delete()
            session.query(LongTermMemory).filter(
                LongTermMemory.user_id == user_id
            ).delete()
            session.commit()
        finally:
            session.close()
