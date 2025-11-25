import logging
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Initialize ORM mapping BEFORE importing domain models
from db.orm import perform_mapping

perform_mapping()

from api.dependencies import get_batch_repository, get_session
from api.schemas import OrderLineInput
from domain.model import OrderLine, OutOfStockError
from repository.repositories import BatchRepository
from service_layer.services import InvalidSku, allocate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="CosmicPython", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.exception("Server error")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},  # Expose actual error message
    )


@app.post("/allocate", status_code=201)
def allocate_endpoint(
    orderline_input: OrderLineInput,
    repo: Annotated[BatchRepository, Depends(get_batch_repository)],
    session: Annotated[Session, Depends(get_session)],
) -> dict[str, str]:
    # Create domain OrderLine from API input
    orderline = OrderLine(
        orderid=orderline_input.orderid,
        sku=orderline_input.sku,
        qty=orderline_input.qty,
    )
    try:
        batchref = allocate(orderline, repo, session)
    except (OutOfStockError, InvalidSku) as e:
        raise HTTPException(status_code=400, detail=str(e))  # noqa: B904
    return {"batchref": batchref}


@app.get("/")
def index():
    return {"message": "Hello World"}


def main():
    uvicorn.run(app, host="0.0.0.0", port=7000, reload=True)


if __name__ == "__main__":
    main()
