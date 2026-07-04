from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


class ProductRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Product).all()

    @staticmethod
    def get_by_id(db: Session, product_id):
        return db.query(Product).filter(
            Product.id == product_id
        ).first()

    @staticmethod
    def create(
        db: Session,
        product_data: ProductCreate
    ):
        product = Product(**product_data.model_dump())

        db.add(product)

        db.commit()

        db.refresh(product)

        return product