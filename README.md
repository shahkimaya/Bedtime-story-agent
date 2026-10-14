# Bedtime Story Agent

A command-line agent that turns a simple bedtime story request into a calm, age-appropriate story for ages 5-10. It uses a multi-step prompt pipeline with an LLM judge that scores each draft and drives revisions. It is built on `gpt-3.5-turbo` (fixed by the assignment) and the OpenAI Python SDK.

## How it works

1. **Router** (`categorize`): classifies the request as adventure, animal, friendship, fantasy, everyday or other. It also extracts characters, setting, tone, moral and a "must include" list. Unsafe requests are flagged and reframed gently instead of refused. Returns JSON at temperature 0.
2. **Planner** (`plan_story`): writes a 5-beat outline: setup, hook, rising action, climax, wind-down.
3. **Storyteller** (`write_story`): writes about 400 words using the category style guide and the outline.
4. **Judge** (`judge_story`): scores the story from 1 to 5 on six criteria: age_appropriate, arc, engagement, faithfulness, bedtime_ending and length. It returns issues and suggestions as JSON.
5. **Reviser** (`revise_story`): rewrites the story using the judge's feedback. The loop in `improve_with_judge` runs at most 2 revisions. It stops early when the average is at least 4.5 and no score is below 4, and it always keeps the best-scoring draft.
6. **Child persona**: a simulated 7-year-old gives a 1-2 sentence reaction to the finished story.
7. **User feedback loop**: the user can ask for changes. These go through the reviser and then the judge again.

The block diagram is in [DESIGN.md](DESIGN.md).

## Setup and run

```
pip install -r requirements.txt
copy .env.example .env     # then paste your OpenAI key into .env
python main.py
```

The key is read from `.env` or the `OPENAI_API_KEY` environment variable. `.env` is git-ignored and must never be committed.

## File guide

| File | Purpose |
|---|---|
| [main.py](main.py) | Pipeline functions (categorize, plan, write, judge, revise), the `call_model` and `call_json` helpers (JSON extraction with retries), config constants (`MODEL`, `MAX_REVISIONS`, `PASS_AVG`, `WORDS`), the CLI loop, and notes on what to build next |
| [prompts.py](prompts.py) | Category style guides and the prompt templates: `CATEGORIZE`, `PLAN`, `WRITE`, `JUDGE`, `REVISE`, `CHILD_REACTION` |
| [DESIGN.md](DESIGN.md) | Mermaid block diagram, design rationale and limitations |
| [requirements.txt](requirements.txt) | Dependencies: `openai`, `python-dotenv` |
| [.env.example](.env.example) | Template for the API key |
| `.env` | Local secret key (git-ignored, not part of the repo) |
| [.gitignore](.gitignore) | Excludes `.env`, `__pycache__/`, `*.pyc` and `.venv/` |

## Design highlights and limitations

- Route first, plan before writing, then run a self-refine judge loop with a best-draft guard.
- Robust JSON parsing with retries and defaults for missing fields.
- Low temperature for the router and judge (consistency), higher for planning and writing (creativity).
- Limitation: the judge is the same small model as the writer, so its scores are noisy and slightly generous.
- Next steps: an evaluation harness, child profile and memory, best-of-N drafting, targeted paragraph revisions and few-shot examples. The full list is at the top of `main.py`.

<details>
<summary>Original assignment instructions</summary>

# Hippocratic AI Coding Assignment
Welcome to the [Hippocratic AI](https://www.hippocraticai.com) coding assignment

## Instructions
The attached code is a simple python script skeleton. Your goal is to take any simple bedtime story request and use prompting to tell a story appropriate for ages 5 to 10.
- Incorporate a LLM judge to improve the quality of the story
- Provide a block diagram of the system you create that illustrates the flow of the prompts and the interaction between judge, storyteller, user, and any other components you add
- Do not change the openAI model that is being used.
- Please use your own openAI key, but do not include it in your final submission.
- Otherwise, you may change any code you like or add any files

---

## Rules
- This assignment is open-ended
- You may use any resources you like with the following restrictions
   - They must be resources that would be available to you if you worked here (so no other humans, no closed AIs, no unlicensed code, etc.)
   - Allowed resources include but not limited to Stack overflow, random blogs, chatGPT et al
   - You have to be able to explain how the code works, even if chatGPT wrote it
- DO NOT PUSH THE API KEY TO GITHUB. OpenAI will automatically delete it

---

## What does "tell a story" mean?
It should be appropriate for ages 5-10. Other than that it's up to you. Here are some ideas to help get the brain-juices flowing!
- Use story arcs to tell better stories
- Allow the user to provide feedback or request changes
- Categorize the request and use a tailored generation strategy for each category

---

## How will I be evaluated
Good question. We want to know the following:
- The efficacy of the system you design to create a good story
- Are you comfortable using and writing a python script
- What kinds of prompting strategies and agent design strategies do you use
- Are the stories your tool creates good?
- Can you understand and deconstruct a problem
- Can you operate in an open-ended environment
- Can you surprise us

---

## Other FAQs
- How long should I spend on this?
No more than 2-3 hours
- Can I change what the input is?
Sure
- How long should the story be?
You decide

</details>
