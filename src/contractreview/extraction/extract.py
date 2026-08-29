"""LLM-based clause extraction. This is the one place in the pipeline
where document variety genuinely requires model reasoning (PROJECT.md
Section 8) -- everything downstream (playbook/rules.py) is a fixed
rules-comparison problem over this extraction's typed output.
"""

from __future__ import annotations

from contractreview.extraction.prompts import SYSTEM_INSTRUCTION, build_extraction_prompt
from contractreview.extraction.schemas import ExtractedContract
from contractreview.llm import LLMClient


def extract_contract(llm: LLMClient, contract_id: str, contract_text: str) -> ExtractedContract:
    prompt = build_extraction_prompt(contract_id, contract_text)
    result = llm.generate_structured(SYSTEM_INSTRUCTION, prompt, ExtractedContract)
    if result.contract_id != contract_id:
        result = result.model_copy(update={"contract_id": contract_id})
    return result
