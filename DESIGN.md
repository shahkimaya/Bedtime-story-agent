# Bedtime Story Agent: Design

## Run
```
pip install -r requirements.txt
copy .env.example .env        # then edit .env and paste your key
python main.py
```
The key is read from `.env` (git-ignored) or the `OPENAI_API_KEY` environment variable, and is never committed. Model stays `gpt-3.5-turbo`.

## Block diagram
```mermaid
flowchart TD
    U([User request]) --> R[1. Router<br/>category, characters, tone, moral,<br/>safety reframe - JSON]
    R --> P[2. Planner<br/>5-beat story arc outline]
    P --> S[3. Storyteller<br/>category-specific style prompt]
    S --> J{4. Judge<br/>6-criterion rubric, JSON}
    J -- "fails (avg < 4.5 or any score < 4)<br/>max 2 revisions" --> V[5. Reviser<br/>issues + suggestions]
    V --> J
    J -- "passes, or revisions used up:<br/>best-scoring draft kept" --> O[Final story]
    O --> C[Child-reader persona<br/>1-2 sentence reaction]
    C --> F{User wants changes?}
    F -- yes, feedback --> V
    F -- no --> E([Sweet dreams])
```

## Design choices
- **Router first.** One cheap, deterministic (temp 0) call produces structured JSON that steers every later prompt and
  maps the request to a style guide (adventure, animal, friendship, fantasy, everyday). It also reframes unsafe requests
  into kid-friendly ones instead of refusing.
- **Plan before writing.** An explicit 5-beat arc (setup, hook, rising action, climax, wind-down) gives gpt-3.5 structure
  and makes every story end calmly for bedtime.
- **Judge loop (self-refine).** The judge scores age-appropriateness, arc, engagement, faithfulness, bedtime ending and
  length, and returns concrete issues and suggestions that go straight into the reviser prompt. The loop is capped at 2
  revisions, and the best-scoring draft wins, so a bad revision cannot make things worse.
- **Robust JSON.** `call_json` extracts the first JSON object and retries on parse failure; missing fields get defaults.
- **Temperatures.** 0 for router and judge (consistency), 0.7-0.8 for planning and writing (creativity).
- **User feedback.** After the story, the user can ask for changes; these go through the reviser and then the judge again.
- **Surprise.** A simulated 7-year-old reacts to each story, and judge scores are printed per draft so the improvement
  is visible.

## Limitations
The judge is the same small model as the writer, so scores are noisy and slightly generous. See the "next 2 hours" notes
at the top of `main.py`.
