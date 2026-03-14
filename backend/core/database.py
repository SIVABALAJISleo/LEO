import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hyper_test.db")

print("Debug: Creating engine...")
engine = create_engine(DATABASE_URL)
print("Debug: Engine created.")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("Debug: Creating base...")
Base = declarative_base()
print("Debug: Base created.")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True) # Firebase UID
    tenant_id = Column(String, index=True) # Multi-tenant isolation ID
    email = Column(String, unique=True, index=True)
    tier = Column(String, default="free") # free, pro, enterprise
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    tenant_id = Column(String, index=True)
    paypal_order_id = Column(String, unique=True)
    status = Column(String) # active, cancelled, expired
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class DocumentMetadata(Base):
    __tablename__ = "document_metadata"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    user_id = Column(Integer)
    tenant_id = Column(String, index=True)
    content_hash = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class UsageMetric(Base):
    __tablename__ = "usage_metrics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    tenant_id = Column(String, index=True)
    metric_type = Column(String) # 'request', 'token', 'storage_bytes'
    value = Column(Integer, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class QueryCluster(Base):
    """Layer 2: Canonical query clustering for answer reuse."""
    __tablename__ = "query_clusters"
    id = Column(Integer, primary_key=True, index=True)
    cluster_hash = Column(String, unique=True, index=True)
    canonical_query = Column(String)
    canonical_answer = Column(Text)
    tenant_id = Column(String, index=True)
    use_count = Column(Integer, default=1)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
