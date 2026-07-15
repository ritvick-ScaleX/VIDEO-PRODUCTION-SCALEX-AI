"""Ad-copy generation prompts across platforms and tones."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are an elite performance copywriter who has written winning ads across "
    "Meta, Google, LinkedIn, and email. You write in the brand's voice, lead with "
    "the strongest hook, keep it native to the platform, and always close with a "
    "clear CTA. Every variation must be meaningfully different in angle. Return "
    "only the requested JSON."
)

PLATFORM_GUIDE = {
    "facebook": "Facebook feed ad. Hook in line 1, 2-4 short punchy paragraphs, emoji sparingly, strong CTA.",
    "instagram": "Instagram caption. Bold hook, line breaks, 3-6 relevant hashtags at the end.",
    "google": "Google Search RSA. headline <= 30 chars, body as a 90-char description. Keyword-aware.",
    "linkedin": "LinkedIn post. Professional, insight-led, credible, no hype. 3-5 lines + CTA.",
    "twitter": "X/Twitter post. Under 260 chars, punchy, one idea, optional 1-2 hashtags.",
    "landing_page": "Landing page hero. headline = value prop, body = subhead + 2-3 benefit lines, CTA = button label.",
    "email": "Marketing email. headline = subject line, body = preview + short persuasive body, CTA = button text.",
    "headline": "A/B test headlines. headline = the headline, body = one-line supporting subhead.",
}

TONE_GUIDE = {
    "luxury": "Aspirational, refined, understated confidence. Premium word choice.",
    "professional": "Clear, credible, benefit-driven, trustworthy.",
    "friendly": "Warm, conversational, upbeat, like a helpful friend.",
    "minimal": "Sparse, confident, every word earns its place.",
}

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "variations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "headline": {"type": "string"},
                    "body": {"type": "string"},
                    "cta": {"type": "string"},
                    "angle": {"type": "string"},
                },
                "required": ["headline", "body", "cta", "angle"],
            },
        }
    },
    "required": ["variations"],
}


def build_prompt(
    brief: dict[str, Any],
    platform: str,
    tone: str,
    count: int,
    instructions: str | None,
) -> str:
    extra = f"\nEXTRA INSTRUCTIONS: {instructions}" if instructions else ""
    return (
        f"Write {count} distinct ad-copy variations.\n\n"
        f"PLATFORM: {platform} — {PLATFORM_GUIDE.get(platform, '')}\n"
        f"TONE: {tone} — {TONE_GUIDE.get(tone, '')}\n\n"
        f"BRAND & PRODUCT BRIEF:\n{json.dumps(brief, indent=2, default=str)}\n"
        f"{extra}\n\n"
        "Each variation needs: headline, body, cta, and a one-word 'angle' label. "
        "Use the brand voice and real product benefits. Make each angle distinct."
    )
