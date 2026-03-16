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
Final demo: First week of April (~2 weeks away)

---

## TECH STACK
- Language: Python 3.14
- TTS: Google Cloud Text-to-Speech API (LINEAR16/WAV output)
- Conversation generation: Claude API — claude-sonnet-4-20250514
- ML Model: Random Forest (scikit-learn) — 88% CV accuracy (retrained with noise)
- Dashboard: Streamlit (localhost:8501) + embedded HTML component for call experience
- API key loading: `from config.api_keys import CLAUDE_API_KEY`
- Google credentials: `os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(ROOT, "config", "google_credentials.json")`

---

## PROJECT STRUCTURE
C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\
├── config\
│   ├── api_keys.py                    ← CLAUDE_API_KEY lives here
│   └── google_credentials.json
├── src\
│   ├── agents\
│   │   ├── scenario_planner.py        ← generate_scenario(call_type) — UPDATED ✅
│   │   ├── conversation_generator.py  ← inbound/outbound openings — UPDATED ✅
│   │   ├── extractor_agent.py
│   │   └── qa_validator.py
│   ├── orchestrator.py
│   ├── scoring_engine.py
│   ├── data_extractor.py
│   ├── data\
│   │   ├── conversations\
│   │   ├── voice_conversations\
│   │   │   ├── voice_hot_001\         ← SHOWCASE (Aoede + Fenrir)
│   │   │   ├── voice_warm_001\        ← SHOWCASE (Aoede + Kore)
│   │   │   └── voice_cold_001\        ← SHOWCASE (Aoede + Fenrir)
│   │   ├── lead_scoring_model.pkl     ← RETRAINED at 88% CV accuracy ✅
│   │   ├── lead_scoring_model_v1.pkl  ← original 100% model (backup)
│   │   ├── label_encoders.pkl
│   │   ├── eval_metrics.json          ← NEW — for evals page ✅
│   │   ├── processed_leads.json
│   │   └── synthetic_leads_dataset.csv
├── pw_knowledge_base\
│   ├── pw_knowledge_base.json
│   └── context_templates.json
├── pages\
│   ├── 1_Analytics.py                 ← will become Command Center in Week 9
│   ├── 2_Lead_List.py
│   └── 3_Live_Demo.py                 ← updated to inbound/outbound ✅
├── app.py
├── retrain_with_noise.py              ← Week 7 script (keep for reference)
├── test_week7.py                      ← smoke test (keep for reference)
└── voice_sampler_v2.py

---

## VOICE DECISIONS (finalized)
| Role           | Voice                    | Speed | Pitch |
|----------------|--------------------------|-------|-------|
| Agent (Priya)  | hi-IN-Chirp3-HD-Aoede    | 0.95  | 0.0   |
| Student male   | hi-IN-Chirp3-HD-Fenrir   | 1.05  | 0.0   |
| Student female | hi-IN-Chirp3-HD-Kore     | 1.05  | 0.0   |

Audio format: LINEAR16 (WAV) — merged using Python's built-in wave module
IMPORTANT: Chirp3-HD voices require pitch=0.0 — any other value causes 400 error

---

## KNOWN GOTCHAS
- Python 3.14 — pydub breaks (pyaudioop removed). Use wave module for WAV merging.
- No admin access — cannot install ffmpeg via PATH
- Scenario planner uses "student_name" key — handle both "name" and "student_name"
- `st.stop()` unreliable inside st.spinner() — use `raise` instead
- Windows CMD doesn't support multi-line python -c — always use a .py script file
- Terminal commands can accidentally get pasted into .py files — always verify after editing

---

## WEEK-BY-WEEK PLAN
| Week | Focus                                             | Status      |
|------|---------------------------------------------------|-------------|
| 1-5  | Pipeline + 100 conversations + ML + Streamlit v1  | DONE ✅     |
| 6    | Voice demo feature + audio merge (WAV)            | DONE ✅     |
| 7    | ML realism + scenario/generator rework            | DONE ✅     |
| 8    | Call experience HTML component + action previews  | UP NEXT ⬜  |
| 9    | Command center + evals page + demo prep           | NOT STARTED |

---

## WEEK 7 — COMPLETED
- [x] ML retrained with noise → 88% CV accuracy (was 100%)
- [x] eval_metrics.json saved for evals page
- [x] scenario_planner.py — added generate_scenario(call_type="inbound"|"outbound")
- [x] conversation_generator.py — inbound/outbound opening logic
- [x] 3_Live_Demo.py — wired to use new generate_scenario(), inbound/outbound radio buttons
- [x] Verified end-to-end: inbound call generates correct opening ("Namaste! Thank you for calling...")

