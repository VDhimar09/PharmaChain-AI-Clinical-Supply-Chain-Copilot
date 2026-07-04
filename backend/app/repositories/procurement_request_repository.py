from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.procurement_request import (
    ProcurementRequest
)

from app.schemas.procurement_request import (
    ProcurementRequestCreate
)


class ProcurementRequestRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(
            ProcurementRequest
        ).all()

    @staticmethod
    def get_by_id(
        db: Session,
        request_id
    ):
        return db.query(
            ProcurementRequest
        ).filter(
            ProcurementRequest.id == request_id
        ).first()

    @staticmethod
    def create(
        db: Session,
        request_data: ProcurementRequestCreate
    ):
        procurement_request = ProcurementRequest(
            **request_data.model_dump()
        )

        db.add(procurement_request)
        db.commit()
        db.refresh(procurement_request)

        return procurement_request

    @staticmethod
    def delete(
        db: Session,
        request_id
    ):
        procurement_request = db.query(
            ProcurementRequest
        ).filter(
            ProcurementRequest.id == request_id
        ).first()

        if procurement_request:
            db.delete(procurement_request)
            db.commit()

        return procurement_request

    @staticmethod
    def get_procurement_statistics(
        db: Session
    ):
        total_requests = db.query(
            func.count(ProcurementRequest.id)
        ).scalar() or 0

        pending_requests = db.query(
            func.count(ProcurementRequest.id)
        ).filter(
            ProcurementRequest.status == "PENDING"
        ).scalar() or 0

        approved_requests = db.query(
            func.count(ProcurementRequest.id)
        ).filter(
            ProcurementRequest.status == "APPROVED"
        ).scalar() or 0

        rejected_requests = db.query(
            func.count(ProcurementRequest.id)
        ).filter(
            ProcurementRequest.status == "REJECTED"
        ).scalar() or 0

        return {
            "total_requests": total_requests,
            "pending_requests": pending_requests,
            "approved_requests": approved_requests,
            "rejected_requests": rejected_requests
        }