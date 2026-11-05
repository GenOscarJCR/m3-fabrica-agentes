"""Punto de entrada de la API de gestión de empleados."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from database import Base, engine
from routers import empleados, vacaciones

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestión de empleados")

app.include_router(empleados.router)
app.include_router(vacaciones.router)


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    primer_error = exc.errors()[0]
    campo = primer_error["loc"][-1]
    return JSONResponse(
        status_code=422,
        content={"detail": f"El campo {campo} es inválido"},
    )


@app.get("/api/salud")
def salud() -> dict[str, str]:
    return {"estado": "ok"}
