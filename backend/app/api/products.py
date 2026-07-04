from typing import List

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.product import (
    ProductCreate,
    ProductResponse
)

from app.services.product_service import ProductService


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


@router.get(
    "/",
    response_model=List[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):
    return ProductService.get_products(db)


@router.post(
    "/",
    response_model=ProductResponse
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    return ProductService.create_product(
        db,
        product
    )