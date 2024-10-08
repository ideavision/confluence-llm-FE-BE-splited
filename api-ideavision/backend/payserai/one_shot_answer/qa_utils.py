import math
import re
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterator
from json.decoder import JSONDecodeError
from typing import Optional
from typing import Tuple

import regex

from payserai.chat.models import PayseraiAnswer
from payserai.chat.models import PayseraiAnswerPiece
from payserai.chat.models import PayseraiQuote
from payserai.chat.models import PayseraiQuotes
from payserai.configs.chat_configs import QUOTE_ALLOWED_ERROR_PERCENT
from payserai.configs.constants import MessageType
from payserai.configs.model_configs import GEN_AI_HISTORY_CUTOFF
from payserai.indexing.models import InferenceChunk
from payserai.llm.utils import get_default_llm_token_encode
from payserai.one_shot_answer.models import ThreadMessage
from payserai.prompts.constants import ANSWER_PAT
from payserai.prompts.constants import QUOTE_PAT
from payserai.prompts.constants import UNCERTAINTY_PAT
from payserai.utils.logger import setup_logger
from payserai.utils.text_processing import clean_model_quote
from payserai.utils.text_processing import clean_up_code_blocks
from payserai.utils.text_processing import extract_embedded_json
from payserai.utils.text_processing import shared_precompare_cleanup

logger = setup_logger()


def _extract_answer_quotes_freeform(
    answer_raw: str,
) -> Tuple[Optional[str], Optional[list[str]]]:
    """Splits the model output into an Answer and 0 or more Quote sections.
    Splits by the Quote pattern, if not exist then assume it's all answer and no quotes
    """
    # If no answer section, don't care about the quote
    if answer_raw.lower().strip().startswith(QUOTE_PAT.lower()):
        return None, None

    # Sometimes model regenerates the Answer: pattern despite it being provided in the prompt
    if answer_raw.lower().startswith(ANSWER_PAT.lower()):
        answer_raw = answer_raw[len(ANSWER_PAT) :]

    # Accept quote sections starting with the lower case version
    answer_raw = answer_raw.replace(
        f"\n{QUOTE_PAT}".lower(), f"\n{QUOTE_PAT}"
    )  # Just in case model unreliable

    sections = re.split(rf"(?<=\n){QUOTE_PAT}", answer_raw)
    sections_clean = [
        str(section).strip() for section in sections if str(section).strip()
    ]
    if not sections_clean:
        return None, None

    answer = str(sections_clean[0])
    if len(sections) == 1:
        return answer, None
    return answer, sections_clean[1:]


def _extract_answer_quotes_json(
    answer_dict: dict[str, str | list[str]]
) -> Tuple[Optional[str], Optional[list[str]]]:
    answer_dict = {k.lower(): v for k, v in answer_dict.items()}
    answer = str(answer_dict.get("answer"))
    quotes = answer_dict.get("quotes") or answer_dict.get("quote")
    if isinstance(quotes, str):
        quotes = [quotes]
    return answer, quotes


def _extract_answer_json(raw_model_output: str) -> dict:
    try:
        answer_json = extract_embedded_json(raw_model_output)
    except (ValueError, JSONDecodeError):
        # LLMs get confused when handling the list in the json. Sometimes it doesn't attend
        # enough to the previous { token so it just ends the list of quotes and stops there
        # here, we add logic to try to fix this LLM error.
        answer_json = extract_embedded_json(raw_model_output + "}")

    if "answer" not in answer_json:
        raise ValueError("Model did not output an answer as expected.")

    return answer_json


def separate_answer_quotes(
    answer_raw: str, is_json_prompt: bool = False
) -> Tuple[Optional[str], Optional[list[str]]]:
    """Takes in a raw model output and pulls out the answer and the quotes sections."""
    if is_json_prompt:
        model_raw_json = _extract_answer_json(answer_raw)
        return _extract_answer_quotes_json(model_raw_json)

    return _extract_answer_quotes_freeform(clean_up_code_blocks(answer_raw))


def match_quotes_to_docs(
    quotes: list[str],
    chunks: list[InferenceChunk],
    max_error_percent: float = QUOTE_ALLOWED_ERROR_PERCENT,
    fuzzy_search: bool = False,
    prefix_only_length: int = 100,
) -> PayseraiQuotes:
    payserai_quotes: list[PayseraiQuote] = []
    for quote in quotes:
        max_edits = math.ceil(float(len(quote)) * max_error_percent)

        for chunk in chunks:
            if not chunk.source_links:
                continue

            quote_clean = shared_precompare_cleanup(
                clean_model_quote(quote, trim_length=prefix_only_length)
            )
            chunk_clean = shared_precompare_cleanup(chunk.content)

            # Finding the offset of the quote in the plain text
            if fuzzy_search:
                re_search_str = (
                    r"(" + re.escape(quote_clean) + r"){e<=" + str(max_edits) + r"}"
                )
                found = regex.search(re_search_str, chunk_clean)
                if not found:
                    continue
                offset = found.span()[0]
            else:
                if quote_clean not in chunk_clean:
                    continue
                offset = chunk_clean.index(quote_clean)

            # Extracting the link from the offset
            curr_link = None
            for link_offset, link in chunk.source_links.items():
                # Should always find one because offset is at least 0 and there
                # must be a 0 link_offset
                if int(link_offset) <= offset:
                    curr_link = link
                else:
                    break

            payserai_quotes.append(
                PayseraiQuote(
                    quote=quote,
                    document_id=chunk.document_id,
                    link=curr_link,
                    source_type=chunk.source_type,
                    semantic_identifier=chunk.semantic_identifier,
                    blurb=chunk.blurb,
                )
            )
            break

    return PayseraiQuotes(quotes=payserai_quotes)


