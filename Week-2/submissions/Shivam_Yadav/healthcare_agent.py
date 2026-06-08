"""
Week 2 — Healthcare Research Agent
Domain: Healthcare / Medical Research

Demonstrates:
- Typed tool inputs with Pydantic
- Real API calls (no hardcoded data, no API key required)
- Tool class pattern with auto-generated Ollama definitions
- Graceful error handling in tools
- Type hints on all functions and class attributes

APIs used (all free, no key required):
  1. disease.sh          — live COVID-19 / disease statistics by country
  2. OpenFDA             — FDA drug label & medication information
  3. ClinicalTrials.gov  — active recruiting clinical trials search

Run:
    pip install ollama pydantic requests
    ollama pull llama3.2        
    python healthcare_agent.py
"""

import json
import requests
import ollama
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator
from typing import Callable, Any


# ─────────────────────────────────────────────
# TOOL INPUT SCHEMAS (Pydantic)
# ─────────────────────────────────────────────

class DiseaseStatsInput(BaseModel):
    """Input for the disease statistics tool."""
    country: str  # e.g. "India", "USA", "global"

    @field_validator("country")
    @classmethod
    def country_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("country cannot be empty")
        return v.strip()


class DrugInfoInput(BaseModel):
    """Input for the drug information tool."""
    drug_name: str  # e.g. "ibuprofen", "metformin", "amoxicillin"

    @field_validator("drug_name")
    @classmethod
    def drug_name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("drug_name cannot be empty")
        return v.strip().lower()


class ClinicalTrialsInput(BaseModel):
    """Input for the clinical trials search tool."""
    condition: str      # e.g. "diabetes", "breast cancer", "alzheimer"
    max_results: int = 3

    @field_validator("condition")
    @classmethod
    def condition_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("condition cannot be empty")
        return v.strip()

    @field_validator("max_results")
    @classmethod
    def clamp_results(cls, v: int) -> int:
        return max(1, min(v, 5))  # keep between 1 and 5


# ─────────────────────────────────────────────
# REAL API FUNCTIONS
#
# Each function:
# - Makes a real HTTP call to a free public API
# - Has a timeout (never skip this)
# - Returns a formatted string (what the model reads)
# - Never crashes — catches exceptions and
#   returns an error string instead
# ─────────────────────────────────────────────

