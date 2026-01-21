from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

Base = declarative_base()

# ======================
# Raw Messages (STM)
# ======================
class Message(Base):
    __tablename__ = "messages_summary"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


# ======================
# Summary (LTM-lite)
# ======================
class ConversationSummary(Base):
    __tablename__ = "conversation_summary"

    session_id = Column(String(100), primary_key=True)
    summary = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    # ---------- Messages ----------
    def add_message(self, session_id, role, content):
        s = self.Session()
        try:
            s.add(Message(
                session_id=session_id,
                role=role,
                content=content
            ))
            s.commit()
        finally:
            s.close()

    def get_messages(self, session_id):
        s = self.Session()
        try:
            return s.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.timestamp).all()
        finally:
            s.close()

    def delete_messages(self, message_ids):
        s = self.Session()
        try:
            s.query(Message).filter(
                Message.id.in_(message_ids)
            ).delete(synchronize_session=False)
            s.commit()
        finally:
            s.close()

    # ---------- Summary ----------
    def get_summary(self, session_id):
        s = self.Session()
        try:
            row = s.query(ConversationSummary).filter(
                ConversationSummary.session_id == session_id
            ).first()
            return row.summary if row else None
        finally:
            s.close()

    def upsert_summary(self, session_id, summary):
        s = self.Session()
        try:
            row = s.query(ConversationSummary).filter(
                ConversationSummary.session_id == session_id
            ).first()

            if row:
                row.summary = summary
                row.updated_at = datetime.utcnow()
            else:
                s.add(ConversationSummary(
                    session_id=session_id,
                    summary=summary
                ))
            s.commit()
        finally:
            s.close()
