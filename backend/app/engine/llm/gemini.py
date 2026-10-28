import json
from typing import List

import httpx

from app.core.logging import logger
from app.engine.llm.base import REVIEW_SYSTEM_PROMPT, BaseLLMProvider, ModelReviewOutput
from app.schemas.finding import FindingBase
from app.schemas.pull_request import DiffSummary


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model or "gemini-1.5-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    async def analyze_diff(
        self, diff_summary: DiffSummary, repo_name: str, pr_title: str
    ) -> List[FindingBase]:
        context = self.build_prompt_context(diff_summary, repo_name, pr_title)

        payload = {
            "system_instruction": {
                "parts": [{"text": REVIEW_SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"Review this PR code diff and output a JSON object adhering to this schema:\n"
                                f"{json.dumps(ModelReviewOutput.model_json_schema())}\n\n"
                                f"{context}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(self.url, json=payload)
                if response.status_code != 200:
                    logger.error(f"Gemini API returned error {response.status_code}: {response.text}")
                    return []

                data = response.json()
                candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed_json = json.loads(candidate_text)
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
                        rule_id="LLM-SUGG-001"
                    ))

                return findings

        except Exception as e:
            logger.error(f"Gemini provider analysis failed: {e}")
            return []
