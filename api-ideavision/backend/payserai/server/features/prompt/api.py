from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from payserai.auth.users import current_admin_user
from payserai.auth.users import current_user
from payserai.db.chat import get_passists_by_ids
from payserai.db.chat import get_prompt_by_id
from payserai.db.chat import get_prompts
from payserai.db.chat import mark_prompt_as_deleted
from payserai.db.chat import upsert_prompt
from payserai.db.engine import get_session
from payserai.db.models import User
from payserai.server.features.prompt.models import CreatePromptRequest
from payserai.server.features.prompt.models import PromptSnapshot
from payserai.utils.logger import setup_logger


# Note: As prompts are fairly innocuous/harmless, there are no protections
# to prevent users from messing with prompts of other users.

logger = setup_logger()

basic_router = APIRouter(prefix="/prompt")


def create_update_prompt(
    prompt_id: int | None,
    create_prompt_request: CreatePromptRequest,
    user: User | None,
    db_session: Session,
) -> PromptSnapshot:
    user_id = user.id if user is not None else None

    passists = (
        list(
            get_passists_by_ids(
                passist_ids=create_prompt_request.passist_ids,
                db_session=db_session,
            )
        )
        if create_prompt_request.passist_ids
        else []
    )

    prompt = upsert_prompt(
        prompt_id=prompt_id,
        user_id=user_id,
        name=create_prompt_request.name,
        description=create_prompt_request.description,
        system_prompt=create_prompt_request.system_prompt,
        task_prompt=create_prompt_request.task_prompt,
        include_citations=create_prompt_request.include_citations,
        datetime_aware=create_prompt_request.datetime_aware,
        passists=passists,
        shared=create_prompt_request.shared,
        db_session=db_session,
    )
    return PromptSnapshot.from_model(prompt)


@basic_router.post("")
def create_passist(
    create_prompt_request: CreatePromptRequest,
    user: User | None = Depends(current_admin_user),
    db_session: Session = Depends(get_session),
) -> PromptSnapshot:
    try:
        return create_update_prompt(
            prompt_id=None,
            create_prompt_request=create_prompt_request,
            user=user,
            db_session=db_session,
        )
    except ValueError as ve:
        logger.exception(ve)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Passist, invalid info.",
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


@basic_router.patch("/{prompt_id}")
def update_prompt(
    prompt_id: int,
    update_prompt_request: CreatePromptRequest,
    user: User | None = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> PromptSnapshot:
    try:
        return create_update_prompt(
            prompt_id=prompt_id,
            create_prompt_request=update_prompt_request,
            user=user,
            db_session=db_session,
        )
    except ValueError as ve:
        logger.exception(ve)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create Passist, invalid info.",
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


@basic_router.delete("/{prompt_id}")
def delete_prompt(
    prompt_id: int,
    user: User | None = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> None:
    mark_prompt_as_deleted(
        prompt_id=prompt_id,
        user_id=user.id if user is not None else None,
        db_session=db_session,
    )


@basic_router.get("")
def list_prompts(
    user: User | None = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> list[PromptSnapshot]:
    user_id = user.id if user is not None else None
    return [
        PromptSnapshot.from_model(prompt)
        for prompt in get_prompts(user_id=user_id, db_session=db_session)
    ]


@basic_router.get("/{prompt_id}")
def get_prompt(
    prompt_id: int,
    user: User | None = Depends(current_user),
    db_session: Session = Depends(get_session),
) -> PromptSnapshot:
    return PromptSnapshot.from_model(
        get_prompt_by_id(
            prompt_id=prompt_id,
            user_id=user.id if user is not None else None,
            db_session=db_session,
        )
    )
