import json
import logging

import anthropic

from app.config import settings
from app.core.entities import CandidateScore, Opportunity, RankedMatch
from app.ports.ai_port import AIPort

logger = logging.getLogger(__name__)


class AnthropicAdapter(AIPort):
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def rank_and_explain(
        self,
        opportunity: Opportunity,
        candidates: list[CandidateScore],
    ) -> list[RankedMatch]:
        profiles_text = ""
        for i, c in enumerate(candidates, 1):
            shared = ", ".join(c.shared_connections) if c.shared_connections else "none"
            profiles_text += (
                f"\n--- Candidate {i} (ID: {c.user.id}) ---\n"
                f"Name: {c.user.name}\n"
                f"Bio: {c.user.bio}\n"
                f"Skills: {', '.join(c.user.skills)}\n"
                f"Interests: {', '.join(c.user.interests)}\n"
                f"Open to: {', '.join(c.user.open_to)}\n"
                f"Embedding similarity: {c.embedding_score:.2f}\n"
                f"Network proximity: {c.network_score:.2f}\n"
                f"Shared connections: {shared}\n"
            )

        prompt = f"""You are the matching engine for Serendip Lab, a platform that creates intentional connections between people and opportunities. Analyze the opportunity and candidates, then rank them by fit.

OPPORTUNITY:
Title: {opportunity.title}
Description: {opportunity.description}
Type: {opportunity.type.value}

CANDIDATES (pre-filtered by relevance):
{profiles_text}

INSTRUCTIONS:
- Rank ALL candidates from best to worst fit
- For each, write a 1-2 sentence explanation of why they're a good match
- Reference network connections when relevant (e.g., "Connected through Maria who works in sustainability")
- Consider skills alignment, interest overlap, and network proximity
- Be specific about what makes each person a good fit, avoid generic statements

Respond ONLY with a JSON array (no markdown, no explanation outside the array):
[
  {{"user_id": "...", "rank": 1, "score": 0.92, "explanation": "..."}},
  ...
]

Score should be 0-1, reflecting overall match quality. Rank 1 is the best match."""

        try:
            response = self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            parsed = json.loads(raw)
            return [
                RankedMatch(
                    user_id=item["user_id"],
                    rank=item["rank"],
                    score=item["score"],
                    explanation=item["explanation"],
                )
                for item in parsed
            ]
        except Exception as e:
            logger.error("Anthropic ranking failed: %s", e)
            return [
                RankedMatch(
                    user_id=c.user.id,
                    rank=i + 1,
                    score=c.combined_score,
                    explanation=f"Matched based on profile similarity ({c.embedding_score:.0%} skill match).",
                )
                for i, c in enumerate(candidates)
            ]
