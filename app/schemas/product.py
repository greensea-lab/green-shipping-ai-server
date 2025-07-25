from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """상품 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=255, description="상품명")
    description: Optional[str] = Field(None, max_length=1000, description="상품 설명")
    price: int = Field(..., gt=0, description="가격")
    stock_quantity: int = Field(0, ge=0, description="재고 수량")


class ProductCreate(ProductBase):
    """상품 생성 스키마"""
    pass


class ProductUpdate(BaseModel):
    """상품 수정 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[int] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class Product(ProductBase):
    """상품 응답 스키마"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "샘플 상품",
                "description": "샘플 상품 설명입니다.",
                "price": 10000,
                "stock_quantity": 50,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        } 