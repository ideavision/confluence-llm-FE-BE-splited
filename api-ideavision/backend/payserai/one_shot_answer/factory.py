from payserai.configs.chat_configs import QA_PROMPT_OVERRIDE
from payserai.configs.chat_configs import QA_TIMEOUT
from payserai.db.models import Prompt
from payserai.llm.exceptions import GenAIDisabledException
from payserai.llm.factory import get_default_llm
from payserai.one_shot_answer.interfaces import QAModel
from payserai.one_shot_answer.qa_block import QABlock
from payserai.one_shot_answer.qa_block import QAHandler
from payserai.one_shot_answer.qa_block import SingleMessageQAHandler
from payserai.one_shot_answer.qa_block import WeakLLMQAHandler
from payserai.utils.logger import setup_logger

logger = setup_logger()


def get_question_answer_model(
    prompt: Prompt | None,
    api_key: str | None = None,
    timeout: int = QA_TIMEOUT,
    chain_of_thought: bool = False,
    llm_version: str | None = None,
    qa_model_version: str | None = QA_PROMPT_OVERRIDE,
) -> QAModel | None:
    if chain_of_thought:
        raise NotImplementedError("COT has been disabled")

    system_prompt = prompt.system_prompt if prompt is not None else None
    task_prompt = prompt.task_prompt if prompt is not None else None

    try:
        llm = get_default_llm(
            api_key=api_key,
            timeout=timeout,
            gen_ai_model_version_override=llm_version,
        )
    except GenAIDisabledException:
        return None

    if qa_model_version == "weak":
        qa_handler: QAHandler = WeakLLMQAHandler(
            system_prompt=system_prompt, task_prompt=task_prompt
        )
    else:
        qa_handler = SingleMessageQAHandler(
            system_prompt=system_prompt, task_prompt=task_prompt
        )

    return QABlock(llm=llm, qa_handler=qa_handler)
