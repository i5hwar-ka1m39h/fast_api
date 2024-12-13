from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class ImageRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_image_url: str
    mask_image_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
     