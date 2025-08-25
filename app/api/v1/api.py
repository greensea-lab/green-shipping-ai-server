from fastapi import APIRouter
from app.api.v1.endpoints import users, products
from app.api.v1.endpoints import ai as ai_endpoints
from app.api.v1.endpoints import geo as geo_endpoints

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"]) 
api_router.include_router(ai_endpoints.router, prefix="/ai", tags=["ai"]) 
api_router.include_router(geo_endpoints.router, prefix="/geo", tags=["geo"]) 
