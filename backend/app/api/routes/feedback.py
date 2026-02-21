import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_ai,
    get_connection_request_repo,
    get_current_user,
    get_feedback_repo,
    get_opportunity_service,
    get_user_service,
)
from app.api.schemas import (
    ExperienceResponse,
    ExperiencesResponse,
    FeedbackCreate,
    FeedbackResponse,
    ImpressionResponse,
)
from app.core.entities import Feedback, User
from app.services.opportunity_service import OpportunityService
from app.services.reputation_service import ReputationService
from app.services.user_service import UserService

router = APIRouter(tags=["feedback"])


@router.get("/api/feedback/experiences/{to_user_id}", response_model=ExperiencesResponse)
def get_experiences(
    to_user_id: str,
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
    feedback_repo=Depends(get_feedback_repo),
    opp_svc: OpportunityService = Depends(get_opportunity_service),
):
    if current_user.id == to_user_id:
        return ExperiencesResponse(experiences=[])

    reqs = req_repo.get_accepted_between(current_user.id, to_user_id)
    seen_opp_ids: set[str] = set()
    experiences: list[ExperienceResponse] = []

    for req in reqs:
        if req.opportunity_id in seen_opp_ids:
            continue
        seen_opp_ids.add(req.opportunity_id)
        opp = opp_svc.get_by_id(req.opportunity_id)
        if not opp:
            continue
        opp_type = opp.type.value
        if feedback_repo.has_feedback(current_user.id, to_user_id, opp_type):
            continue
        experiences.append(
            ExperienceResponse(
                opportunity_id=opp.id,
                opportunity_type=opp_type,
                opportunity_title=opp.title,
            )
        )

    return ExperiencesResponse(experiences=experiences)


@router.get("/api/feedback/can-leave/{user_id}")
def can_leave_feedback(
    user_id: str,
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
):
    if current_user.id == user_id:
        return {"allowed": False}
    return {"allowed": req_repo.has_accepted_between(current_user.id, user_id)}


@router.post("/api/feedback", response_model=FeedbackResponse, status_code=201)
def create_feedback(
    body: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    feedback_repo=Depends(get_feedback_repo),
    req_repo=Depends(get_connection_request_repo),
    user_svc: UserService = Depends(get_user_service),
):
    if current_user.id == body.to_user_id:
        raise HTTPException(status_code=400, detail="Cannot leave feedback for yourself")

    target = user_svc.get_by_id(body.to_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    if not req_repo.has_accepted_between(current_user.id, body.to_user_id):
        raise HTTPException(
            status_code=403,
            detail="You can only leave feedback after completing an interaction",
        )

    valid_types = ["job", "project", "help", "collab", "date", "fun"]
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
