from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, LeaderUser
from app.models.transfer import TransferRequest, TransferOffer, Transfer
from app.models.equipment import Equipment
from app.schemas.transfer import (
    TransferRequestCreate,
    TransferRequestResponse,
    TransferRequestRespond,
    TransferOfferCreate,
    TransferOfferResponse,
    TransferConfirmation,
    TransferApproval,
    TransferResponse,
)

router = APIRouter()


# Requests
@router.post("/requests", response_model=TransferRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer_request(
    request_data: TransferRequestCreate,
    db: DB,
    current_user: CurrentUser,
):
    """Create a transfer request"""
    # Validate equipment if direct request
    if request_data.request_type == "direct":
        if not request_data.equipment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="equipment_id required for direct request"
            )

        eq_result = await db.execute(
            select(Equipment).where(Equipment.id == request_data.equipment_id)
        )
        equipment = eq_result.scalar_one_or_none()

        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found"
            )

        if not equipment.is_transferable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipment is not transferable"
            )

        if equipment.current_holder_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have this equipment"
            )

        # Check for existing pending request
        existing = await db.execute(
            select(TransferRequest).where(
                and_(
                    TransferRequest.equipment_id == request_data.equipment_id,
                    TransferRequest.requester_id == current_user.id,
                    TransferRequest.status == "pending"
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending request for this equipment"
            )

    # Determine if approval is needed
    requires_approval = False
    if request_data.request_type == "direct" and request_data.equipment_id:
        eq_result = await db.execute(
            select(Equipment).where(Equipment.id == request_data.equipment_id)
        )
        equipment = eq_result.scalar_one_or_none()
        if equipment:
            # Check equipment or category settings
            if equipment.transfer_requires_approval:
                requires_approval = True
            elif equipment.category and equipment.category.transfer_requires_approval:
                requires_approval = True

    transfer_request = TransferRequest(
        request_type=request_data.request_type,
        equipment_id=request_data.equipment_id,
        category_id=request_data.category_id,
        requester_id=current_user.id,
        holder_id=request_data.holder_id,
        location_id=request_data.location_id,
        location_note=request_data.location_note,
        needed_from=request_data.needed_from,
        needed_until=request_data.needed_until,
        message=request_data.message,
        requires_leader_approval=requires_approval,
        status="requires_approval" if requires_approval else "pending",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    db.add(transfer_request)
    await db.commit()
    await db.refresh(transfer_request)

    # Reload with relationships
    result = await db.execute(
        select(TransferRequest)
        .options(
            selectinload(TransferRequest.equipment),
            selectinload(TransferRequest.category),
            selectinload(TransferRequest.requester),
            selectinload(TransferRequest.holder),
            selectinload(TransferRequest.location),
            selectinload(TransferRequest.offers)
        )
        .where(TransferRequest.id == transfer_request.id)
    )
    transfer_request = result.scalar_one()

    return TransferRequestResponse.model_validate(transfer_request)


@router.get("/requests/sent", response_model=List[TransferRequestResponse])
async def get_sent_requests(
    db: DB,
    current_user: CurrentUser,
    status: Optional[str] = None,
):
    """Get requests sent by current user"""
    query = select(TransferRequest).options(
        selectinload(TransferRequest.equipment),
        selectinload(TransferRequest.category),
        selectinload(TransferRequest.requester),
        selectinload(TransferRequest.holder),
        selectinload(TransferRequest.offers)
    ).where(TransferRequest.requester_id == current_user.id)

    if status:
        query = query.where(TransferRequest.status == status)

    query = query.order_by(TransferRequest.created_at.desc())
    result = await db.execute(query)
    requests = result.scalars().all()

    return [TransferRequestResponse.model_validate(r) for r in requests]


@router.get("/requests/received", response_model=List[TransferRequestResponse])
async def get_received_requests(
    db: DB,
    current_user: CurrentUser,
):
    """Get requests received by current user (as equipment holder)"""
    # Get equipment IDs held by current user
    eq_result = await db.execute(
        select(Equipment.id).where(Equipment.current_holder_id == current_user.id)
    )
    equipment_ids = [row[0] for row in eq_result.fetchall()]

    if not equipment_ids:
        return []

    query = select(TransferRequest).options(
        selectinload(TransferRequest.equipment),
        selectinload(TransferRequest.category),
        selectinload(TransferRequest.requester),
        selectinload(TransferRequest.holder),
        selectinload(TransferRequest.offers)
    ).where(
        and_(
            TransferRequest.equipment_id.in_(equipment_ids),
            TransferRequest.status == "pending"
        )
    ).order_by(TransferRequest.created_at.desc())

    result = await db.execute(query)
    requests = result.scalars().all()

    return [TransferRequestResponse.model_validate(r) for r in requests]


@router.get("/requests/available", response_model=List[TransferRequestResponse])
async def get_available_requests(
    db: DB,
    current_user: CurrentUser,
):
    """Get broadcast requests where current user can offer"""
    query = select(TransferRequest).options(
        selectinload(TransferRequest.equipment),
        selectinload(TransferRequest.category),
        selectinload(TransferRequest.requester),
        selectinload(TransferRequest.offers)
    ).where(
        and_(
            TransferRequest.request_type == "broadcast",
            TransferRequest.status == "pending",
            TransferRequest.requester_id != current_user.id
        )
    ).order_by(TransferRequest.created_at.desc())

    result = await db.execute(query)
    requests = result.scalars().all()

    return [TransferRequestResponse.model_validate(r) for r in requests]


@router.post("/requests/{request_id}/respond")
async def respond_to_request(
    request_id: UUID,
    response_data: TransferRequestRespond,
    db: DB,
    current_user: CurrentUser,
):
    """Accept or reject a transfer request"""
    result = await db.execute(
        select(TransferRequest)
        .options(selectinload(TransferRequest.equipment))
        .where(TransferRequest.id == request_id)
    )
    transfer_request = result.scalar_one_or_none()

    if not transfer_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if transfer_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request is not pending (status: {transfer_request.status})"
        )

    # Verify current user is the holder
    if transfer_request.equipment and transfer_request.equipment.current_holder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the equipment holder"
        )

    if response_data.action == "accept":
        transfer_request.status = "accepted"
        transfer_request.responded_at = datetime.utcnow()

        # Create transfer record
        transfer = Transfer(
            equipment_id=transfer_request.equipment_id,
            request_id=transfer_request.id,
            from_user_id=current_user.id,
            to_user_id=transfer_request.requester_id,
            transfer_type="peer"
        )
        db.add(transfer)

    elif response_data.action == "reject":
        transfer_request.status = "rejected"
        transfer_request.responded_at = datetime.utcnow()
        transfer_request.rejection_reason = response_data.rejection_reason

    await db.commit()

    return {"message": f"Request {response_data.action}ed successfully"}


@router.post("/requests/{request_id}/cancel")
async def cancel_request(
    request_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Cancel a transfer request"""
    result = await db.execute(
        select(TransferRequest).where(TransferRequest.id == request_id)
    )
    transfer_request = result.scalar_one_or_none()

    if not transfer_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if transfer_request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own requests"
        )

    if transfer_request.status not in ["pending", "requires_approval"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel this request"
        )

    transfer_request.status = "cancelled"
    await db.commit()

    return {"message": "Request cancelled successfully"}


# Offers
@router.post("/requests/{request_id}/offer", response_model=TransferOfferResponse)
async def create_offer(
    request_id: UUID,
    offer_data: TransferOfferCreate,
    db: DB,
    current_user: CurrentUser,
):
    """Offer equipment for a broadcast request"""
    # Check request exists and is broadcast
    req_result = await db.execute(
        select(TransferRequest).where(TransferRequest.id == request_id)
    )
    transfer_request = req_result.scalar_one_or_none()

    if not transfer_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if transfer_request.request_type != "broadcast":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only offer on broadcast requests"
        )

    # Check equipment
    eq_result = await db.execute(
        select(Equipment).where(Equipment.id == offer_data.equipment_id)
    )
    equipment = eq_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    if equipment.current_holder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't hold this equipment"
        )

    offer = TransferOffer(
        request_id=request_id,
        offerer_id=current_user.id,
        equipment_id=offer_data.equipment_id,
        message=offer_data.message,
        status="pending"
    )

    db.add(offer)
    await db.commit()
    await db.refresh(offer)

    return TransferOfferResponse.model_validate(offer)


@router.post("/offers/{offer_id}/accept")
async def accept_offer(
    offer_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Accept an offer for your broadcast request"""
    result = await db.execute(
        select(TransferOffer)
        .options(
            selectinload(TransferOffer.request),
            selectinload(TransferOffer.equipment)
        )
        .where(TransferOffer.id == offer_id)
    )
    offer = result.scalar_one_or_none()

    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )

    if offer.request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only accept offers on your requests"
        )

    # Accept this offer
    offer.status = "accepted"

    # Reject other offers
    await db.execute(
        select(TransferOffer)
        .where(
            and_(
                TransferOffer.request_id == offer.request_id,
                TransferOffer.id != offer_id
            )
        )
    )
    # Update status on other offers
    other_offers_result = await db.execute(
        select(TransferOffer).where(
            and_(
                TransferOffer.request_id == offer.request_id,
                TransferOffer.id != offer_id
            )
        )
    )
    for other_offer in other_offers_result.scalars():
        other_offer.status = "rejected"

    # Update request
    offer.request.status = "accepted"
    offer.request.equipment_id = offer.equipment_id
    offer.request.holder_id = offer.offerer_id

    # Create transfer
    transfer = Transfer(
        equipment_id=offer.equipment_id,
        request_id=offer.request_id,
        from_user_id=offer.offerer_id,
        to_user_id=current_user.id,
        transfer_type="peer"
    )
    db.add(transfer)

    await db.commit()

    return {"message": "Offer accepted successfully"}


