import json
import logging
from collections import defaultdict

from app.ports.ai_port import AIPort
from app.ports.repositories import FeedbackRepository

logger = logging.getLogger(__name__)

_impression_cache: dict[str, dict] = {}


class ReputationService:
    def __init__(self, feedback_repo: FeedbackRepository, ai: AIPort):
        self._feedback_repo = feedback_repo
        self._ai = ai

    async def get_impression(self, user_id: str) -> dict:
        if user_id in _impression_cache:
            return _impression_cache[user_id]

        feedbacks = self._feedback_repo.get_by_user(user_id)
        if not feedbacks:
            return {"summary": "", "by_context": {}, "feedback_count": 0}

        grouped: dict[str, list[str]] = defaultdict(list)
        for f in feedbacks:
            grouped[f.opportunity_type].append(f.text)

        result = await self._generate_impression(grouped, len(feedbacks))
        _impression_cache[user_id] = result
        return result

    async def _generate_impression(
        self, grouped: dict[str, list[str]], total_count: int
    ) -> dict:
        sections = ""
        for ctx, texts in grouped.items():
            joined = "\n".join(f"- {t}" for t in texts)
            sections += f"\n[{ctx.upper()}] ({len(texts)} feedback entries):\n{joined}\n"

        prompt = f"""You are summarizing anonymous community feedback about a person on Serendip Lab, a platform for intentional connections.

Below are anonymous feedback entries grouped by interaction context (project, collaboration, date, job, help).

FEEDBACK:
{sections}

INSTRUCTIONS:
- Write a warm but honest narrative summary (2-4 sentences) that captures the overall impression
- Do NOT reveal individual feedback verbatim — synthesize themes
- Do NOT assign numerical scores
- If there are different contexts, briefly touch on each
- Be specific about qualities mentioned, avoid generic platitudes
- Write in third person ("People describe them as...")

Also generate a short 1-sentence summary per context category present.

Respond ONLY with JSON (no markdown):
{{
  "summary": "Overall narrative...",
  "by_context": {{
    "project": "One sentence about project interactions...",
    "date": "One sentence about date experiences..."
  }}
}}

Only include context keys that have feedback."""

        try:
            from anthropic import Anthropic
            from app.config import settings

            client = Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            parsed = json.loads(raw)
            return {
                "summary": parsed.get("summary", ""),
                "by_context": parsed.get("by_context", {}),
                "feedback_count": total_count,
            }
        except Exception as e:
            logger.error("Impression generation failed: %s", e)
            all_texts = []
            for texts in grouped.values():
                all_texts.extend(texts)
            return {
                "summary": f"Based on {total_count} community interactions.",
                "by_context": {},
                "feedback_count": total_count,
            }

    @staticmethod
    def invalidate_cache(user_id: str) -> None:
        _impression_cache.pop(user_id, None)
