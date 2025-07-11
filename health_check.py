import bentoml
from pydantic import BaseModel

class Status(BaseModel):
    status: str

@bentoml.service
class HealthCheckService:
    @bentoml.api
    def check(self) -> Status:
        return Status(status="ok")