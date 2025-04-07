import logging
from functools import partial

from fastapi import FastAPI

from api.helpers import custom_openapi
from api.notifications import notifications_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(
    notifications_router, prefix="/notifications", tags=["notifications"]
)

app.openapi = partial(custom_openapi, app)  # type: ignore[method-assign]
