# PW Voice AI — Session Notes
# Update this file at the END of every working session
# Paste this file at the START of the next session to restore context

---

## PROJECT GOAL
Build an elegant Voice AI product prototype for PhysicsWallah that:
1. Shows a Command Center with lead pipeline metrics and live activity
2. Lets user trigger inbound or outbound calls
3. Plays audio with live call UI (embedded HTML component)
4. After call: reveals transcript, lead qualification, AI-generated next steps
5. Shows simulated integrations (Slack, email, CRM)
6. Has an evals page with model, conversation, and business metrics

Demo audience: Mixed (technical + business)
Final demo: First week of April (~3 weeks away)
Time budget: 9 hours (3 hrs/week × 3 weeks)

---

## TECH STACK
- Language: Python 3.14
- TTS: Google Cloud Text-to-Speech API
- Conversation generation: Claude API (Anthropic) — claude-sonnet-4-20250514
- ML Model: Random Forest (scikit-learn) — trained on 100 synthetic leads
- Dashboard: Streamlit (localhost:8501) + embedded HTML component for call experience
- API key loading: `from config.api_keys import CLAUDE_API_KEY`
- Google credentials: `os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(ROOT, "config", "google_credentials.json")`

---

## PROJECT STRUCTURE
C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\
├── config\
│   ├── api_keys.py                    ← CLAUDE_API_KEY lives here
│   └── google_credentials.json        ← Google service account key
├── src\
│   ├── agents\
│   │   ├── scenario_planner.py        ← generate_hot/warm/cold_scenarios(count=N) — NEEDS REWORK
│   │   ├── conversation_generator.py  ← ConversationGenerator(api_key, kb_path).generate(scenario)
│   │   ├── extractor_agent.py
│   │   └── qa_validator.py
│   ├── orchestrator.py
│   ├── scoring_engine.py
│   ├── data_extractor.py
│   ├── data\
│   │   ├── conversations\             ← 100 text conversations
│   │   ├── voice_conversations\       ← 15 voice conversations with MP3s
│   │   │   ├── voice_hot_001\         ← SHOWCASE (Aoede + Fenrir)
│   │   │   ├── voice_warm_001\        ← SHOWCASE (Aoede + Kore)
│   │   │   └── voice_cold_001\        ← SHOWCASE (Aoede + Fenrir)
│   │   ├── lead_scoring_model.pkl
│   │   ├── label_encoders.pkl
│   │   ├── processed_leads.json
│   │   └── synthetic_leads_dataset.csv
├── pw_knowledge_base\
│   ├── pw_knowledge_base.json
│   └── context_templates.json
├── pages\
│   ├── 1_Command_Center.py            ← NEW — replaces Analytics
│   ├── 2_Lead_List.py
│   ├── 3_Live_Demo.py                 ← MAJOR REWORK — inbound/outbound + HTML component
│   └── 4_Evals.py                     ← NEW — model + conversation + business metrics
├── app.py                             ← Main Streamlit entry point
├── regenerate_voices.py
└── voice_sampler_v2.py

---

## VOICE DECISIONS (finalized)
| Role           | Voice                    | Speed | Pitch |
|----------------|--------------------------|-------|-------|
| Agent (Priya)  | hi-IN-Chirp3-HD-Aoede    | 0.95  | 0.0   |
| Student male   | hi-IN-Chirp3-HD-Fenrir   | 1.05  | 0.0   |
| Student female | hi-IN-Chirp3-HD-Kore     | 1.05  | 0.0   |

IMPORTANT: Chirp3-HD voices require pitch=0.0 — any other value causes 400 error
Gender detection: check scenario["name"].lower() against FEMALE_NAMES set

---

## KNOWN GOTCHAS
- Python 3.14 — pydub's AudioSegment breaks (pyaudioop removed in 3.13+)
- ffmpeg IS installed — pydub MP3 merging now works ✅
- Scenario planner uses "student_name" key; some places use "name" — handle both
- `st.stop()` doesn't reliably halt execution inside st.spinner() — use `raise` instead
- pages/ files must be single .py extension (was double .py.py, now fixed)

---

## KEY DESIGN DECISIONS (finalized in brainstorming session — March 8, 2026)

### Framework
- Streamlit for all pages (command center, lead list, evals)
- Embedded HTML component (st.components.v1.html()) for call experience page only
- Rationale: Streamlit can't do real-time stateful call UI well, but is great for data pages

