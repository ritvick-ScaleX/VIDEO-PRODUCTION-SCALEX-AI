"""Deterministic mock content used when the AI provider is not configured.

These keep the whole product explorable offline and act as the fallback if a
live call fails. They pull real product/brand facts from the brief so the demo
content reads like it belongs to the project.
"""
from __future__ import annotations

from typing import Any


def _name(brief: dict[str, Any]) -> str:
    return brief.get("product_name") or "your product"


def _benefits(brief: dict[str, Any]) -> list[str]:
    return brief.get("benefits") or [
        "Save hours every week",
        "Look effortlessly premium",
        "Get results you can measure",
    ]


def mock_brand(signals: dict[str, Any]) -> dict[str, Any]:
    name = signals.get("name") or signals.get("site_name") or signals.get("title") or "Your Brand"
    desc = signals.get("description") or signals.get("hero_content") or ""
    return {
        "name": name,
        "tagline": (signals.get("tagline") or signals.get("hero_content") or f"{name} — made to stand out")[:80],
        "mission": (desc or f"{name} builds products people love and trust.")[:200],
        "brand_voice": "Confident, warm, and modern — speaks clearly and respects the customer's time.",
        "writing_style": "Short, active sentences. Benefit-led. Minimal jargon, occasional playful line.",
        "target_audience": "Quality-conscious buyers who research before purchase and value good design.",
    }


def mock_analysis(product: dict[str, Any]) -> dict[str, Any]:
    name = product.get("product_name") or "the product"
    benefits = product.get("benefits") or [
        "Effortless everyday performance",
        "Premium quality that lasts",
        "Designed around real needs",
    ]
    return {
        "brand_voice": f"Confident, warm, and benefit-led — {name} speaks like a trusted expert who respects the buyer's time.",
        "customer_persona": f"Ambitious 28-45 year-olds who value quality and their time. They research before buying and are drawn to brands that feel considered and premium. They'd happily pay more for {name} if it removes friction from their day.",
        "pain_points": [
            "Existing options feel cheap or overcomplicated",
            "Too much time wasted on things that should be simple",
            "Hard to trust marketing claims",
            "Worried about buyer's remorse",
        ],
        "benefits": benefits,
        "marketing_angles": [
            "The premium upgrade you deserve",
            "Time-back: reclaim your day",
            "Trusted by people like you",
            "The last one you'll ever need",
        ],
        "offers": [
            "Launch offer: 20% off your first order",
            "Free shipping + 30-day happiness guarantee",
            "Bundle & save",
        ],
        "hooks": [
            f"Everyone's switching to {name} — here's why.",
            "This changed my entire routine.",
            "I was skeptical. Then I tried it.",
            "The 30-second upgrade I wish I'd made sooner.",
            "Stop settling for 'good enough.'",
        ],
        "cta_suggestions": [
            "Shop now",
            "Claim your offer",
            "See it in action",
            "Get started today",
        ],
        "emotional_triggers": ["Aspiration", "Belonging", "Relief", "Confidence", "FOMO"],
        "ingredients": [],
        "usp": f"{name} delivers premium results without the premium hassle — designed to just work.",
        "strategy_summary": f"Lead with the aspirational upgrade angle for cold audiences, then retarget with social proof and the launch offer. Keep the voice confident and warm. {name}'s edge is friction-free premium quality — make every creative feel effortless and trustworthy.",
    }


