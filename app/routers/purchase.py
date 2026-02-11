from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    ChangeBreakdownResponse,
    PurchaseRequest,
    PurchaseResponse,
)
from app.services import purchase_service

router = APIRouter()


@router.post("/purchase", response_model=PurchaseResponse)
@router.post("/purchase", response_model=PurchaseResponse)
def purchase(data: PurchaseRequest, db: Session = Depends(get_db)):
    try:
        result = purchase_service.purchase(db, data.item_id, data.cash_inserted)
        return PurchaseResponse(**result)

    except ValueError as e:
        error = e.args[0]

        if error == "item_not_found":
            raise HTTPException(status_code=404, detail="Item not found")

        if error == "out_of_stock":
            raise HTTPException(
                status_code=400,
                detail={"error": "Item out of stock"},
            )

        if error == "invalid_cash_amount":
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid cash amount"},
            )

        if error == "unsupported_denomination":
            raise HTTPException(
                status_code=400,
                detail={"error": "Unsupported denomination"},
            )

        if error == "insufficient_cash":
            required = e.args[1]
            inserted = e.args[2]
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Insufficient cash",
                    "required": required,
                    "inserted": inserted,
                },
            )

        raise



@router.get("/purchase/change-breakdown", response_model=ChangeBreakdownResponse)
def change_breakdown(change: int = Query(..., ge=0)):
    try:
        return purchase_service.change_breakdown(change)
    except ValueError as e:
        if e.args[0] == "cannot_make_exact_change":
            raise HTTPException(
                status_code=400,
                detail="Cannot make exact change with supported denominations",
            )
        raise

