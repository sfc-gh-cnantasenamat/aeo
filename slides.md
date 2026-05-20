---
# AI Engine Optimization (AEO)

## Measuring How Well AI Answers Developer Questions

*Chanin Nantasenamat, Daniel Myers, Umesh Unnikrishnan*
*Developer Relations, Snowflake*

---
# The Landscape: SEO in the Age of AI

Developers no longer Google first. They ask AI assistants. Three paradigms have emerged:

- **Answer Engine Optimization (AEO)** — optimizing content so AI chatbots surface your brand in conversational answers (featured snippets, voice search, zero-click results)
- **Generative Engine Optimization (GEO)** — structuring content so generative AI systems cite and recommend your product when synthesizing responses
- **AI Engine Optimization (AEO)** — *our approach*: measuring whether AI gives the **right answer**, not just whether it mentions you

```
Traditional SEO    → Rank on page 1 of Google
Answer Engine Opt  → Get cited in AI chatbot answers
Generative Engine  → Get recommended in AI-synthesized content
AI Engine Opt      → Ensure AI gives CORRECT answers about your product
```

---
# AEO vs GEO: Different Questions Entirely

| Dimension | Answer/Generative Engine Opt | Our AEO (Snowflake) |
|-----------|------------------------------|---------------------|
| Core question | "Does AI mention us?" | "Does AI get it right?" |
| Metric | Brand visibility, citation count | Correctness, completeness, recency |
| Who benefits | Marketing teams | Engineering and product teams |
| What it measures | Presence in responses | Quality of responses |
| Actionable output | Content structure changes | Documentation gap analysis |
| Example pioneer | Vercel (Feb 2026) | Snowflake DevRel (2026) |

Vercel built AEO to track whether coding agents recommend Next.js. We built AEO to measure whether coding agents give developers **correct Snowflake answers**.

---
# WHO: The Team and Stakeholders

**Built by:** Snowflake Developer Relations

**Serves two audiences:**

- **Platform engineering teams** who configure AI developer tools: which levers improve answer quality, and by how much?
- **Product managers** who own documentation: where are the coverage gaps that cause AI to fail on their product area?

**Judge panel:** 5 LLM judges score every response independently (claude-opus-4-6, claude-opus-4-7, openai-gpt-5.4, llama4-maverick, gemini-3.1-pro)

**Respondent models tested:** claude-opus-4-6, claude-opus-4-7, openai-gpt-5.4

---
# WHAT: The Benchmark System

**128 questions** across **32 Snowflake product categories** (4 per category)

**4 question types** testing different developer needs:
- **Explain** — conceptual understanding
- **Implement** — correct code and procedures
- **Debug** — diagnostic reasoning under failure
- **Compare** — tradeoff analysis between options

**5 scoring dimensions** (0-10 scale each):
- Correctness, Completeness, Recency, Citation, Recommendation

**Must-have checks:** Up to 5 binary pass/fail facts per question (640 total checks)

```
Total evaluation surface:
128 questions x 16 configurations x 3 models = 48 runs
48 runs x 5 judges = 240 scoring passes
240 passes x 128 questions = 30,720 individual scores
```

---
# WHY: The Problem We Solve

When a developer asks an AI assistant a Snowflake question, the quality depends on more than training data.

**What actually makes AI give better answers?**

- More instructions? (domain prompts)
- Access to tools? (web search, doc retrieval)
- Self-review loops? (generate then revise)
- All of the above?

**Nobody had tested this systematically.** Teams were guessing which configuration to deploy. We built a controlled experiment to replace intuition with data.

The **2 to the 4th factorial design** tests all 16 combinations of 4 binary factors, making interaction effects directly observable.

---
# HOW: The Factorial Experiment

**4 factors, each ON or OFF, all 16 combinations tested:**

| Factor | OFF | ON |
|--------|-----|-----|
| Domain Prompt | No system message | 1,800-token Snowflake primer |
| Citation | Raw question only | "Cite official docs" appended |
| Agentic Tools | Single API call, no tools | Full Cortex Code session |
| Self-Critique | Single-turn generation | Two-turn generate-then-revise |

**Non-agentic:** CORTEX.COMPLETE with 8,192-token cap
**Agentic:** Native Cortex Code with web search, bash, SQL, file I/O

**Scoring pipeline:** Custom 5-judge panel (not TruLens native) with canonical answer grounding and must-have binary checks

---
# WHEN and WHERE: Timeline and Infrastructure

**Timeline:**
- Feb 2026 — Vercel publishes AEO concept for brand tracking
- Mar 2026 — Snowflake DevRel pivots concept to answer quality
- Apr 2026 — v1 benchmark (50 questions, 13 categories)
- Apr 2026 — v2 expanded (128 questions, 32 categories, 3 models)
- Apr 2026 — v3 factorial (48 runs, 5-judge panel, full replication)
- May 2026 — v4 scale-up (42 categories, 840 questions via Docs CKE generation, SPCS runner)

**Infrastructure:**
- Response generation: Cortex Code CLI sessions (agentic) and CORTEX.COMPLETE API (non-agentic)
- Scoring: Custom pipeline with 5 independent LLM judges
- Observability: Per-question tool usage, token attribution, generation time
- Results: Streamlit app deployed on Snowflake (DevRel + Snowhouse)
- Automation: SPCS-based runner for scheduled benchmark execution

---
# Key Results

**Best configuration: Citation + Agentic (no domain prompt)**

| Config | Score | Must-Have |
|--------|------:|----------:|
| Baseline (all OFF) | 53.6% | 58.9% |
| Citation + Agentic | 69.2% | 72.4% |
| **Improvement** | **+15.6pp** | **+13.5pp** |

**Factor impact rankings:**

```
Agentic Tools    +8.5pp  ████████████████████████████████████████
Citation Instr   +1.5pp  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Domain Prompt    +0.1pp  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Self-Critique    -4.1pp  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░  (HURTS)
```

**Cross-model validation:** The hierarchy holds across all 3 respondent models. claude-opus-4-7 reaches 83.3% under C+A.

---
# Actionable Findings

**For platform teams configuring AI tools:**

1. **Deploy agentic tools, not bigger prompts.** Tool access is the only lever that meaningfully separates configurations.
2. **Pair citation with agentic tools.** Citation alone adds nothing; with tools it enables real doc retrieval.
3. **Remove domain prompts from agentic configs.** Static primers interfere with tool-based retrieval.
4. **Do not add self-critique.** It doubles generation time while reducing quality in every agentic configuration.

**For product managers (documentation gaps):**

- **Implement** is weakest in 50% of categories (16/32) — missing how-to guides and code examples
- **Debug** is weakest in 41% of categories (13/32) — missing troubleshooting runbooks
- Worst gaps: Cortex Agents (30.8% Implement), Iceberg Tables (31.3% Debug), Semantic Views (37.6% Implement)

---
# What Comes Next

**Immediate priorities:**

- Automate for regression detection (scheduled benchmark runs via SPCS)
- Expand question bank to 8-12 questions per category for tighter confidence intervals
- Extend factorial replication to all 5 judge models as respondents
- Build PM self-serve tooling (per-category gap analysis in Streamlit)

**The bigger picture:**

AEO is not a one-time study. It is a **continuous measurement system** that tells us whether AI developer tools are getting better or worse at answering real questions, and exactly where documentation investment will have the highest impact.

*Give the agent tools, tell it to cite sources, and stay out of its way.*
