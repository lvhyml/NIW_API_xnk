import ssl

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from endpoints_login import login_router
from endpoints_user import user_router
from endpoints_product import product_router

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(login_router)
app.include_router(user_router)
app.include_router(product_router)

# Run the FastAPI app
if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host='0.0.0.0', port=7002, reload=True)
    # uvicorn.run("main:app", host='0.0.0.0', port=7001)
