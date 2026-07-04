from sqlalchemy.orm import Session

from app.repositories.procurement_request_repository import (
    ProcurementRequestRepository
)

from app.schemas.procurement_request import (
    ProcurementRequestCreate
)


class ProcurementRequestService:

    @staticmethod
    def get_procurement_requests(
        db: Session
    ):
        return ProcurementRequestRepository.get_all(
            db
        )

    @staticmethod
    def get_procurement_request_by_id(
        db: Session,
        request_id
    ):
        return ProcurementRequestRepository.get_by_id(
            db,
            request_id
        )

    @staticmethod
    def create_procurement_request(
        db: Session,
        request_data: ProcurementRequestCreate
    ):
        return ProcurementRequestRepository.create(
            db,
            request_data
        )

    @staticmethod
    def delete_procurement_request(
        db: Session,
        request_id
    ):
        return ProcurementRequestRepository.delete(
            db,
            request_id
        )

    @staticmethod
    def get_procurement_statistics(
        db: Session
    ):
        return ProcurementRequestRepository.get_procurement_statistics(
            db
        )