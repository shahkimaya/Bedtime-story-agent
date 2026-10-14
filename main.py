import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

import prompts

load_dotenv()  # loads OPENAI_API_KEY from a local .env file if present

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

1. An evaluation harness: a fixed set of ~20 varied requests, run with and without the judge loop, comparing
   judge scores and a pairwise A/B judge (to guard against the judge just rewarding its own style).
2. Personalisation and memory: a child profile (name, favourite animals, fears to avoid) and recurring
   characters across nights, plus streaming and text-to-speech read-aloud with a slowing pace.
3. Cost/latency work: caching the categorizer, running the judge with a smaller rubric, and token tracking.
4. Judge calibration: hand-rate ~20 stories (1-5 on each criterion), compare with the judge's scores, and adjust
   the rubric wording and the PASS_AVG threshold until they agree, since the judge is the same small model as the
   writer and tends to be generous.
5. Best-of-N drafting: generate 3 first drafts at different temperatures and let the judge pick the strongest
   before any revision, instead of revising a single draft that may start weak.
6. Targeted revisions: have the judge point to the weak paragraphs and rewrite only those, so a fix to one
   problem (say, the ending) does not undo what already works elsewhere in the story.
7. Few-shot examples: add a short, hand-written model story for each category to the writer prompt, so the
   model copies good pacing, sentence length and a calm ending rather than inventing them from rules alone.
"""

MODEL = "gpt-3.5-turbo"  # do not change
MAX_REVISIONS = 2
PASS_AVG = 4.5  # average score at or above this (with no criterion below 4) ends the loop
WORDS = 400

_client = None


def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # key comes from the environment only
    resp = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def call_json(prompt: str, retries=2, **kw) -> dict:
    """Call the model and parse a JSON object from the reply, retrying if it is malformed."""
    for _ in range(retries + 1):
        text = call_model(prompt, temperature=0.0, **kw)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {}


def categorize(request: str) -> dict:
    info = call_json(prompts.CATEGORIZE.format(cats=list(prompts.CATEGORIES), request=request), max_tokens=400)
    if info.get("category") not in prompts.CATEGORIES:
        info["category"] = "other"
    info.setdefault("characters", [])
    info.setdefault("setting", "a cosy place")
    info.setdefault("tone", "warm and gentle")
    info.setdefault("moral", "kindness matters")
    items = info.get("must_include")
    items = items if isinstance(items, list) else []
    # Fall back to the characters, then to the raw request, so the judge always has something concrete to check.
    info["must_include"] = ", ".join(map(str, items or info["characters"])) or request
    return info


def plan_story(request: str, info: dict) -> str:
    style = prompts.CATEGORIES[info["category"]]
    return call_model(
        prompts.PLAN.format(
            request=request, category=info["category"], style=style,
            characters=", ".join(map(str, info["characters"])) or "your choice",
            setting=info["setting"], tone=info["tone"], moral=info["moral"],
            must_include=info["must_include"],
        ),
        max_tokens=600, temperature=0.7,
    )


def write_story(request: str, info: dict, outline: str) -> str:
    return call_model(
        prompts.WRITE.format(
            request=request, style=prompts.CATEGORIES[info["category"]], tone=info["tone"],
            outline=outline, words=WORDS, must_include=info["must_include"],
        ),
        max_tokens=1200, temperature=0.8,
    )


def judge_story(request: str, story: str, must_include: str) -> dict:
    result = call_json(
        prompts.JUDGE.format(request=request, story=story, words=WORDS, must_include=must_include), max_tokens=700
    )
    scores = {k: v for k, v in result.get("scores", {}).items() if isinstance(v, (int, float))}
    result["scores"] = scores
    result["avg"] = sum(scores.values()) / len(scores) if scores else 0.0
    result.setdefault("issues", [])
    result.setdefault("suggestions", [])
    return result


def passes(verdict: dict) -> bool:
    s = verdict["scores"]
    return bool(s) and verdict["avg"] >= PASS_AVG and min(s.values()) >= 4


def revise_story(request: str, story: str, feedback: str, must_include: str, label="Editor feedback") -> str:
    return call_model(
        prompts.REVISE.format(
            request=request, story=story, feedback=feedback, feedback_label=label, words=WORDS,
            must_include=must_include,
        ),
        max_tokens=1200, temperature=0.7,
    )


def improve_with_judge(request: str, story: str, must_include: str) -> str:
    """Judge -> revise loop. Keeps the best-scoring draft so a bad revision never replaces a good story."""
    best, best_verdict = story, judge_story(request, story, must_include)
    current, verdict = story, best_verdict
    for i in range(MAX_REVISIONS + 1):
        print(f"  [judge] draft {i + 1}: avg {verdict['avg']:.2f} {verdict['scores']}")
        if passes(verdict) or i == MAX_REVISIONS:
            break
        feedback = "\n".join(f"- {x}" for x in verdict["issues"] + verdict["suggestions"]) or "- Improve overall quality."
        current = revise_story(request, current, feedback, must_include)
        verdict = judge_story(request, current, must_include)
        if verdict["avg"] > best_verdict["avg"]:
            best, best_verdict = current, verdict
    return best


def tell_story(request: str) -> tuple[str, str]:
    print("  [router] classifying request...")
    info = categorize(request)
    print(f"  [router] category={info['category']} tone={info['tone']!r}")
    if info.get("safe_request") is False:
        print("  [router] request was not kid-friendly; telling a gentle version instead.")
    print("  [planner] outlining a 5-beat story arc...")
    outline = plan_story(request, info)
    print("  [storyteller] writing first draft...")
    story = write_story(request, info, outline)
    return improve_with_judge(request, story, info["must_include"]), info["must_include"]


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Please set the OPENAI_API_KEY environment variable.")
    request = input("😴 Time to dream! Tell me what story you want to hear tonight :")
    story, must_include = tell_story(request)
    while True:
        print("\n" + story + "\n")
        print("  [child] " + call_model(prompts.CHILD_REACTION.format(story=story), max_tokens=100, temperature=0.9))
        change = input("\nWant any changes? (describe them, or press Enter to finish) ").strip()
        if not change:
            print("Sweet dreams!")
            break
        story = revise_story(request, story, change, must_include, label="The listener asked for these changes")
        story = improve_with_judge(request, story, must_include)


if __name__ == "__main__":
    main()
