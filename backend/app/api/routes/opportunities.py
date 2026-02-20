import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_matching_service, get_opportunity_service, get_user_service
from app.api.schemas import (
    MatchResponse,
    OpportunityCreate,
    OpportunityDetailResponse,
    OpportunityResponse,
)
from app.core.entities import Opportunity
from app.core.enums import OpportunityType
from app.services.matching_service import MatchingService
from app.services.opportunity_service import OpportunityService
from app.services.user_service import UserService

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.get("", response_model=list[OpportunityResponse])
def list_opportunities(
    svc: OpportunityService = Depends(get_opportunity_service),
    user_svc: UserService = Depends(get_user_service),
):
    opps = svc.get_all()
    result = []
    for o in opps:
        poster = user_svc.get_by_id(o.posted_by)
        result.append(
            OpportunityResponse(
                id=o.id,
                title=o.title,
                description=o.description,
                type=o.type.value,
                posted_by=o.posted_by,
                poster_name=poster.name if poster else "Unknown",
                created_at=o.created_at,
            )
        )
    return result


@router.get("/{opportunity_id}", response_model=OpportunityDetailResponse)
def get_opportunity(
    opportunity_id: str,
    svc: OpportunityService = Depends(get_opportunity_service),
    matching_svc: MatchingService = Depends(get_matching_service),
    user_svc: UserService = Depends(get_user_service),
):
    opp = svc.get_by_id(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    poster = user_svc.get_by_id(opp.posted_by)
    matches = matching_svc.get_matches(opportunity_id)

    match_responses = []
    for m in matches:
        user = user_svc.get_by_id(m.user_id)
        match_responses.append(
            MatchResponse(
                id=m.id,
                opportunity_id=m.opportunity_id,
                user_id=m.user_id,
                user_name=user.name if user else "Unknown",
                user_bio=user.bio if user else "",
                user_skills=user.skills if user else [],
                score=m.score,
                embedding_score=m.embedding_score,
                network_score=m.network_score,
                explanation=m.explanation,
                rank=m.rank,
                created_at=m.created_at,
            )
        )

    return OpportunityDetailResponse(
        opportunity=OpportunityResponse(
            id=opp.id,
            title=opp.title,
            description=opp.description,
            type=opp.type.value,
            posted_by=opp.posted_by,
            poster_name=poster.name if poster else "Unknown",
            created_at=opp.created_at,
        ),
        matches=match_responses,
    )


@router.post("", response_model=OpportunityDetailResponse, status_code=201)
async def create_opportunity(
    body: OpportunityCreate,
    svc: OpportunityService = Depends(get_opportunity_service),
    matching_svc: MatchingService = Depends(get_matching_service),
    user_svc: UserService = Depends(get_user_service),
):
    try:
        opp_type = OpportunityType(body.type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {[t.value for t in OpportunityType]}",
        )

    poster = user_svc.get_by_id(body.posted_by)
    if not poster:
        raise HTTPException(status_code=400, detail="User not found")

    opportunity = Opportunity(
        id=str(uuid.uuid4()),
        title=body.title,
        description=body.description,
        type=opp_type,
        posted_by=body.posted_by,
    )
    created = svc.create(opportunity)

    matches = await matching_svc.find_matches(created)

    match_responses = []
    for m in matches:
        user = user_svc.get_by_id(m.user_id)
        match_responses.append(
            MatchResponse(
                id=m.id,
                opportunity_id=m.opportunity_id,
                user_id=m.user_id,
                user_name=user.name if user else "Unknown",
                user_bio=user.bio if user else "",
                user_skills=user.skills if user else [],
                score=m.score,
                embedding_score=m.embedding_score,
                network_score=m.network_score,
                explanation=m.explanation,
                rank=m.rank,
                created_at=m.created_at,
            )
        )

    return OpportunityDetailResponse(
        opportunity=OpportunityResponse(
            id=created.id,
            title=created.title,
            description=created.description,
            type=created.type.value,
            posted_by=created.posted_by,
            poster_name=poster.name,
            created_at=created.created_at,
        ),
        matches=match_responses,
    )