def mock_copy(
    brief: dict[str, Any], platform: str, tone: str, count: int
) -> dict[str, Any]:
    name = _name(brief)
    benefits = _benefits(brief)
    cta = brief.get("cta") or "Shop now"
    angles = ["aspiration", "problem-solution", "social-proof", "urgency", "value", "story"]
    templates = [
        {
            "headline": f"Meet {name} — the upgrade you didn't know you needed",
            "body": f"{benefits[0]}. Thousands have already made the switch. It's the {tone} choice that just works.",
            "cta": cta,
        },
        {
            "headline": f"Tired of settling? {name} changes that.",
            "body": f"Say goodbye to compromise. {benefits[min(1, len(benefits)-1)]} — all in one place. Try it risk-free today.",
            "cta": "Claim your offer",
        },
        {
            "headline": f"Why people can't stop talking about {name}",
            "body": f"⭐⭐⭐⭐⭐ \"Genuinely the best purchase I've made this year.\" {benefits[-1]}. See what the hype is about.",
            "cta": "See reviews",
        },
        {
            "headline": f"Only a few left — {name} is selling fast",
            "body": f"Our launch offer ends soon. {benefits[0]} at a price that won't last. Don't miss it.",
            "cta": "Get yours before it's gone",
        },
        {
            "headline": f"The smart way to {benefits[0].lower()}",
            "body": f"{name} was built to do one thing exceptionally well. No fluff, no gimmicks — just results.",
            "cta": cta,
        },
        {
            "headline": f"From skeptic to obsessed in one week with {name}",
            "body": f"\"I almost didn't buy it. Now I recommend it to everyone.\" That's the {name} effect.",
            "cta": "Start your story",
        },
    ]
    variations = []
    for i in range(min(count, len(templates))):
        v = dict(templates[i])
        v["angle"] = angles[i % len(angles)]
        variations.append(v)
    return {"variations": variations}


def mock_ugc(brief: dict[str, Any], req: dict[str, Any]) -> dict[str, Any]:
    name = _name(brief)
    benefits = _benefits(brief)
    return {
        "hook": f"Okay I need to talk about {name} because I'm genuinely obsessed…",
        "script": (
            f"Okay I need to talk about {name} because I'm genuinely obsessed. "
            f"So I used to struggle with this every single day — {benefits[0].lower()} felt impossible. "
            f"Then I found {name}. [hold it up to camera] Look at this. "
            f"Within a week, everything changed. {benefits[-1]}. "
            f"Honestly, if you've been on the fence, this is your sign. Link's right here."
        ),
        "camera_directions": [
            "Handheld selfie, eye-level, natural window light",
            "Cut to close-up of the product in hand",
            "Quick B-roll montage of it in use",
            "Return to talking-head for the CTA, lean in slightly",
        ],
        "scene_breakdown": [
            {"scene": "Hook", "action": "Talking to camera, excited", "dialogue": f"I need to talk about {name}…", "duration": "0-3s"},
            {"scene": "Problem", "action": "Relatable frustration face", "dialogue": "I used to struggle with this daily…", "duration": "3-8s"},
            {"scene": "Reveal", "action": "Show product to camera", "dialogue": f"Then I found {name}.", "duration": "8-14s"},
            {"scene": "Proof", "action": "B-roll of it working", "dialogue": f"{benefits[-1]}.", "duration": "14-22s"},
            {"scene": "CTA", "action": "Lean in, point down", "dialogue": "This is your sign — link below.", "duration": "22-28s"},
        ],
        "b_roll": [
            "Unboxing close-up",
            "Product in daily-use setting",
            "Before/after side-by-side",
            "Hands interacting with the product",
        ],
        "cta": "Tap the link in bio and use my code to save on your first order!",
    }