def get_disease_stats(country: str) -> str:
    """
    Fetch live COVID-19 statistics for a country (or globally)
    using disease.sh — free, no API key needed.

    Args:
        country: Country name / ISO code, or "global" for worldwide totals.

    Returns:
        Formatted string with case counts, deaths, recoveries, and tests.
    """
    try:
        if country.lower() in ("global", "all", "world", "worldwide"):
            url = "https://disease.sh/v3/covid-19/all"
            label = "Global"
        else:
            url = f"https://disease.sh/v3/covid-19/countries/{country}"
            label = None  # will be read from response

        response = requests.get(url, timeout=6)

        # disease.sh returns 404 for unknown country names
        if response.status_code == 404:
            return (
                f"Country '{country}' not found. "
                "Try the full country name or ISO code, e.g. 'USA', 'India', 'UK', 'Germany'."
            )

        response.raise_for_status()
        data = response.json()

        # Format the Unix-ms timestamp into a readable date
        updated_ms: int = data.get("updated", 0)
        if updated_ms:
            updated_str = datetime.fromtimestamp(
                updated_ms / 1000, tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M UTC")
        else:
            updated_str = "N/A"

        name = label or data.get("country", "Unknown")

        def fmt(n: int | None) -> str:
            return f"{n:,}" if isinstance(n, int) else "N/A"

        return (
            f"📊 COVID-19 Statistics — {name}\n"
            f"  Total Cases    : {fmt(data.get('cases'))}\n"
            f"  Deaths         : {fmt(data.get('deaths'))}\n"
            f"  Recovered      : {fmt(data.get('recovered'))}\n"
            f"  Active Cases   : {fmt(data.get('active'))}\n"
            f"  Critical       : {fmt(data.get('critical'))}\n"
            f"  Total Tests    : {fmt(data.get('tests'))}\n"
            f"  Population     : {fmt(data.get('population'))}\n"
            f"  Last Updated   : {updated_str}"
        )

    except requests.HTTPError as e:
        return f"Could not fetch stats for '{country}': HTTP {e.response.status_code}"
    except requests.RequestException as e:
        return f"Could not fetch disease statistics: {e}"


def get_drug_info(drug_name: str) -> str:
    """
    Look up drug label information from the OpenFDA API
    (free, no API key needed, up to 1 000 requests/day).

    Tries a generic-name search first, then falls back to brand-name.

    Args:
        drug_name: Generic or brand name of the drug.

    Returns:
        Formatted string with brand name, indications, warnings, and dosage.
    """

    def _fetch(search_field: str) -> requests.Response:
        return requests.get(
            "https://api.fda.gov/drug/label.json",
            params={
                "search": f'openfda.{search_field}:"{drug_name}"',
                "limit": 1,
            },
            timeout=8,
        )

    def _truncate(text: str, chars: int = 350) -> str:
        return text[:chars].rstrip() + "…" if len(text) > chars else text

    def _first(value: list[str] | str | None, fallback: str = "N/A") -> str:
        if isinstance(value, list):
            return value[0] if value else fallback
        return value if value else fallback

    try:
        # Try generic name first, then brand name
        response = _fetch("generic_name")
        if response.status_code == 404:
            response = _fetch("brand_name")

        if response.status_code == 404:
            return (
                f"No FDA drug label found for '{drug_name}'. "
                "Try an alternative spelling or the generic name."
            )

        response.raise_for_status()
        data = response.json()
        results: list[dict[str, Any]] = data.get("results", [])

        if not results:
            return f"No drug label found for '{drug_name}'."

        label = results[0]
        openfda: dict[str, Any] = label.get("openfda", {})

        brand_names: str = ", ".join(openfda.get("brand_name", ["N/A"]))
        generic_names: str = ", ".join(openfda.get("generic_name", ["N/A"]))
        manufacturer: str = _first(openfda.get("manufacturer_name"))

        indications: str = _truncate(
            _first(label.get("indications_and_usage"))
        )
        warnings: str = _truncate(
            _first(label.get("warnings", label.get("boxed_warning")))
        )
        dosage: str = _truncate(
            _first(label.get("dosage_and_administration"))
        )

        return (
            f"💊 Drug Information — {generic_names}\n"
            f"  Brand Name(s)  : {brand_names}\n"
            f"  Manufacturer   : {manufacturer}\n"
            f"  Indications    : {indications}\n"
            f"  Warnings       : {warnings}\n"
            f"  Dosage Notes   : {dosage}\n"
            f"⚠️  Always consult a licensed pharmacist or doctor before use."
        )

    except requests.HTTPError as e:
        return f"Drug info lookup failed: HTTP {e.response.status_code}"
    except requests.RequestException as e:
        return f"Drug info lookup failed: {e}"


def find_clinical_trials(condition: str, max_results: int = 3) -> str:
    """
    Search for actively recruiting clinical trials on ClinicalTrials.gov
    using their v2 API (free, no API key needed).

    Args:
        condition: Medical condition or disease, e.g. "diabetes", "lung cancer".
        max_results: Number of trials to return (1–5).

    Returns:
        Formatted list of trials with title, phase, sponsor, and direct link.
    """
    try:
        response = requests.get(
            "https://clinicaltrials.gov/api/v2/studies",
            params={
                "query.cond": condition,
                "filter.overallStatus": "RECRUITING",
                "pageSize": max_results,
                "format": "json",
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        studies: list[dict[str, Any]] = data.get("studies", [])
        total: int = data.get("totalCount", 0)

        if not studies:
            return (
                f"No actively recruiting clinical trials found for '{condition}'.\n"
                "Try a broader term, e.g. 'cancer', 'diabetes', 'heart disease'."
            )

        lines: list[str] = [
            f"🔬 Clinical Trials for '{condition}' — "
            f"showing {len(studies)} of {total:,} recruiting trials:\n"
        ]

        for i, study in enumerate(studies, 1):
            proto: dict[str, Any] = study.get("protocolSection", {})

            id_mod: dict[str, Any]     = proto.get("identificationModule", {})
            status_mod: dict[str, Any] = proto.get("statusModule", {})
            design_mod: dict[str, Any] = proto.get("designModule", {})
            sponsor_mod: dict[str, Any] = proto.get("sponsorCollaboratorsModule", {})

            nct_id: str       = id_mod.get("nctId", "N/A")
            title: str        = id_mod.get("briefTitle", "No title available")[:90]
            status: str       = status_mod.get("overallStatus", "N/A")
            phases: list[str] = design_mod.get("phases", [])
            phase: str        = ", ".join(phases) if phases else "Not specified"
            sponsor: str      = sponsor_mod.get("leadSponsor", {}).get("name", "N/A")

            lines.append(
                f"  [{i}] {title}\n"
                f"      NCT ID  : {nct_id}\n"
                f"      Status  : {status}\n"
                f"      Phase   : {phase}\n"
                f"      Sponsor : {sponsor}\n"
                f"      Link    : https://clinicaltrials.gov/study/{nct_id}"
            )

        return "\n".join(lines)

    except requests.HTTPError as e:
        return f"Clinical trials search failed: HTTP {e.response.status_code}"
    except requests.RequestException as e:
        return f"Clinical trials search failed: {e}"


# ─────────────────────────────────────────────
# TOOL CLASS
#
# Wraps a function + its Pydantic schema.
# run()                  → validates inputs, then calls the function.
# to_ollama_definition() → auto-generates the JSON schema Ollama needs.
# ─────────────────────────────────────────────

class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        input_model: type[BaseModel],
        func: Callable[..., str],
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.input_model: type[BaseModel] = input_model
        self.func: Callable[..., str] = func

    def run(self, raw_input: dict[str, Any]) -> str:
        """Validate inputs with Pydantic, then invoke the API function."""
        try:
            validated = self.input_model(**raw_input)
            return self.func(**validated.model_dump())
        except Exception as e:
            return f"Tool '{self.name}' failed: {e}"

    def to_ollama_definition(self) -> dict[str, Any]:
        """
        Auto-generate the Ollama tool definition from the Pydantic model.

        Ollama follows the OpenAI function-calling schema:
        {
            "type": "function",
            "function": {
                "name": ...,
                "description": ...,
                "parameters": {
                    "type": "object",
                    "properties": { field: { "type": ..., "description": ... } },
                    "required": [...]
                }
            }
        }
        """
        schema = self.input_model.model_json_schema()
        raw_props: dict[str, Any] = schema.get("properties", {})
        required: list[str] = schema.get("required", [])

        # Build a clean properties dict Ollama can consume
        # (strips Pydantic meta-fields like 'title', '$ref', etc.)
        clean_props: dict[str, Any] = {}
        for prop_name, prop_def in raw_props.items():
            entry: dict[str, Any] = {"type": prop_def.get("type", "string")}
            if "description" in prop_def:
                entry["description"] = prop_def["description"]
            if "default" in prop_def:
                entry["default"] = prop_def["default"]
            clean_props[prop_name] = entry

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": clean_props,
                    "required": required,
                },
            },
        }


