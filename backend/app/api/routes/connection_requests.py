import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_connection_repo,
    get_connection_request_repo,
    get_current_user,
    get_opportunity_service,
    get_user_service,
)
from app.api.schemas import ConnectionRequestCreate, ConnectionRequestResponse
from app.core.entities import Connection, ConnectionRequest, User
from app.core.enums import ConnectionSource
from app.services.opportunity_service import OpportunityService
from app.services.user_service import UserService

router = APIRouter(prefix="/api/connection-requests", tags=["connection-requests"])


def _to_response(
    req: ConnectionRequest,
    user_svc: UserService,
    opp_svc: OpportunityService,
) -> ConnectionRequestResponse:
    from_user = user_svc.get_by_id(req.from_user_id)
    to_user = user_svc.get_by_id(req.to_user_id)
    opp = opp_svc.get_by_id(req.opportunity_id)
    return ConnectionRequestResponse(
        id=req.id,
        from_user_id=req.from_user_id,
        to_user_id=req.to_user_id,
        opportunity_id=req.opportunity_id,
        match_id=req.match_id,
        status=req.status,
        from_user_name=from_user.name if from_user else "",
        to_user_name=to_user.name if to_user else "",
        opportunity_title=opp.title if opp else "",
        created_at=req.created_at,
    )


@router.post("", response_model=ConnectionRequestResponse, status_code=201)
def create_request(
    body: ConnectionRequestCreate,
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
    user_svc: UserService = Depends(get_user_service),
    opp_svc: OpportunityService = Depends(get_opportunity_service),
):
    if current_user.id == body.to_user_id:
        raise HTTPException(status_code=400, detail="Cannot send request to yourself")

    target = user_svc.get_by_id(body.to_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    if req_repo.exists(current_user.id, body.to_user_id, body.opportunity_id):
        raise HTTPException(status_code=400, detail="Request already sent")

    req = ConnectionRequest(
        id=str(uuid.uuid4()),
        from_user_id=current_user.id,
        to_user_id=body.to_user_id,
        opportunity_id=body.opportunity_id,
        match_id=body.match_id,
    )
    created = req_repo.create(req)
    return _to_response(created, user_svc, opp_svc)


@router.get("/incoming", response_model=list[ConnectionRequestResponse])
def get_incoming(
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
    user_svc: UserService = Depends(get_user_service),
    opp_svc: OpportunityService = Depends(get_opportunity_service),
):
    reqs = req_repo.get_incoming(current_user.id)
    return [_to_response(r, user_svc, opp_svc) for r in reqs]


@router.get("/outgoing", response_model=list[ConnectionRequestResponse])
def get_outgoing(
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
    user_svc: UserService = Depends(get_user_service),
    opp_svc: OpportunityService = Depends(get_opportunity_service),
):
    reqs = req_repo.get_outgoing(current_user.id)
    return [_to_response(r, user_svc, opp_svc) for r in reqs]


@router.get("/check")
def check_request(
    opportunity_id: str,
    to_user_id: str,
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
):
    return {"exists": req_repo.exists(current_user.id, to_user_id, opportunity_id)}


@router.get("/by-opportunity/{opportunity_id}", response_model=list[ConnectionRequestResponse])
def get_by_opportunity(
    opportunity_id: str,
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
    user_svc: UserService = Depends(get_user_service),
    opp_svc: OpportunityService = Depends(get_opportunity_service),
):
    opp = opp_svc.get_by_id(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if opp.posted_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the poster can view these requests")
    reqs = req_repo.get_by_opportunity(opportunity_id)
    return [_to_response(r, user_svc, opp_svc) for r in reqs]


@router.post("/{request_id}/accept", response_model=ConnectionRequestResponse)
def accept_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
    conn_repo=Depends(get_connection_repo),
    user_svc: UserService = Depends(get_user_service),
    opp_svc: OpportunityService = Depends(get_opportunity_service),
):
    req = req_repo.get_by_id(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can accept")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request is no longer pending")

    updated = req_repo.update_status(request_id, "accepted")

    conn = Connection(
        id=str(uuid.uuid4()),
        user_a=req.from_user_id,
        user_b=req.to_user_id,
        source=ConnectionSource.MATCH,
    )
    conn_repo.create(conn)

    return _to_response(updated, user_svc, opp_svc)


@router.post("/{request_id}/decline", response_model=ConnectionRequestResponse)
def decline_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    req_repo=Depends(get_connection_request_repo),
    user_svc: UserService = Depends(get_user_service),
    opp_svc: OpportunityService = Depends(get_opportunity_service),
):
    req = req_repo.get_by_id(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can decline")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request is no longer pending")

    updated = req_repo.update_status(request_id, "declined")
    return _to_response(updated, user_svc, opp_svc)
