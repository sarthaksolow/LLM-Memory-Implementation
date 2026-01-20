from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages_trimming'
    
    id = Column(Integer, Sequence('message_id_seq'), primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a new message to the database"""
        session = self.Session()
        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content
            )
            session.add(message)
            session.commit()
        finally:
            session.close()
    
    def get_messages(self, session_id: str, limit: int = None):
        """Get messages for a session, optionally limited to last N messages"""
        session = self.Session()
        try:
            query = session.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.timestamp.desc())
            
            if limit:
                query = query.limit(limit)
            
            messages = query.all()
            # Reverse to get chronological order
            return list(reversed(messages))
        finally:
            session.close()
    
    def trim_messages(self, session_id: str, keep_last: int):
        """Keep only the last N messages, delete older ones"""
        session = self.Session()
        try:
            # Get all message IDs ordered by timestamp
            all_messages = session.query(Message.id).filter(
                Message.session_id == session_id
            ).order_by(Message.timestamp.desc()).all()
            
            if len(all_messages) > keep_last:
                # Get IDs to delete (all except the last keep_last)
                ids_to_delete = [msg.id for msg in all_messages[keep_last:]]
                
                # Delete old messages
                session.query(Message).filter(
                    Message.id.in_(ids_to_delete)
                ).delete(synchronize_session=False)
                
                session.commit()
                return len(ids_to_delete)
            return 0
        finally:
            session.close()
    
    def clear_session(self, session_id: str):
        """Clear all messages for a session"""
        session = self.Session()
        try:
            session.query(Message).filter(
                Message.session_id == session_id
            ).delete()
            session.commit()
        finally:
            session.close()