# ─────────────────────────────────────────────
# TOOL REGISTRY
# ─────────────────────────────────────────────

TOOLS: list[Tool] = [
    Tool(
        name="get_disease_stats",
        description=(
            "Fetch live COVID-19 statistics for a specific country or globally. "
            "Returns total cases, deaths, recoveries, active cases, and test count. "
            "Use 'global' for worldwide totals. "
            "Always use this tool when the user asks about disease numbers, "
            "COVID data, or pandemic statistics."
        ),
        input_model=DiseaseStatsInput,
        func=get_disease_stats,
    ),
    Tool(
        name="get_drug_info",
        description=(
            "Look up FDA-approved drug label information for a medication: "
            "brand/generic names, manufacturer, indications, warnings, and dosage. "
            "Use for any question about a specific medicine or drug, "
            "e.g. 'what is ibuprofen for?', 'what are the side effects of metformin?'."
        ),
        input_model=DrugInfoInput,
        func=get_drug_info,
    ),
    Tool(
        name="find_clinical_trials",
        description=(
            "Search for actively recruiting clinical trials for a medical condition "
            "on ClinicalTrials.gov. Returns trial title, phase, sponsor, and a direct "
            "link to the trial page. Use when the user asks about ongoing research, "
            "clinical studies, or trials for a disease."
        ),
        input_model=ClinicalTrialsInput,
        func=find_clinical_trials,
    ),
]