def mock_video(brief: dict[str, Any], req: dict[str, Any]) -> dict[str, Any]:  # noqa: C901
    name = _name(brief)
    benefits = _benefits(brief)
    return {
        "character": "A friendly Indian presenter in their late 20s, casual smart outfit, warm energy.",
        "voice": "A warm, natural female Indian voice, mid-20s, friendly and clear, Hinglish delivery.",
        "setting": "A real, lived-in Indian home, natural daylight.",
        "script": (
            f"[Upbeat] Introducing {name}. {benefits[0]}. "
            f"Built for people who refuse to settle. {benefits[-1]}. "
            f"Join thousands who've already upgraded. {name} — {brief.get('tagline') or 'better, by design.'}"
        ),
        "voiceover": (
            f"This is {name}. The upgrade you've been waiting for. "
            f"{benefits[0]}, without the hassle. Try it today."
        ),
        "storyboard": [
            {"scene": "Open", "visual": "Slow push-in on product, dramatic lighting", "voiceover": f"This is {name}.", "on_screen_text": name, "duration": "0-4s"},
            {"scene": "Problem", "visual": "Quick cuts of everyday frustration", "voiceover": "Tired of settling?", "on_screen_text": "Enough.", "duration": "4-9s"},
            {"scene": "Solution", "visual": "Product hero shot, rotating", "voiceover": benefits[0], "on_screen_text": benefits[0], "duration": "9-16s"},
            {"scene": "Proof", "visual": "Happy customers, 5-star overlays", "voiceover": "Loved by thousands.", "on_screen_text": "⭐ 4.9/5", "duration": "16-24s"},
            {"scene": "CTA", "visual": "Logo + offer, button pulse", "voiceover": "Get yours today.", "on_screen_text": brief.get("cta") or "Shop now", "duration": "24-30s"},
        ],
        "captions": [
            f"This is {name}.",
            "Tired of settling?",
            benefits[0],
            "Loved by thousands ⭐ 4.9/5",
            brief.get("cta") or "Shop now",
        ],
        "transitions": ["Push in", "Hard cut", "Whip pan", "Cross dissolve", "Zoom out"],
    }


