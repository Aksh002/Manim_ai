from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100_000)
    quality: str = Field(default="1080p30")
    retry_on_error: bool = True


class RenderResponse(BaseModel):
    job_id: str
    status: str


class RegenerateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100_000)
    instruction: str = Field(min_length=1, max_length=500)


class RegenerateResponse(BaseModel):
    code: str
