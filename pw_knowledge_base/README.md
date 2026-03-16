# PW Knowledge Base — RAG-Lite for Agent Pipeline

## What Is This?

A **realistic synthetic knowledge base** for PhysicsWallah that feeds into your 4-agent pipeline.
This is NOT real PW data — it's realistic, industry-accurate data based on Indian edtech patterns.

## Why Synthetic (Not Scraped)?

| Factor | Scraping Real Data | Synthetic KB (This) |
|--------|-------------------|---------------------|
| **Time** | 3-4 hours (build scraper + clean data) | 15 min (generated) |
| **Legal risk** | Possible TOS violation | None |
| **Accuracy needed** | Your capstone needs "realistic", not "exact" | ✅ Realistic |
| **Maintenance** | Breaks when PW changes their site | Never breaks |
| **For demo** | Evaluators check if system works, not prices | ✅ Works perfectly |

## Files

### `pw_knowledge_base.json` — The Full Knowledge Base
Contains:
- **Company info**: PW overview, USPs, scale
- **Course catalog**: 6 courses (3 JEE, 2 NEET, 1 Boards) with full pricing, features, batch timings, faculty
- **Financial options**: EMI plans, 3 scholarship types, refund policy
- **Competitor context**: 5 competitors with PW differentiators
- **Student demographics**: 26 cities, 40 names, exam/class/budget distributions
- **Objection handling**: Pre-built responses for 8 common objection types
- **Agent persona**: Priya's personality, guidelines, phrases to use/avoid

### `context_templates.json` — Agent-Specific Context Blocks
Pre-built context strings optimized for each agent:
- **Agent 1 (Scenario Planner)**: Demographics + course list + personality variations
- **Agent 2 (Conversation Generator)**: Full course details + pricing + objection responses + conversation rules
- **Agent 3 (Extractor + Scorer)**: Valid field values for extraction validation
- **Agent 4 (QA Validator)**: Quality check criteria + distribution targets + accuracy rules

## How to Use in Your Pipeline

```python
import json

# Load knowledge base
with open('pw_knowledge_base/pw_knowledge_base.json', 'r') as f:
    kb = json.load(f)

# Load context templates
with open('pw_knowledge_base/context_templates.json', 'r') as f:
    contexts = json.load(f)

# In each agent, inject the relevant context into the system prompt:
def build_agent_prompt(agent_name, task_specific_instructions):
    context = contexts[f"agent_{agent_name}"]["context_block"]
    return f"""
{task_specific_instructions}

{context}
"""

# Example: Conversation Generator agent
system_prompt = build_agent_prompt(
    "2_conversation_generator",
    "Generate a realistic sales conversation based on the following scenario..."
)
```

## What's the Product Lesson Here?

**RAG-lite vs Full RAG decision framework:**

| Your Situation | Right Choice |
|----------------|-------------|
| Small KB (< 50 pages) + fits in context window | RAG-lite (this) |
| Large KB (100+ pages) + need semantic search | Full RAG (vector DB) |
| KB changes frequently + need real-time updates | Full RAG + data pipeline |
| One-time batch generation (your case) | RAG-lite (this) |

You chose the simplest tool that solves the problem. That's good product thinking.