### Call Flow — Inbound vs. Outbound
- User picks "Incoming Call" or "Make Outbound Call" — NOT HOT/WARM/COLD
- System decides the outcome (no predetermined tiers)
- More realistic, more impressive for demo audience

### Scenario Generation — Independent Attributes (Approach 3)
- Attributes randomized independently: class, exam, timeline, budget, decision maker
- Single differentiator between inbound/outbound: engagement level distribution
  - Inbound: engagement skews medium/high
  - Outbound: engagement skews low/medium
- All other attributes sampled from the same pool regardless of call type
- Rationale: mirrors reality — real students aren't "designed" to be hot or cold

### ML Model
- Call type is METADATA ONLY — not a scoring feature
- Model scores purely on conversation signals (extracted fields)
- Product story: "AI scores based on what the student said, not how they reached us"
- Retrain with noise to hit 85-90% accuracy (100% looks fake)

### Demo Page — 4 States (embedded HTML component)
- STATE 1 — READY: Two buttons: "Incoming Call" / "Make Outbound Call"
- STATE 2 — CALL IN PROGRESS:
  - Agent name (Priya), speaker indicators, call timer, audio playing
  - Outbound: shows pre-populated student context (name, lead source, city)
  - Inbound: shows minimal info ("Inbound — PW Helpline")
  - NO live data extraction during call — clean listening experience
- STATE 2→3 TRANSITION: 2-3 second "Analyzing conversation..." animation
- STATE 3 — POST-CALL ANALYSIS:
  - Full transcript
  - Extracted fields revealed
  - Rule-based + ML scores with tier badge
  - AI-GENERATED personalized action previews (one extra Claude API call):
    - Slack notification card (styled like real Slack message)
    - Email to student card (with personalized subject + body preview)
    - CRM record card (lead ID, status, assigned team, follow-up date)
  - Recommended next steps based on tier:
    - HOT: "Transfer to senior sales rep, send pricing brochure"
    - WARM: "Schedule follow-up in 3 days, send course comparison"
    - COLD: "Add to nurture campaign, revisit in 30 days"
- STATE 4 — LEAD ADDED: Confirmation + nav to command center or back to State 1

### Command Center
- Philosophy B: Funnel and trends view + small live activity section at top
- Pre-populated with simulated pipeline stages for 100 existing leads
- Stages: New (~15), Contacted (~35), Qualified (~30), Transferred (~12), Converted (~5), Dropped (~3)
- Tier correlates with progression (HOT leads overrepresented in Transferred/Converted)
- Randomly assigned within constraints
- New leads from demo page appear in real time

### Evals Page — 3 Categories
1. Model Performance: accuracy, precision, recall, confusion matrix, feature importance
2. Conversation Quality: avg length, objection diversity, field extraction coverage
3. Business Impact Simulation: time saved per lead, cost per qualified lead, conversion lift

### Integrations
- ALL SIMULATED — no real API calls to Slack/email/database
- Rich visual previews that look like the real thing
- Rationale: audience cares about the experience, not whether HTTP fired

---

## WEEK-BY-WEEK PLAN (revised March 8, 2026)
| Week | Focus                                              | Hours | Status         |
|------|----------------------------------------------------|-------|----------------|
| 1-5  | Pipeline + 100 conversations + ML + Streamlit v1   | —     | DONE ✅        |
| 6    | Voice demo feature + audio merge                   | —     | DONE ✅        |
| 7    | ML realism + scenario planner/generator rework      | 2 hrs | NOT STARTED ⬜ |
| 8    | Call experience HTML component + action previews    | 3 hrs | NOT STARTED ⬜ |
| 9    | Command center + evals page + demo prep             | 3-4hr | NOT STARTED ⬜ |

### Week 7 — Detailed Tasks (next session)
- [ ] Inject noise into training data → retrain model to ~85-90% accuracy
- [ ] Add confidence intervals to score display
- [ ] Rework scenario_planner.py:
  - Replace generate_hot/warm/cold_scenarios() with generate_scenario(call_type)
  - Randomize attributes independently
  - Single differentiator: engagement_level distribution differs by call_type
  - Add call_type field to scenario dict ("inbound" or "outbound")
- [ ] Update conversation_generator.py:
  - Different system prompt opening for inbound vs outbound
  - Inbound: agent answers "Thanks for calling PhysicsWallah..."
  - Outbound: agent initiates "Hi, am I speaking with {name}? I noticed you..."
- [ ] Test: generate 5 inbound + 5 outbound, verify variety of tiers emerge