# Transfer confirmations
@router.post("/{transfer_id}/confirm-handover")
async def confirm_handover(
    transfer_id: UUID,
    confirmation: TransferConfirmation,
    db: DB,
    current_user: CurrentUser,
):
    """Confirm handover (from giver's side)"""
    result = await db.execute(
        select(Transfer).where(Transfer.id == transfer_id)
    )
    transfer = result.scalar_one_or_none()

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )

    if transfer.from_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the giver in this transfer"
        )

    transfer.from_confirmed_at = datetime.utcnow()
    transfer.condition_at_transfer = confirmation.condition
    transfer.photo_url = confirmation.photo_url
    transfer.notes = confirmation.notes
    if confirmation.gps_lat:
        transfer.transfer_gps_lat = confirmation.gps_lat
        transfer.transfer_gps_lng = confirmation.gps_lng

    await db.commit()

    return {"message": "Handover confirmed"}


@router.post("/{transfer_id}/confirm-receipt")
async def confirm_receipt(
    transfer_id: UUID,
    confirmation: TransferConfirmation,
    db: DB,
    current_user: CurrentUser,
):
    """Confirm receipt (from receiver's side)"""
    result = await db.execute(
        select(Transfer)
        .options(selectinload(Transfer.equipment))
        .where(Transfer.id == transfer_id)
    )
    transfer = result.scalar_one_or_none()

    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )

    if transfer.to_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the receiver in this transfer"
        )

    transfer.to_confirmed_at = datetime.utcnow()

    # If both confirmed, complete the transfer
    if transfer.from_confirmed_at and transfer.to_confirmed_at:
        # Update equipment holder
        equipment = transfer.equipment
        equipment.current_holder_id = transfer.to_user_id

        # Update request if exists
        if transfer.request_id:
            req_result = await db.execute(
                select(TransferRequest).where(TransferRequest.id == transfer.request_id)
            )
            request = req_result.scalar_one_or_none()
            if request:
                request.status = "completed"
                request.completed_at = datetime.utcnow()

    await db.commit()

    return {"message": "Receipt confirmed"}


