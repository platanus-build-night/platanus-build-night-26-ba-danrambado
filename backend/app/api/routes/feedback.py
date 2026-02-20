import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_ai, get_current_user, get_feedback_repo, get_user_service
from app.api.schemas import FeedbackCreate, FeedbackResponse, ImpressionResponse
from app.core.entities import Feedback, User
from app.services.reputation_service import ReputationService
from app.services.user_service import UserService

router = APIRouter(tags=["feedback"])


@router.post("/api/feedback", response_model=FeedbackResponse, status_code=201)
def create_feedback(
    body: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    feedback_repo=Depends(get_feedback_repo),
    user_svc: UserService = Depends(get_user_service),
):
    if current_user.id == body.to_user_id:
        raise HTTPException(status_code=400, detail="Cannot leave feedback for yourself")

    target = user_svc.get_by_id(body.to_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    valid_types = ["job", "project", "help", "collab", "date"]
    if body.opportunity_type not in valid_types:
        raise HTTPException(
            status_code=400, detail=f"Invalid type. Must be one of: {valid_types}"
        )

    feedback = Feedback(
        id=str(uuid.uuid4()),
        from_user_id=current_user.id,
        to_user_id=body.to_user_id,
        opportunity_type=body.opportunity_type,
        text=body.text,
    )
    created = feedback_repo.create(feedback)
    ReputationService.invalidate_cache(body.to_user_id)

    return FeedbackResponse(
        id=created.id,
        to_user_id=created.to_user_id,
        opportunity_type=created.opportunity_type,
        created_at=created.created_at,
    )


@router.get("/api/users/{user_id}/impression", response_model=ImpressionResponse)
async def get_impression(
    user_id: str,
    feedback_repo=Depends(get_feedback_repo),
    ai=Depends(get_ai),
    user_svc: UserService = Depends(get_user_service),
):
    user = user_svc.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    svc = ReputationService(feedback_repo, ai)
    result = await svc.get_impression(user_id)
    return ImpressionResponse(**result)
