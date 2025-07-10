import traceback
from fastapi import APIRouter, HTTPException
from ..services.trips_service import TripsService
from ..dto.base_dto import Response
from ..dto.trips_dto import TripsRequest

router = APIRouter(
    prefix="/api/uber-trips",
    tags=["uber"],
    responses={404: {"description": "Not found"}}
)


@router.post("/")
async def get_trips(request:TripsRequest) -> Response:
    print("post trips")
    try:
        
        result = await TripsService().set_trips_json(request.date_code)
        response = Response(status_code=200, status_name="OK", message="Complete", result=result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:      
        traceback.print_exc()
        raise HTTPException(status_code=501, detail=str(e))

    return response