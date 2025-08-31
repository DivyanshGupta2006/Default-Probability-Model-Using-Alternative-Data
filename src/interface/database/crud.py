from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from typing import Dict, List, Optional
from datetime import datetime
import json

from .models import User, UserFeature, RiskAssessment, FeatureHistory, RiskCategory, AssessmentType


class UserCRUD:
    @staticmethod
    def create_user(db: Session, user_data: Dict) -> User:
        """Create a new user"""
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_all_active_users(db: Session) -> List[User]:
        """Get all active users"""
        return db.query(User).filter(User.status == "active").all()

    @staticmethod
    def update_user_status(db: Session, user_id: str, status: str) -> bool:
        """Update user status"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.status = status
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False


class FeatureCRUD:
    @staticmethod
    def create_user_features(db: Session, user_id: str, features: Dict) -> UserFeature:
        """Create new user features"""
        # Map the features to match database column names
        feature_data = {
            'user_id': user_id,
            **{k.lower(): v for k, v in features.items()}
        }

        db_features = UserFeature(**feature_data)
        db.add(db_features)
        db.commit()
        db.refresh(db_features)
        return db_features

    @staticmethod
    def get_current_features(db: Session, user_id: str) -> Optional[UserFeature]:
        """Get current features for a user"""
        return db.query(UserFeature).filter(
            and_(UserFeature.user_id == user_id, UserFeature.is_current == True)
        ).first()

    @staticmethod
    def mark_features_as_historical(db: Session, user_id: str):
        """Mark current features as historical"""
        db.query(UserFeature).filter(
            and_(UserFeature.user_id == user_id, UserFeature.is_current == True)
        ).update({UserFeature.is_current: False})
        db.commit()

    @staticmethod
    def update_user_features(db: Session, user_id: str, updated_features: Dict,
                             changed_by: str = "system") -> UserFeature:
        """Update user features with audit trail"""
        # Get current features
        current_features = FeatureCRUD.get_current_features(db, user_id)
        if not current_features:
            raise ValueError(f"No current features found for user {user_id}")

        # Log changes to history
        for field, new_value in updated_features.items():
            old_value = getattr(current_features, field.lower(), None)
            if str(old_value) != str(new_value):
                history_entry = FeatureHistory(
                    user_id=user_id,
                    feature_name=field,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    changed_by=changed_by,
                    change_reason="Manual update via tracking interface"
                )
                db.add(history_entry)

        # Mark current features as historical
        FeatureCRUD.mark_features_as_historical(db, user_id)

        # Create new current features
        current_dict = {
            column.name: getattr(current_features, column.name)
            for column in current_features.__table__.columns
            if column.name not in ['feature_id', 'created_at', 'updated_at', 'is_current']
        }

        # Update with new values
        for field, value in updated_features.items():
            current_dict[field.lower()] = value

        new_features = FeatureCRUD.create_user_features(db, user_id, current_dict)
        db.commit()
        return new_features


class AssessmentCRUD:
    @staticmethod
    def create_assessment(db: Session, user_id: str, feature_id: int, assessment_data: Dict,
                          assessment_type: str = "initial") -> RiskAssessment:
        """Create a new risk assessment"""

        # Determine risk category based on probability
        probability = assessment_data['prediction_probability']
        if probability < 0.3:
            risk_category = RiskCategory.low
        elif probability < 0.7:
            risk_category = RiskCategory.medium
        else:
            risk_category = RiskCategory.high

        db_assessment = RiskAssessment(
            user_id=user_id,
            feature_id=feature_id,
            base_value=assessment_data['base_value'],
            prediction_probability=assessment_data['prediction_probability'],
            risk_category=risk_category,
            feature_impacts=assessment_data['feature_impacts'],
            assessment_type=AssessmentType(assessment_type),
            model_version="v1.0"  # You can make this dynamic
        )

        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        return db_assessment

    @staticmethod
    def get_latest_assessment(db: Session, user_id: str) -> Optional[RiskAssessment]:
        """Get latest assessment for a user"""
        return db.query(RiskAssessment).filter(
            RiskAssessment.user_id == user_id
        ).order_by(desc(RiskAssessment.assessed_at)).first()

    @staticmethod
    def get_user_assessment_history(db: Session, user_id: str, limit: int = 50) -> List[RiskAssessment]:
        """Get assessment history for a user"""
        return db.query(RiskAssessment).filter(
            RiskAssessment.user_id == user_id
        ).order_by(desc(RiskAssessment.assessed_at)).limit(limit).all()


class PortfolioCRUD:
    @staticmethod
    def get_portfolio_data(db: Session, filters: Optional[Dict] = None) -> List[Dict]:
        """Get complete portfolio data with optional filtering."""

        query = db.query(
            User.user_id,
            User.full_name,
            User.email,
            User.status,
            UserFeature,
            RiskAssessment.prediction_probability,
            RiskAssessment.risk_category,
            RiskAssessment.assessed_at
        ).join(
            UserFeature, and_(User.user_id == UserFeature.user_id, UserFeature.is_current == True)
        ).join(
            RiskAssessment, User.user_id == RiskAssessment.user_id
        )

        # Subquery to ensure we only join with the LATEST assessment for each user
        from sqlalchemy import func
        latest_assessments = db.query(
            RiskAssessment.user_id,
            func.max(RiskAssessment.assessment_id).label('latest_assessment_id')
        ).group_by(RiskAssessment.user_id).subquery()

        query = query.join(
            latest_assessments,
            and_(
                RiskAssessment.user_id == latest_assessments.c.user_id,
                RiskAssessment.assessment_id == latest_assessments.c.latest_assessment_id
            )
        )

        # --- FIX START: Apply filters to the query ---
        if filters:
            if filters.get('risk_level'):
                query = query.filter(RiskAssessment.risk_category == filters['risk_level'])

            if filters.get('status'):
                query = query.filter(User.status == filters['status'])

            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        User.user_id.ilike(search_term),
                        User.full_name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
        # --- FIX END ---

        results = query.order_by(desc(RiskAssessment.assessed_at)).all()

        # Convert to dictionary format
        portfolio_data = []
        for result in results:
            user_id, full_name, email, status, features, prob, risk_cat, assessed_at = result
            user_data = {
                'id': user_id,
                'full_name': full_name,
                'email': email,
                'status': status.value if status else 'unknown',
                'risk_score': float(prob) * 100 if prob else 0,
                'risk_category': risk_cat.value if risk_cat else 'unknown',
                'last_updated': assessed_at.strftime('%Y-%m-%d %H:%M:%S') if assessed_at else 'N/A',
                **{c.name: getattr(features, c.name) for c in features.__table__.columns if
                   c.name not in ['feature_id', 'user_id']}
            }
            portfolio_data.append(user_data)

        return portfolio_data