def mock_ideas(brief: dict[str, Any], user_prompt: str, count: int) -> dict[str, Any]:
    name = _name(brief)
    benefits = _benefits(brief)
    directions = [
        {
            "kind": "image",
            "title": "Golden Hour Hero",
            "angle": "product-in-its-world",
            "description": f"{name} staged alone in its natural habitat — warm golden light, real props, product razor-sharp as the sole hero. No people.",
            "hook": f"Meet {name}.",
        },
        {
            "kind": "image",
            "title": "Ingredient Story",
            "angle": "ingredient-hero",
            "description": f"Macro flat-lay of {name} surrounded by its key ingredients, editorial styling, clean negative space for a headline.",
            "hook": "What's inside matters.",
        },
        {
            "kind": "image",
            "title": "Real-Life Moment",
            "angle": "lifestyle",
            "description": f"A real person mid-routine with {name} — candid, natural skin texture, documentary light. Feels like a photo, not an ad.",
            "hook": "Your everyday, upgraded.",
        },
        {
            "kind": "video",
            "title": "Problem → Hero",
            "angle": "pain-to-solution",
            "description": f"Open on the everyday frustration your buyer feels, then reveal {name} as the fix. {benefits[0]}.",
            "hook": f"Tired of settling? {name} changes everything.",
        },
        {
            "kind": "video",
            "title": "Day in the Life",
            "angle": "lifestyle",
            "description": f"Follow a relatable creator through their day using {name} — natural, aspirational, real.",
            "hook": f"POV: your day just got upgraded with {name}.",
        },
        {
            "kind": "video",
            "title": "Honest Review",
            "angle": "authenticity",
            "description": f"A creator gives a candid, first-person take on {name}. Builds trust fast.",
            "hook": "I was skeptical… but then I tried this.",
        },
        {
            "kind": "video",
            "title": "Social Proof Wall",
            "angle": "reviews",
            "description": f"Rapid-fire real reactions + 5-star callouts. {benefits[-1]}.",
            "hook": f"Everyone's switching to {name} — here's why.",
        },
        {
            "kind": "video",
            "title": "Bold Claim",
            "angle": "provocation",
            "description": f"Lead with a confident, category-defining claim about {name} and back it up.",
            "hook": f"This is the only {name} you'll ever need.",
        },
        {
            "kind": "video",
            "title": "Before / After",
            "angle": "transformation",
            "description": f"Show the clear contrast {name} makes. {benefits[0]}.",
            "hook": "Watch the difference for yourself.",
        },
    ]
    if user_prompt:
        directions[0]["description"] = f"{user_prompt.strip().rstrip('.')} — {directions[0]['description']}"
    # Balance the batch: half image concepts, half video concepts.
    imgs = [d for d in directions if d.get("kind") == "image"]
    vids = [d for d in directions if d.get("kind") == "video"]
    n_img = max(1, count // 2)
    picked = imgs[:n_img] + vids[: max(1, count - n_img)]
    return {"ideas": picked[:count]}


def mock_script(brief: dict[str, Any], idea: dict[str, Any], req: dict[str, Any]) -> dict[str, Any]:
    name = _name(brief)
    benefits = _benefits(brief)
    hook = idea.get("hook") or f"Yaar, {name} ne toh game hi change kar diya!"
    return {
        "character": (
            "A warm, confident Indian woman in her late 20s; shoulder-length black hair; "
            "wearing a sage-green linen shirt; natural makeup; friendly, energetic vibe."
        ),
        "voice": "A warm, natural female Indian voice, mid-20s, friendly and clear, Hinglish delivery.",
        "setting": "A real, lived-in Indian home living room, warm morning sunlight, homely neutral palette.",
        "script": (
            f"[Hook] {hook} "
            f"[Body] Sach mein, {benefits[0].lower()} — bina kisi jhanjhat ke. "
            f"Main daily use karta hoon aur difference clearly dikhta hai. "
            f"[CTA] Trust me, ek baar try karo — link niche hai!"
        ),
        "voiceover": (
            f"{hook} Honestly, {name} is a total game-changer. {benefits[0]}, "
            f"bilkul easy. Aaj hi try karo!"
        ),
        "storyboard": [
            {"scene": "Hook", "visual": "Presenter close-up, energetic", "voiceover": hook, "on_screen_text": name, "duration": "0-4s"},
            {"scene": "Problem", "visual": "Relatable everyday struggle", "voiceover": "Pehle main bhi struggle karta tha…", "on_screen_text": "Relatable?", "duration": "4-9s"},
            {"scene": "Reveal", "visual": "Product held to camera", "voiceover": f"Phir mila {name}.", "on_screen_text": benefits[0], "duration": "9-16s"},
            {"scene": "Proof", "visual": "Product in use, happy reaction", "voiceover": benefits[-1], "on_screen_text": "⭐ 4.9/5", "duration": "16-23s"},
            {"scene": "CTA", "visual": "Presenter points down, smiling", "voiceover": "Link niche — abhi try karo!", "on_screen_text": brief.get("cta") or "Shop now", "duration": "23-28s"},
        ],
        "captions": [hook, "Pehle main bhi struggle karta tha…", benefits[0], "⭐ 4.9/5", brief.get("cta") or "Shop now"],
        "transitions": ["Punch in", "Hard cut", "Whip pan", "Zoom", "Cross dissolve"],
    }


def mock_score(target_type: str, content: str) -> dict[str, Any]:
    base = 78
    length = min(len(content or ""), 400)
    variance = (length % 15)
    def clamp(v):
        return max(50, min(97, v))
    scores = {
        "hook_strength": clamp(base + variance - 2),
        "readability": clamp(base + 8),
        "brand_consistency": clamp(base + 4),
        "visual_hierarchy": clamp(base + variance),
        "cta_quality": clamp(base + 6),
        "emotion": clamp(base + variance + 1),
        "conversion_potential": clamp(base + 3),
    }
    overall = round(sum(scores.values()) / len(scores), 1)
    return {
        "overall": overall,
        **scores,
        "suggestions": [
            "Lead with the single strongest benefit in the first 5 words.",
            "Tighten the body — cut any sentence that doesn't move the sale.",
            "Make the CTA more specific and action-oriented.",
            "Add a concrete proof point (number, review, or result).",
        ],
        "summary": f"Solid {target_type} with a clear message and a working CTA. The hook and emotional pull are the biggest levers for lift — sharpen those and this could break 90.",
    }