### Week 8 — Detailed Tasks
- [ ] Build embedded HTML component for call experience (4 states)
- [ ] State 1: ready screen with two buttons
- [ ] State 2: call in progress UI (speakers, timer, context panel)
- [ ] State 2→3: "Analyzing conversation..." animation (2-3 sec)
- [ ] State 3: transcript + scores + AI-generated action previews
- [ ] State 4: confirmation + navigation
- [ ] Wire up Claude API call for personalized Slack/email/CRM content
- [ ] Test full flow: inbound and outbound, all possible tiers

### Week 9 — Detailed Tasks
- [ ] Build 1_Command_Center.py:
  - Live activity section (calls today, leads processed)
  - Pipeline funnel visualization (New → Contacted → Qualified → Transferred → Converted)
  - Trend charts (leads over time, tier distribution)
  - Simulate pipeline stages for 100 existing leads
  - Wire up: new leads from demo page update command center
- [ ] Build 4_Evals.py:
  - Model performance tab (confusion matrix, accuracy, feature importance)
  - Conversation quality tab (length distribution, field coverage, objection diversity)
  - Business impact tab (time saved, cost per lead, conversion lift estimates)
- [ ] Demo prep:
  - Run full demo flow 3 times end-to-end
  - Handle edge cases (API timeout, generation failure)
  - Prepare demo script and talking points
- [ ] Update SESSION_NOTES.md with final state

---

## DEMO NARRATIVE (suggested flow)
1. Open Command Center — show populated pipeline, "this is what the sales manager sees"
2. Navigate to Live Demo — "let's watch what happens when a student calls in"
3. Click "Incoming Call" — listen to conversation play out
4. Call ends — "Analyzing conversation..." beat
5. Post-call reveal — transcript, scoring, tier, "watch what the system does next"
6. Show AI-generated Slack notification, email preview, CRM record
7. "Now let's see an outbound call" — repeat with different experience
8. Navigate back to Command Center — "notice the new lead appeared"
9. Show Evals page — "here's how we validate the system works"
10. Q&A

---

## IMPLEMENTATION NOTES FOR SONNET (use in desktop app)

### Scenario Planner Rework
Current: generate_hot_scenarios(count), generate_warm_scenarios(count), generate_cold_scenarios(count)
New: generate_scenario(call_type="inbound"|"outbound")
- Randomize independently: current_class, exam, months_to_exam, budget_concern, decision_maker
- Engagement level: inbound → weighted toward ["high", "medium"], outbound → weighted toward ["medium", "low"]
- Add "call_type" field to scenario dict
- Use existing name/city pools from knowledge base

### Conversation Generator Changes
- Accept call_type from scenario
- Inbound opening: "Namaste! Thank you for calling PhysicsWallah. This is Priya, how can I help you today?"
- Outbound opening: "Hi, am I speaking with {student_name}? This is Priya from PhysicsWallah. I noticed you {lead_source}..."
- lead_source examples: "downloaded our JEE preparation guide", "visited our website", "registered for our free webinar"
- Keep message count at 20

### ML Noise Injection
- Add random noise to 10-15% of training labels (flip tier for those rows)
- Add slight gaussian noise to numeric features
- Retrain Random Forest → target 85-90% accuracy
- Save new model to lead_scoring_model.pkl
- Save confusion matrix and classification report for evals page

### Post-Call Action Generation (Claude API)
After scoring, make one Claude API call with:
- Full transcript
- Extracted fields
- Assigned tier
- Prompt: "Generate personalized post-call actions as JSON: slack_message, email (to/subject/body), crm_record (fields), next_steps (list)"
- Parse JSON response → display in State 3 cards

### Simulated Pipeline Stages
- Write a one-time script to assign stages to 100 existing leads
- Logic: tier influences stage probabilities
  - HOT → higher chance of Transferred/Converted
  - WARM → mostly Contacted/Qualified
  - COLD → mostly New/Contacted/Dropped
- Save as pipeline_stages.json or add to processed_leads.json
- Command center reads this data + appends any new live demo leads

### HTML Component Architecture
- Single HTML file with embedded CSS + JS
- Receives data from Streamlit via st.components.v1.html(html_string, height=...)
- Streamlit generates audio + data in Python, base64-encodes audio
- Passes everything into HTML template as JS variables
- HTML/JS handles: audio playback, speaker animation, timer, state transitions
- After call ends, HTML displays transcript + scores + action cards
- No communication back to Streamlit needed (all data pre-computed)
