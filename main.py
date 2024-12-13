from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn



from models import ImageRecord
from database import get_async_session, engine
from s3_utils import s3Uploader
from dotenv import load_dotenv
import os

load_dotenv()


S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'name')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', 'key')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', 'secret')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

s3_uploader = s3Uploader(
    bucket_name=S3_BUCKET_NAME,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

@app.on_event('startup')
async def start_up():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

@app.get('/health/')
async def health():
    return {"message":"server is running smoothly"}

@app.post('/uploads-images/')
async def upload_image(
    original_image: UploadFile = File(...), 
    mask_image: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
    ):
    original_url = s3_uploader.upload_file(original_image, 'original')
    if not original_url:
        return {"error":"failed during the uploading of image"}
    
    mask_url = s3_uploader.upload_file(mask_image, 'mask')
    if not mask_url:
        return {"error":"failed during the uploading of image"}
    
    image_record = ImageRecord(
        original_image_url= original_url,
        mask_image_url=mask_url
    )

    session.add(image_record)
    await session.commit()
    await session.refresh(image_record)

    return {
        "id":image_record.id,
        "original_image_url": original_url,
        "mask_image_url": mask_url

    }


@app.get("/images/")
async def get_images(session:AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(ImageRecord))
    images = result.scalars().all()
    return images


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)