@router.get("/history", response_model=List[TransferResponse])
async def get_transfer_history(
    db: DB,
    current_user: CurrentUser,
    equipment_id: Optional[UUID] = None,
):
    """Get transfer history"""
    query = select(Transfer).options(
        selectinload(Transfer.equipment),
        selectinload(Transfer.from_user),
        selectinload(Transfer.to_user),
        selectinload(Transfer.location)
    ).where(
        or_(
            Transfer.from_user_id == current_user.id,
            Transfer.to_user_id == current_user.id
        )
    )

    if equipment_id:
        query = query.where(Transfer.equipment_id == equipment_id)

    query = query.order_by(Transfer.created_at.desc())
    result = await db.execute(query)
    transfers = result.scalars().all()

    return [TransferResponse.model_validate(t) for t in transfers]


# Approval (for leaders)
@router.get("/pending-approval", response_model=List[TransferRequestResponse])
async def get_pending_approvals(
    db: DB,
    current_user: LeaderUser,
):
    """Get transfers pending approval"""
    # Get team member IDs
    from app.models.user import User
    team_result = await db.execute(
        select(User.id).where(User.manager_id == current_user.id)
    )
    team_ids = [row[0] for row in team_result.fetchall()]
    team_ids.append(current_user.id)

    query = select(TransferRequest).options(
        selectinload(TransferRequest.equipment),
        selectinload(TransferRequest.requester),
        selectinload(TransferRequest.holder)
    ).where(
        and_(
            TransferRequest.status == "requires_approval",
            or_(
                TransferRequest.requester_id.in_(team_ids),
                TransferRequest.holder_id.in_(team_ids)
            )
        )
    ).order_by(TransferRequest.created_at.desc())

    result = await db.execute(query)
    requests = result.scalars().all()

    return [TransferRequestResponse.model_validate(r) for r in requests]


@router.post("/requests/{request_id}/approve")
async def approve_request(
    request_id: UUID,
    approval: TransferApproval,
    db: DB,
    current_user: LeaderUser,
):
    """Approve or reject a transfer request"""
    result = await db.execute(
        select(TransferRequest).where(TransferRequest.id == request_id)
    )
    transfer_request = result.scalar_one_or_none()

    if not transfer_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if transfer_request.status != "requires_approval":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request does not require approval"
        )

    if approval.approved:
        transfer_request.status = "pending"
        transfer_request.approved_by = current_user.id
        transfer_request.approved_at = datetime.utcnow()
    else:
        transfer_request.status = "rejected"
        transfer_request.rejection_reason = approval.notes

    await db.commit()

    return {"message": "Request " + ("approved" if approval.approved else "rejected")}
