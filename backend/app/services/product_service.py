from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate


class ProductService:

    @staticmethod
    def get_products(
        db: Session
    ):
        return ProductRepository.get_all(db)

    @staticmethod
    def create_product(
        db: Session,
        product_data: ProductCreate
    ):
        return ProductRepository.create(
            db,
            product_data
        )

    @staticmethod
    def get_product_by_id(
        db: Session,
        product_id,
    ):
        return ProductRepository.get_by_id(
            db,
            product_id,
        )
