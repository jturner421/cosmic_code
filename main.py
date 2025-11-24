import uvicorn
from fastapi import FastAPI, HTTPException

from db.session import Database
from domain.model import OrderLine, OutOfStockError
from repository.repositories import BatchRepository
from service_layer.services import InvalidSku, allocate

app = FastAPI(title="CosmicPython", version="1.0.0")


@app.post("/allocate", status_code=201)
def allocate_endpoint(orderline: OrderLine):
    session = Database().session
    repo = BatchRepository(session)
    try:
        batchref = allocate(orderline, repo, session)

    except (OutOfStockError, InvalidSku) as e:
        raise HTTPException(status_code=400, detail=str(e))  # noqa: B904
    return {"batchref": batchref}


@app.get("/")
def index():
    return {"message": "Hello World"}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
