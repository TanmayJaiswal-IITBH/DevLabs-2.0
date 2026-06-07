# Healthcare Research Agent

A conversational healthcare research assistant powered by a **local Ollama LLM** and three real free public APIs. The agent uses a **ReAct loop** (Reason → Act → Observe) to answer medical queries — it never guesses numbers or invents drug facts.

---

## Features

- Live COVID-19 statistics by country or globally
- FDA drug label lookup — indications, warnings, and dosage
- Active clinical trial search from ClinicalTrials.gov
- Pydantic-validated tool inputs — bad input returns a clean error, never a crash
- Fully local LLM via Ollama — no cloud API key needed

---

## Setup

### 1. Install Python dependencies

```bash
pip install ollama pydantic requests
```

### 2. Install Ollama and pull a model

Download Ollama from https://ollama.com, then pull a model that supports tool-use:

```bash
ollama pull llama3.2        # recommended
# alternatives:
# ollama pull llama3.1
# ollama pull qwen2.5
# ollama pull mistral-nemo
```

### 3. Run the agent

```bash
python healthcare_agent.py
```

---

## Project Structure

```
healthcare_agent.py
│
├── Pydantic Schemas           # Validate every tool input at runtime
│   ├── DiseaseStatsInput
│   ├── DrugInfoInput
│   └── ClinicalTrialsInput
│
├── API Functions              # Real HTTP calls, never crash
│   ├── get_disease_stats()    → disease.sh
│   ├── get_drug_info()        → OpenFDA
│   └── find_clinical_trials() → ClinicalTrials.gov
│
├── Tool class                 # Wraps function + schema
│   ├── run()                  → validates with Pydantic, calls function
│   └── to_ollama_definition() → auto-generates Ollama JSON schema
│
└── HealthcareResearchAgent    # ReAct loop
    └── run()                  → Thought → Action → Observation → repeat
```

---

## Tools & APIs

