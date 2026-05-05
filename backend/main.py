from fastapi import FastAPI
from api.upload import router as upload_router  # type: ignore      

app = FastAPI()

app.include_router(upload_router)