def process_answer(
    answer_raw: str,
    chunks: list[InferenceChunk],
    is_json_prompt: bool = True,
) -> tuple[PayseraiAnswer, PayseraiQuotes]:
    """Used (1) in the non-streaming case to process the model output
    into an Answer and Quotes AND (2) after the complete streaming response
    has been received to process the model output into an Answer and Quotes."""
    answer, quote_strings = separate_answer_quotes(answer_raw, is_json_prompt)
    if answer == UNCERTAINTY_PAT or not answer:
        if answer == UNCERTAINTY_PAT:
            logger.debug("Answer matched UNCERTAINTY_PAT")
        else:
            logger.debug("No answer extracted from raw output")
        return PayseraiAnswer(answer=None), PayseraiQuotes(quotes=[])

    logger.info(f"Answer: {answer}")
    if not quote_strings:
        logger.debug("No quotes extracted from raw output")
        return PayseraiAnswer(answer=answer), PayseraiQuotes(quotes=[])
    logger.info(f"All quotes (including unmatched): {quote_strings}")
    quotes = match_quotes_to_docs(quote_strings, chunks)
    logger.info(f"Final quotes: {quotes}")

    return PayseraiAnswer(answer=answer), quotes


def _stream_json_answer_end(answer_so_far: str, next_token: str) -> bool:
    next_token = next_token.replace('\\"', "")
    # If the previous character is an escape token, don't consider the first character of next_token
    # This does not work if it's an escaped escape sign before the " but this is rare, not worth handling
    if answer_so_far and answer_so_far[-1] == "\\":
        next_token = next_token[1:]
    if '"' in next_token:
        return True
    return False


def _extract_quotes_from_completed_token_stream(
    model_output: str, context_chunks: list[InferenceChunk], is_json_prompt: bool = True
) -> PayseraiQuotes:
    answer, quotes = process_answer(model_output, context_chunks, is_json_prompt)
    if answer:
        logger.info(answer)
    elif model_output:
        logger.warning("Answer extraction from model output failed.")

    return quotes


def process_model_tokens(
    tokens: Iterator[str],
    context_docs: list[InferenceChunk],
    is_json_prompt: bool = True,
) -> Generator[PayseraiAnswerPiece | PayseraiQuotes, None, None]:
    """Used in the streaming case to process the model output
    into an Answer and Quotes

    Yields Answer tokens back out in a dict for streaming to frontend
    When Answer section ends, yields dict with answer_finished key
    Collects all the tokens at the end to form the complete model output"""
    quote_pat = f"\n{QUOTE_PAT}"
    # Sometimes worse model outputs new line instead of :
    quote_loose = f"\n{quote_pat[:-1]}\n"
    # Sometime model outputs two newlines before quote section
    quote_pat_full = f"\n{quote_pat}"
    model_output: str = ""
    found_answer_start = False if is_json_prompt else True
    found_answer_end = False
    hold_quote = ""
    for token in tokens:
        model_previous = model_output
        model_output += token

        if not found_answer_start and '{"answer":"' in re.sub(r"\s", "", model_output):
            # Note, if the token that completes the pattern has additional text, for example if the token is "?
            # Then the chars after " will not be streamed, but this is ok as it prevents streaming the ? in the
            # event that the model outputs the UNCERTAINTY_PAT
            found_answer_start = True

            # Prevent heavy cases of hallucinations where model is not even providing a json until later
            if is_json_prompt and len(model_output) > 40:
                logger.warning("LLM did not produce json as prompted")
                found_answer_end = True

            continue

        if found_answer_start and not found_answer_end:
            if is_json_prompt and _stream_json_answer_end(model_previous, token):
                found_answer_end = True
                yield PayseraiAnswerPiece(answer_piece=None)
                continue
            elif not is_json_prompt:
                if quote_pat in hold_quote + token or quote_loose in hold_quote + token:
                    found_answer_end = True
                    yield PayseraiAnswerPiece(answer_piece=None)
                    continue
                if hold_quote + token in quote_pat_full:
                    hold_quote += token
                    continue
            yield PayseraiAnswerPiece(answer_piece=hold_quote + token)
            hold_quote = ""

    logger.debug(f"Raw Model QnA Output: {model_output}")

    yield _extract_quotes_from_completed_token_stream(
        model_output=model_output,
        context_chunks=context_docs,
        is_json_prompt=is_json_prompt,
    )


def simulate_streaming_response(model_out: str) -> Generator[str, None, None]:
    """Mock streaming by generating the passed in model output, character by character"""
    for token in model_out:
        yield token


def combine_message_thread(
    messages: list[ThreadMessage],
    token_limit: int | None = GEN_AI_HISTORY_CUTOFF,
    llm_tokenizer: Callable | None = None,
) -> str:
    """Used to create a single combined message context from threads"""
    message_strs: list[str] = []
    total_token_count = 0
    if llm_tokenizer is None:
        llm_tokenizer = get_default_llm_token_encode()

    for message in reversed(messages):
        if message.role == MessageType.USER:
            role_str = message.role.value.upper()
            if message.sender:
                role_str += " " + message.sender
            else:
                # Since other messages might have the user identifying information
                # better to use Unknown for symmetry
                role_str += " Unknown"
        else:
            role_str = message.role.value.upper()

        msg_str = f"{role_str}:\n{message.message}"
        message_token_count = len(llm_tokenizer(msg_str))

        if (
            token_limit is not None
            and total_token_count + message_token_count > token_limit
        ):
            break

        message_strs.insert(0, msg_str)
        total_token_count += message_token_count

    return "\n\n".join(message_strs)
