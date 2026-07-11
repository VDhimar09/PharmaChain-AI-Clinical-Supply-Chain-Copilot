from typing import List

from fastapi import BackgroundTasks
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.user import User

from app.schemas.product import (
    ProductCreate,
    ProductResponse
)

from app.services.product_service import ProductService
from app.services.audit_service import AuditService


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


@router.get(
    "/",
    response_model=List[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.read")
    ),
):
    return ProductService.get_products(db)


@router.post(
    "/",
    response_model=ProductResponse
)
def create_product(
    request: Request,
    background_tasks: BackgroundTasks,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory.write")
    ),
):
    created_product = ProductService.create_product(
        db,
        product
    )

    product_data = jsonable_encoder(
        created_product
    )

    AuditService.enqueue_log(
        background_tasks,
        action="PRODUCT_CREATED",
        resource_type="Product",
        status_code=200,
        request=request,
        user=current_user,
        resource_id=product_data.get("id"),
        details={
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "supplier_id": product.supplier_id,
        },
    )

    return created_product
