from collections.abc import Iterator
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from payserai.configs.constants import DocumentSource
from payserai.search.models import QueryFlow
from payserai.search.models import RetrievalDocs
from payserai.search.models import SearchResponse
from payserai.search.models import SearchType


class LlmDoc(BaseModel):
    """This contains the minimal set information for the LLM portion including citations"""

    document_id: str
    content: str
    semantic_identifier: str
    source_type: DocumentSource
    updated_at: datetime | None
    link: str | None


# First chunk of info for streaming QA
class QADocsResponse(RetrievalDocs):
    rephrased_query: str | None = None
    predicted_flow: QueryFlow | None
    predicted_search: SearchType | None
    applied_source_filters: list[DocumentSource] | None
    applied_time_cutoff: datetime | None
    recency_bias_multiplier: float

    def dict(self, *args: list, **kwargs: dict[str, Any]) -> dict[str, Any]:  # type: ignore
        initial_dict = super().dict(*args, **kwargs)  # type: ignore
        initial_dict["applied_time_cutoff"] = (
            self.applied_time_cutoff.isoformat() if self.applied_time_cutoff else None
        )
        return initial_dict


# Second chunk of info for streaming QA
class LLMRelevanceFilterResponse(BaseModel):
    relevant_chunk_indices: list[int]


class PayseraiAnswerPiece(BaseModel):
    # A small piece of a complete answer. Used for streaming back answers.
    answer_piece: str | None  # if None, specifies the end of an Answer


# An intermediate representation of citations, later translated into
# a mapping of the citation [n] number to SearchDoc
class CitationInfo(BaseModel):
    citation_num: int
    document_id: str


class StreamingError(BaseModel):
    error: str


class PayseraiQuote(BaseModel):
    # This is during inference so everything is a string by this point
    quote: str
    document_id: str
    link: str | None
    source_type: str
    semantic_identifier: str
    blurb: str


class PayseraiQuotes(BaseModel):
    quotes: list[PayseraiQuote]


class PayseraiAnswer(BaseModel):
    answer: str | None


class QAResponse(SearchResponse, PayseraiAnswer):
    quotes: list[PayseraiQuote] | None
    predicted_flow: QueryFlow
    predicted_search: SearchType
    eval_res_valid: bool | None = None
    llm_chunks_indices: list[int] | None = None
    error_msg: str | None = None


AnswerQuestionReturn = tuple[PayseraiAnswer, PayseraiQuotes]


AnswerQuestionStreamReturn = Iterator[
    PayseraiAnswerPiece | PayseraiQuotes | StreamingError
]


class LLMMetricsContainer(BaseModel):
    prompt_tokens: int
    response_tokens: int
