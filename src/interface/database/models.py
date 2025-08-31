from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, DECIMAL, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class RiskCategory(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AssessmentType(enum.Enum):
    initial = "initial"
    update = "update"
    periodic = "periodic"


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(SQLEnum(UserStatus), default=UserStatus.active)

    # Relationships
    features = relationship("UserFeature", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("RiskAssessment", back_populates="user", cascade="all, delete-orphan")
    history = relationship("FeatureHistory", back_populates="user", cascade="all, delete-orphan")


class UserFeature(Base):
    __tablename__ = "user_features"

    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # Categorical Features
    name_education_type = Column(String(100))
    name_seller_industry = Column(String(100))
    truecalr_flag = Column(String(20))

    # Numerical Features
    region_rating_client = Column(Integer)
    reg_region_not_live_region = Column(Integer)
    reg_region_not_work_region = Column(Integer)
    live_region_not_work_region = Column(Integer)
    amt_drawings_atm_current = Column(DECIMAL(15, 2))
    amt_drawings_current = Column(DECIMAL(15, 2))
    amt_drawings_other_current = Column(DECIMAL(15, 2))
    amt_drawings_pos_current = Column(DECIMAL(15, 2))
    cnt_drawings_atm_current = Column(DECIMAL(10, 2))
    cnt_drawings_current = Column(DECIMAL(10, 2))
    cnt_drawings_other_current = Column(DECIMAL(10, 2))
    cnt_drawings_pos_current = Column(DECIMAL(10, 2))
    sellerplace_area = Column(Integer)
    rchrg_frq = Column(DECIMAL(10, 2))
    trd_acc = Column(DECIMAL(10, 2))
    ofc_doc_exp = Column(Integer)
    gst_fil_def = Column(Integer)
    sim_card_fail = Column(Integer)
    ecom_shop_return = Column(Integer)
    utility_bil = Column(DECIMAL(15, 2))
    reg_veh_challan = Column(Integer)
    linkedin_data = Column(Integer)
    rev_frm_uber_rapido = Column(DECIMAL(15, 2))
    no_of_smrt_card = Column(Integer)
    no_type_of_acc = Column(Integer)

    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_current = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="features")
    assessments = relationship("RiskAssessment", back_populates="features")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    assessment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    feature_id = Column(Integer, ForeignKey("user_features.feature_id", ondelete="CASCADE"), nullable=False)

    # Model Results
    base_value = Column(DECIMAL(10, 6))
    prediction_probability = Column(DECIMAL(10, 6))
    risk_category = Column(SQLEnum(RiskCategory))
    model_version = Column(String(50))

    # SHAP Explanations
    feature_impacts = Column(JSON)

    # Metadata
    assessed_at = Column(TIMESTAMP, default=datetime.utcnow)
    assessment_type = Column(SQLEnum(AssessmentType), default=AssessmentType.initial)

    # Relationships
    user = relationship("User", back_populates="assessments")
    features = relationship("UserFeature", back_populates="assessments")


class FeatureHistory(Base):
    __tablename__ = "feature_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    feature_name = Column(String(100), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(String(100))
    change_reason = Column(Text)
    changed_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="history")


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    model_id = Column(String(50), primary_key=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50))
    performance_metrics = Column(JSON)
    deployed_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)