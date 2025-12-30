from pydantic import BaseModel, Field, model_validator
from typing import Optional


class Message(BaseModel):
    speaker: str
    content: str
    start_time: float = Field(ge=0)
    end_time: float = Field(ge=0)

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time < self.start_time:
            raise ValueError("end_time doit être >= start_time")
        return self


class Context(BaseModel):
    domain: str = ""
    participants: dict[str, str] = Field(default_factory=dict)
    glossary: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)


class Metadata(BaseModel):
    duration: float = Field(gt=0)
    date: str
    source: str


class Transcript(BaseModel):
    transcript_id: str
    metadata: Metadata
    messages: list[Message]
    context: Optional[Context] = None
