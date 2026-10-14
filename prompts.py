"""All prompt templates and category style guides, kept apart from pipeline logic."""

CATEGORIES = {
    "adventure": "Brisk and curious. A small quest with a clear goal, one friendly obstacle, and a clever (not violent) solution.",
    "animal": "Warm and playful. Animals have simple, distinct personalities and gentle humour. Include sounds and movement.",
    "friendship": "Tender and emotional. Focus on kindness, sharing, and making up after a small misunderstanding.",
    "fantasy": "Whimsical and magical. Gentle magic, friendly creatures, wonder. Any 'danger' is mild and quickly resolved.",
    "everyday": "Cosy and relatable. Small real-life moments (school, family, a new pet) made special.",
    "other": "Warm, imaginative and soothing.",
}

CATEGORIZE = """You are a children's story editor. Read the story request and reply with ONLY a JSON object:
{{"category": one of {cats}, "characters": [list of names/types], "must_include": [every specific name, relationship, trait, object or event the request explicitly mentions, copied closely], "setting": "short phrase", "tone": "2-3 words", "moral": "one short, gentle lesson", "safe_request": true or false}}
Set "safe_request" to false only if the request asks for violence, gore, horror or adult content. In that case still fill in a gentle alternative setting/tone/moral that keeps the spirit of the request in a kid-friendly way.

Request: {request}"""

PLAN = """You are a children's author planning a bedtime story for ages 5-10.
Request: {request}
Category: {category} ({style})
Characters: {characters}
Must include (from the request, each must matter to the plot): {must_include}
Setting: {setting}
Tone: {tone}
Moral: {moral}

Write a 5-beat outline, one or two sentences each:
1. Setup (meet characters and place)
2. Hook (something interesting happens or is wanted)
3. Rising action (try, fail, try again, with one fun surprise)
4. Climax (a clever, kind solution; nothing scary or violent)
5. Wind-down (calm resolution, cosy, ends with the character drifting off to sleep)
Output only the outline."""

WRITE = """You are a warm, gifted bedtime storyteller for children aged 5 to 10.
Write the story below following the outline.

Request: {request}
Style: {style}
Tone: {tone}
Must include: {must_include}
Outline:
{outline}

Rules:
- Every "Must include" item must appear in the story and matter to the plot. Use character names exactly as given in the request.
- About {words} words, with a short title.
- Simple vocabulary and short sentences; a few fun sound words or repetition for reading aloud.
- Vivid but gentle. No violence, death, or real fear. Any problem is small and solved with kindness or cleverness.
- Dialogue for the characters, and the moral shown through actions (do not lecture).
- The last paragraph slows down and ends peacefully, ready for sleep.
Output only the story."""

JUDGE = """You are a strict but kind editor of children's bedtime stories for ages 5-10.
Score the story from 1 (poor) to 5 (excellent) on each criterion:
- age_appropriate: vocabulary, sentence length, and no scary/violent/adult content
- arc: clear beginning, middle, end with a satisfying climax
- engagement: creativity, fun details, dialogue, a sense of wonder
- faithfulness: check EACH item of the Must-include list below. 5 = every item appears and matters to the plot, names used exactly; 4 = all appear but one is minor; 3 = one item missing or barely used; 2 = several missing; 1 = ignores the request. When you score below 5, name the missing or weak items in "issues".
- bedtime_ending: calm, soothing final paragraph
- length: about {words} words (score 5 if within 20%)

Request: {request}
Must include: {must_include}

Story:
\"\"\"
{story}
\"\"\"

Reply with ONLY JSON:
{{"scores": {{"age_appropriate": n, "arc": n, "engagement": n, "faithfulness": n, "bedtime_ending": n, "length": n}}, "issues": ["specific problems"], "suggestions": ["specific, actionable fixes"]}}"""

REVISE = """You are a children's bedtime storyteller revising your own story for ages 5-10.

Original request: {request}
Must include (keep or add these, each mattering to the plot): {must_include}

Current story:
\"\"\"
{story}
\"\"\"

{feedback_label}:
{feedback}

Rewrite the full story applying the feedback. Keep what already works, keep it about {words} words, and keep the calm bedtime ending. Output only the story, including a title."""

CHILD_REACTION = """You are a curious 7-year-old who just heard this bedtime story. In 1-2 short sentences, in a child's voice, say what you liked best and one thing you wish had happened.

Story:
{story}"""
