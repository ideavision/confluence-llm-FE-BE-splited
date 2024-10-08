from pydantic import BaseModel

from payserai.db.models import Prompt


class CreatePromptRequest(BaseModel):
    name: str
    description: str
    shared: bool
    system_prompt: str
    task_prompt: str
    include_citations: bool = False
    datetime_aware: bool = False
    passist_ids: list[int] | None = None


class PromptSnapshot(BaseModel):
    id: int
    name: str
    shared: bool
    description: str
    system_prompt: str
    task_prompt: str
    include_citations: bool
    datetime_aware: bool
    default_prompt: bool
    # Not including passist info, not needed

    @classmethod
    def from_model(cls, prompt: Prompt) -> "PromptSnapshot":
        if prompt.deleted:
            raise ValueError("Prompt has been deleted")

        return PromptSnapshot(
            id=prompt.id,
            name=prompt.name,
            shared=prompt.user_id is None,
            description=prompt.description,
            system_prompt=prompt.system_prompt,
            task_prompt=prompt.task_prompt,
            include_citations=prompt.include_citations,
            datetime_aware=prompt.datetime_aware,
            default_prompt=prompt.default_prompt,
        )
