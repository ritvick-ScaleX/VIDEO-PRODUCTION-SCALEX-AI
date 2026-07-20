"""Script generation from a selected idea — Hinglish, Indian audience."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are an award-winning short-form ad director and scriptwriter for the Indian "
    "market (think scroll-stopping Instagram Reels and YouTube Shorts). You write "
    "natural Hindi-English (Hinglish) spoken lines in Roman script that a real Indian "
    "presenter would say to camera — warm, punchy, culturally native, never translated-"
    "sounding. Craft rules: (1) open with a 1.5-second pattern-interrupt HOOK that names "
    "the viewer's problem or desire; (2) one clear idea per scene, spoken lines short "
    "enough to say in the scene's duration; (3) show the product in use, not just "
    "described; (4) build to a single, specific call-to-action; (5) each scene's 'visual' "
    "must be a concrete, filmable camera direction (shot size, action, setting, product "
    "placement) a Veo model can render. Keep it authentic and high-energy. Return only "
    "the requested JSON."
)

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "script": {"type": "string"},
        "voiceover": {"type": "string"},
        "character": {"type": "string"},
        "voice": {"type": "string"},
        "setting": {"type": "string"},
        "storyboard": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "scene": {"type": "string"},
                    "visual": {"type": "string"},
                    "voiceover": {"type": "string"},
                    "on_screen_text": {"type": "string"},
                    "duration": {"type": "string"},
                },
                "required": ["scene", "visual", "voiceover", "on_screen_text", "duration"],
            },
        },
        "captions": {"type": "array", "items": {"type": "string"}},
        "transitions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["script", "voiceover", "character", "voice", "setting", "storyboard", "captions", "transitions"],
}

_DURATION_HINT = {
    "15s": "15 seconds, 3-4 fast scenes",
    "30s": "30 seconds, 4-6 scenes",
    "60s": "60 seconds, 6-8 scenes",
    "reel": "~25 seconds vertical Reel, punchy",
    "short": "~30 seconds vertical Short, hook-first",
    "story": "~15 seconds vertical Story, single message",
}


def build_prompt(brief: dict[str, Any], idea: dict[str, Any], req: dict[str, Any]) -> str:
    duration = req.get("duration", "reel")
    extra = f"\nEXTRA NOTES: {req.get('instructions')}" if req.get("instructions") else ""
    return (
        f"Write the video script for this chosen concept. Target: "
        f"{_DURATION_HINT.get(duration, duration)}.\n\n"
        f"CHOSEN IDEA:\n{json.dumps(idea, indent=2, default=str)}\n\n"
        f"BRAND & PRODUCT:\n{json.dumps(brief, indent=2, default=str)}\n"
        f"{extra}\n\n"
        "The spoken lines ('voiceover' and each scene's voiceover) must be in "
        "natural Hinglish (Hindi + English mixed, Roman script), as an Indian "
        "presenter would speak. Start with a strong hook in the first scene. Each "
        "'visual' is a concrete camera/staging direction (shot size, presenter action, "
        "real setting, where the product appears) — filmable as-is. Deliver: a full "
        "script; one combined voiceover track that flows naturally end-to-end; a "
        "storyboard (scene, visual, voiceover, on_screen_text, duration); punchy "
        "per-scene captions; and smooth transitions that fit the pacing. "
        "CONSISTENCY (critical): also return 'character' — ONE detailed, reusable "
        "description of the single presenter who appears in EVERY scene, CHOSEN TO FIT this "
        "product, its category and its target audience (pick the right gender, age, look, "
        "styling and vibe for who actually buys this product — e.g. a men's grooming product "
        "gets a male presenter, a bridal product a bride-age woman). Describe gender, age, "
        "complexion, hair style & colour, exact outfit with colours, overall vibe — and "
        "'setting' — ONE primary location + light description (time of day, palette). "
        "Every scene features that SAME character (face/hair/build never change). Use the "
        "primary setting for nearly all scenes; at most ONE later scene may move to a "
        "different location for a deliberate transformation/payoff beat — if so, name the "
        "new location explicitly in that scene's 'visual'. "
        "Also return 'voice' — ONE fixed voice for the whole ad, CHOSEN TO FIT the presenter "
        "and target audience (gender, age, accent, tone, pace) so every scene is spoken in the "
        "SAME single voice, never a different voice per scene. Match the voice gender to the "
        "presenter. Prefer a natural Indian Hinglish voice. "
        "SETTING: default to an authentic, real Indian home / everyday Indian location "
        "(lived-in, believable) rather than a generic studio or artificial AI-looking backdrop."
    )
