from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class APIError(HTTPException):
    def __init__(self, status: int, code: str, message: str, errors=None):
        super().__init__(status_code=status, detail={
            "code": code,
            "message": message,
            **({"errors": errors} if errors else {}),
        })

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, exc: APIError):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(p) for p in e["loc"][1:]),
            "issue": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(status_code=400, content={
            "code": "validation_failed",
            "message": "Some fields are invalid",
            "errors": errors
        })