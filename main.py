from fastapi import FastAPI
from fastapi.routing import APIRoute

from routes.assessment import router as assessment_router
from routes.simplification import router as simplification_router

from models import assessment
from database import engine

app = FastAPI()
# models.Base.metadata.create_all(bind=engine)

app.include_router(assessment_router)
app.include_router(simplification_router)


def list_routes(app: FastAPI):
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods),
            })
    return routes


if __name__ == "__main__":
    import uvicorn

    print(list_routes(app))
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