TOOL_MAP: dict[str, Tool] = {t.name: t for t in TOOLS}


# ─────────────────────────────────────────────
# AGENT
# ─────────────────────────────────────────────

class HealthcareResearchAgent:
    """
    A healthcare research assistant that uses a ReAct loop
    (Reason → Act → Observe) to answer medical queries using
    three real public APIs via a locally running Ollama model.
    """

    def __init__(self, model: str = "llama3.2") -> None:
        self.model: str = model
        self.tool_definitions: list[dict[str, Any]] = [
            t.to_ollama_definition() for t in TOOLS
        ]
        self.system: str = (
            "You are a knowledgeable and compassionate healthcare research assistant. "
            "You help users understand disease statistics, medication details, "
            "and ongoing clinical research.\n\n"
            "Rules:\n"
            "- Always use the available tools to fetch real data. Never guess numbers or drug facts.\n"
            "- For disease stats, always call get_disease_stats.\n"
            "- For drug questions, always call get_drug_info.\n"
            "- For research/trial questions, always call find_clinical_trials.\n"
            "- Remind users that your information is for educational purposes only, "
            "and they should consult a qualified doctor for diagnosis or treatment decisions."
        )

    def run(self, user_message: str) -> str:
        """Run the ReAct agent loop for a single user query."""
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.system},
            {"role": "user",   "content": user_message},
        ]

        print(f"\nUser: {user_message}")

        while True:
            # ── THOUGHT ──────────────────────────────────────────────
            # Model reasons and decides the next action (tool call or reply).
            response = ollama.chat(
                model=self.model,
                messages=messages,
                tools=self.tool_definitions,
            )

            assistant_msg = response.message
            messages.append(assistant_msg)   # keep full history

            # No tool calls → the model is done; return the final answer
            if not assistant_msg.tool_calls:
                return assistant_msg.content or "[No response generated]"

            # ── ACTION + OBSERVATION ─────────────────────────────────
            # Execute each requested tool and feed results back into context.
            for tool_call in assistant_msg.tool_calls:
                fn_name: str = tool_call.function.name
                fn_args: Any = tool_call.function.arguments

                # Ollama may return arguments as a JSON string; parse if needed
                if isinstance(fn_args, str):
                    try:
                        fn_args = json.loads(fn_args)
                    except json.JSONDecodeError:
                        fn_args = {}

                if fn_name not in TOOL_MAP:
                    result = f"Error: Unknown tool '{fn_name}'."
                else:
                    print(f"  → Calling : {fn_name}({fn_args})")
                    result = TOOL_MAP[fn_name].run(fn_args)
                    print(f"  ← Result  :\n    "
                          + result.replace("\n", "\n    "))

                # Observation: feed the tool result back to the model
                messages.append({
                    "role": "tool",
                    "content": result,
                })


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    
    agent = HealthcareResearchAgent(model="llama3.2")

    queries: list[str] = [
        "What are the current COVID-19 statistics for India and globally?",
        "Tell me about metformin — what is it used for and what are the main warnings?",
        "Are there any active clinical trials for Alzheimer's disease? Show me 3.",
    ]

    for query in queries:
        answer = agent.run(query)
        print(f"\nAgent: {answer}")
        print("─" * 60)