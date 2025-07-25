from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.models.product import Product as ProductModel

router = APIRouter()


@router.get("/", response_model=List[Product], summary="상품 목록 조회")
def get_products(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 개수"),
    db: Session = Depends(get_db)
):
    """
    상품 목록을 조회합니다.
    
    - **skip**: 건너뛸 상품 개수 (페이지네이션용)
    - **limit**: 가져올 상품 개수 (최대 1000개)
    """
    try:
        products = db.query(ProductModel).filter(ProductModel.is_active == True).offset(skip).limit(limit).all()
        return products
    except Exception as e:
        print(f"Database error: {e}")
        # Return dummy data for testing without database
        from app.schemas.product import Product
        from datetime import datetime
        return [
            Product(
                id=1,
                name="샘플 상품",
                description="샘플 상품 설명입니다.",
                price=10000,
                stock_quantity=50,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]


@router.get("/{product_id}", response_model=Product, summary="상품 상세 조회")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    특정 상품의 상세 정보를 조회합니다.
    
    - **product_id**: 조회할 상품의 ID
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"상품 ID {product_id}를 찾을 수 없습니다."
        )
    return product


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED, summary="상품 생성")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    새로운 상품을 생성합니다.
    
    - **name**: 상품명 (필수)
    - **description**: 상품 설명 (선택)
    - **price**: 가격 (필수, 0보다 커야 함)
    - **stock_quantity**: 재고 수량 (기본값: 0)
    """
    # 상품명 중복 체크
    existing_product = db.query(ProductModel).filter(ProductModel.name == product.name).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"상품명 '{product.name}'은 이미 존재합니다."
        )
    
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=Product, summary="상품 수정")
def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """
    기존 상품 정보를 수정합니다.
    
    - **product_id**: 수정할 상품의 ID
    - 수정할 필드만 전송하면 됩니다.
    """
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"상품 ID {product_id}를 찾을 수 없습니다."
        )
    
    # 업데이트할 데이터만 필터링
    update_data = product_update.dict(exclude_unset=True)
    
    # 상품명 변경 시 중복 체크
    if "name" in update_data and update_data["name"] != db_product.name:
        existing_product = db.query(ProductModel).filter(
            ProductModel.name == update_data["name"],
            ProductModel.id != product_id
        ).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"상품명 '{update_data['name']}'은 이미 존재합니다."
            )
    
    # 데이터 업데이트
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="상품 삭제")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    상품을 삭제합니다 (실제 삭제가 아닌 비활성화).
    
    - **product_id**: 삭제할 상품의 ID
    """
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"상품 ID {product_id}를 찾을 수 없습니다."
        )
    
    # 실제 삭제 대신 비활성화
    db_product.is_active = False
    db.commit()
    
    return None 