---

## WEEK 8 — DETAILED TASKS (next session)

### The big build: Replace 3_Live_Demo.py with HTML component experience

### Task 1: Build HTML component (4 states)
- STATE 1 — READY: Two buttons "📞 Incoming Call" / "📱 Make Outbound Call"
- STATE 2 — CALL IN PROGRESS:
  - Agent avatar (Priya) + Student avatar with speaking indicators
  - Call timer counting up
  - Outbound: shows pre-populated student context (name, lead source, city)
  - Inbound: shows minimal info ("Inbound — PW Helpline")
  - Audio playing via HTML5 audio element (base64 encoded WAV passed in)
- STATE 2→3 TRANSITION: "Analyzing conversation..." animation (2-3 sec)
- STATE 3 — POST-CALL ANALYSIS:
  - Full transcript (agent left, student right)
  - Extracted fields panel
  - Rule-based + ML scores with tier badge
  - AI-generated action cards (separate Claude API call):
    - Slack notification (styled like real Slack)
    - Email to student (subject + body preview)
    - CRM record (lead ID, status, assigned team, follow-up date)
  - Recommended next steps based on tier:
    - HOT: "Transfer to senior sales rep, send pricing brochure"
    - WARM: "Schedule follow-up in 3 days, send course comparison"
    - COLD: "Add to nurture campaign, revisit in 30 days"
- STATE 4 — LEAD ADDED: Confirmation + nav options

### Task 2: Post-call action generation (Claude API call)
Prompt includes: full transcript + extracted fields + assigned tier
Output JSON:
  - slack_message: channel, text (what Priya promised + tier recommendation)
  - email: to, subject, body preview
  - crm_record: lead_id, status, assigned_team, follow_up_date
  - promised_actions: list of things agent explicitly promised in conversation
  - recommended_actions: tier-based next steps
Key insight: "promised_actions" extracted FROM conversation + "recommended_actions" added ON TOP
Demo moment: "The AI heard what Priya promised and automatically queued those actions"

### Task 3: Wire full flow in Streamlit
- Streamlit generates scenario + conversation + audio (Python side)
- Base64 encodes WAV audio
- Passes all data into HTML template as JS variables
- HTML handles playback + state transitions
- After call, Python scores lead and generates action cards
- Display everything in State 3

### SSML pronunciation fixes (do in Task 1)
- "JEE" → spell out: <say-as interpret-as="characters">JEE</say-as>
- "NEET" → same
- Mobile numbers → <say-as interpret-as="telephone">

---

## WEEK 9 — DETAILED TASKS
- [ ] Rename 1_Analytics.py → 1_Command_Center.py
- [ ] Build command center: pipeline funnel + live activity + trends
- [ ] Simulate pipeline stages for 100 existing leads (save as pipeline_stages.json)
- [ ] Build 4_Evals.py: model performance + conversation quality + business impact
- [ ] Demo prep: run full flow 3x end-to-end, prepare talking points

---

## DEMO NARRATIVE (suggested flow)
1. Open Command Center — "this is what the sales manager sees every morning"
2. Navigate to Live Demo — "let's watch what happens when a student calls in"
3. Click "Incoming Call" — listen to conversation play
4. Call ends — "Analyzing conversation..." beat
5. Post-call reveal — transcript, scoring, tier
6. "Watch what the system does next" — Slack, email, CRM cards appear
7. "Notice it also captured what Priya promised" — promised actions highlighted
8. "Now let's try an outbound call" — repeat with different experience
9. Back to Command Center — "notice the new lead appeared in the pipeline"
10. Evals page — "here's how we validate the system works"
11. Q&A

---

## KEY DECISIONS LOG
- WAV over MP3 (no ffmpeg needed, better browser compatibility)
- Google TTS over ElevenLabs (already integrated)
- Inbound/outbound over HOT/WARM/COLD (more realistic product experience)
- System decides tier — user doesn't predetermine outcome
- ML accuracy 88% (100% looks fake to technical audience)
- Post-call actions: promised_actions (extracted) + recommended_actions (tier-based)
- All integrations simulated — no real Slack/email API calls
- HTML component for call experience (Streamlit can't do real-time stateful UI)