| Tool | API | What it returns |
|---|---|---|
| `get_disease_stats` | [disease.sh](https://disease.sh) — free, no key | Cases, deaths, recoveries, tests by country or global |
| `get_drug_info` | [OpenFDA](https://open.fda.gov/apis/drug/label/) — free, no key | Brand/generic name, indications, warnings, dosage |
| `find_clinical_trials` | [ClinicalTrials.gov v2](https://clinicaltrials.gov/data-api/api) — free, no key | Recruiting trials with title, phase, sponsor, link |

---

## How the ReAct Loop Works

```
User question
      │
      ▼
 ollama.chat()  ──► Model decides: call a tool or reply?
      │
      ├─► Tool call → Tool.run()
      │       ├── Pydantic validates inputs
      │       ├── Real API call (with timeout)
      │       └── Returns result string (or error string)
      │
      ├─► Result appended as {"role": "tool", "content": ...}
      │
      └─► Loop repeats until no more tool calls
              │
              ▼
         Final answer returned to user
```

---

## Sample Runs

### Run 1 — COVID-19 statistics for India and globally

```
User: What are the current COVID-19 statistics for India and globally?

   → Calling : get_disease_stats({'country': 'India'})
  ← Result  :
    📊 COVID-19 Statistics — India
      Total Cases    : 45,035,393
      Deaths         : 533,570
      Recovered      : 0
      Active Cases   : 44,501,823
      Critical       : 0
      Total Tests    : 935,879,495
      Population     : 1,406,631,776
      Last Updated   : 2026-06-07 10:57 UTC

  → Calling : get_disease_stats({'country': 'global'})
  ← Result  :
    📊 COVID-19 Statistics — Global
      Total Cases    : 704,753,890
      Deaths         : 7,010,681
      Recovered      : 675,619,811
      Active Cases   : 22,123,398
      Critical       : 34,794
      Total Tests    : 7,026,505,313
      Population     : 7,944,935,131
      Last Updated   : 2026-06-07 10:57 UTC

Agent: Thank you for the call to get_disease_stats. Please note that these numbers are subject to change and may not reflect the current situation.
```

---

### Run 2 — Drug information for metformin

```
User: Tell me about metformin — what is it used for and what are the main warnings?

  → Calling : get_drug_info({'drug_name': 'metformin'})
  ← Result  :
    💊 Drug Information — SITAGLIPTIN AND METFORMIN HYDROCHLORIDE
      Brand Name(s)  : ZITUVIMET
      Manufacturer   : Zydus Lifesciences Limited
      Indications    : 1 INDICATIONS AND USAGE ZITUVIMET is a combination of sitagliptin, a dipeptidyl peptidase-4 (DPP-4) inhibitor, and metformin hydrochloride (HCl), a biguanide, indicated as an adjunct to diet and exercise to improve glycemic control in adults with type 2 diabetes mellitus. ( 1 ) Limitations of Use: ZITUVIMET is not recommended in patients with type…
      Warnings       : WARNING: LACTIC ACIDOSIS WARNING: LACTIC ACIDOSIS See full prescribing information for complete boxed warning . Postmarketing cases of metformin-associated lactic acidosis have resulted in death, hypothermia, hypotension, and resistant bradyarrhythmias. Symptoms included malaise, myalgias, respiratory distress, somnolence, and abdominal pain. Labor…
      Dosage Notes   : 2 DOSAGE AND ADMINISTRATION Take ZITUVIMET orally twice daily with meals. ( 2.1 ) Individualize the dosage of ZITUVIMET on the basis of the patient's current regimen, effectiveness, and tolerability. ( 2.1 ) The maximum recommended daily dose is 100 mg of sitagliptin and 2,000 mg of metformin HCl. ( 2.1 ) The recommended starting dose in patients n…
    ⚠️  Always consult a licensed pharmacist or doctor before use.

Agent: Metformin is a biguanide medication used to treat type 2 diabetes mellitus. It works by decreasing glucose production in the liver, improving insulin sensitivity, and increasing glucose uptake in muscles.

As for warnings, one of the main concerns with metformin is the risk of lactic acidosis, a rare but serious condition that can be fatal. This risk is increased in patients with:

* Renal impairment or chronic kidney disease
* Hepatic impairment or liver disease
* Concomitant use of other medications that may increase lactate levels

It's essential to note that metformin is not recommended for patients with type 1 diabetes, pancreatitis, or a history of liver disease.
```

---

### Run 3 — Active clinical trials for Alzheimer's disease

```
User: Are there any active clinical trials for Alzheimer's disease? Show me 3.

  → Calling : find_clinical_trials({'condition': 'Alzheimer', 'max_results': '3'})
  ← Result  :
    🔬 Clinical Trials for 'Alzheimer' — showing 3 of 0 recruiting trials:

      [1] A Clinical Study of MK-2214 in People With Early Alzheimer's Disease (MK-2214-004)
          NCT ID  : NCT07033494
          Status  : RECRUITING
          Phase   : PHASE2
          Sponsor : Merck Sharp & Dohme LLC
          Link    : https://clinicaltrials.gov/study/NCT07033494
      [2] Deep TMS for Comorbid Depression and Cognitive Impairment in Older Adults
          NCT ID  : NCT03665831
          Status  : RECRUITING
          Phase   : NA
          Sponsor : Rotman Research Institute at Baycrest
          Link    : https://clinicaltrials.gov/study/NCT03665831
      [3] Single-center Prospective Longitudinal Study of Taste in Patients With Cognitive Disorders
          NCT ID  : NCT05888961
          Status  : RECRUITING
          Phase   : NA
          Sponsor : Centre Hospitalier Universitaire Dijon
          Link    : https://clinicaltrials.gov/study/NCT05888961

Agent: I've found three active clinical trials for Alzheimer's disease. Please note that these trials are subject to change and may have different statuses or phases as they progress.

1. **A Clinical Study of MK-2214 in People With Early Alzheimer's Disease (MK-2214-004)**: This Phase 2 trial is recruiting participants and is being sponsored by Merck Sharp & Dohme LLC. The study aims to evaluate the efficacy and safety of MK-2214 in individuals with early Alzheimer's disease.

Link: https://clinicaltrials.gov/study/NCT07033494

2. **Deep TMS for Comorbid Depression and Cognitive Impairment in Older Adults**: This trial is also recruiting participants and is being sponsored by the Rotman Research Institute at Baycrest. The study will investigate the effectiveness of Deep Transcranial Magnetic Stimulation (TMS) in improving cognitive function and managing comorbid depression in older adults with cognitive disorders.

Link: https://clinicaltrials.gov/study/NCT03665831

3. **Single-center Prospective Longitudinal Study of Taste in Patients With Cognitive Disorders**: This observational study is recruiting participants and is being sponsored by the Centre Hospitalier Universitaire Dijon. The research aims to explore the relationship between taste disturbances and cognitive decline in patients with cognitive disorders, including Alzheimer's disease.

Link: https://clinicaltrials.gov/study/NCT05888961

Please consult a qualified healthcare professional for any information or advice regarding clinical trials or treatment options for Alzheimer's disease. These trials are for educational purposes only.
```

---

## Changing the Model

Edit the last section of `healthcare_agent.py`:

```python
agent = HealthcareResearchAgent(model="llama3.2")    # default
agent = HealthcareResearchAgent(model="qwen2.5")     # alternative
agent = HealthcareResearchAgent(model="mistral-nemo") # alternative
```

Any Ollama model with tool-use support will work.

---

> ⚠️ **Disclaimer:** All information provided by this agent is for educational and research purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.