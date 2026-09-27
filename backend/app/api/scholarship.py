from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.scholarship import ScholarshipResponse
from app.services.scholarship_service import list_scholarships

router = APIRouter(prefix="/scholarships", tags=["Scholarships"])


@router.get("", response_model=list[ScholarshipResponse])
@router.get("/", response_model=list[ScholarshipResponse], include_in_schema=False)
def list_scholarships_api(db: Session = Depends(get_db)):
    return list_scholarships(db)
