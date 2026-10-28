import json
from typing import List

import httpx

from app.core.logging import logger
from app.engine.llm.base import REVIEW_SYSTEM_PROMPT, BaseLLMProvider, ModelReviewOutput
from app.schemas.finding import FindingBase
from app.schemas.pull_request import DiffSummary


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-4o-mini"):
        self.api_key = api_key or "sk-dummy"
        self.base_url = base_url.rstrip("/")
        self.model = model or "gpt-4o-mini"

    async def analyze_diff(
        self, diff_summary: DiffSummary, repo_name: str, pr_title: str
    ) -> List[FindingBase]:
        context = self.build_prompt_context(diff_summary, repo_name, pr_title)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        messages = [
            {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Review this PR code diff and output a JSON object adhering to this schema:\n"
                    f"{json.dumps(ModelReviewOutput.model_json_schema())}\n\n"
                    f"{context}"
                )
            }
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(f"OpenAI/Ollama API returned error {response.status_code}: {response.text}")
                    return []

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed_json = json.loads(content)
                review_output = ModelReviewOutput.model_validate(parsed_json)

                findings: List[FindingBase] = []
                for item in review_output.findings:
                    findings.append(FindingBase(
                        file_path=item.file_path,
                        line_start=item.line_start,
                        line_end=item.line_end,
                        severity=item.severity,
                        category=item.category,
                        title=f"[AI Suggestion] {item.title}",
                        message=item.message,
                        evidence=item.evidence,
                        suggested_remediation=item.suggested_remediation,
                        detection_source="llm_suggestion",
                        confidence="medium",
                        rule_id="LLM-SUGG-002"
                    ))

                return findings

        except Exception as e:
            logger.error(f"OpenAI-compatible provider analysis failed: {e}")
            return []
