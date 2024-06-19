# api_v1/api.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import json

from .endpoints import pages, auth
from .auth import AuthHandler

auth_handler = AuthHandler()

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(pages.router, prefix="/pages", dependencies=[Depends(auth_handler.auth_wrapper)], tags=["Pages"])

@router.get('/sql')
async def get_query(query: str, request: Request) -> dict:
    """ GET /pages/sql?query='SELECT' - fetches custom query """
    print(query)
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data=query) 
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json.loads(response.content)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function get_query encoutered an error: " + str(e))
