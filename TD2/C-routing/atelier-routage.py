#!/usr/bin/env python3
"""TD 2, Step 3 (Pair C): the supplied routing simulator, adapted to our rule.

No API call, no key. What changed compared with the supplied file:
- RESOURCES holds our five TD 1 models (all on free routes) plus the paid
  OpenRouter route of gpt-oss-120b, instead of three fictitious resources;
- eligibility is no longer a level 1/2/3: a model is eligible for a question
  family only if it was 100 % correct on that family in traces-td1.csv;
- the checks come from our one-page rule (family x use);
- every "reason" cites the TD 1 cells that justify the decision.
The order of the branches in choose is unchanged.

Prices (portefeuille-modeles-en, snapshot of 28 September 2026):
- gpt-oss-20b#groq, qwen3.8-27b#groq, gpt-oss-120b#groq: free route, 0;
- north-mini-code:free and dots-3-note-preview:free: absent from the snapshot,
  free route according to their ":free" identifier (to document in
  five-model-summary-en.csv);
- gpt-oss-120b#openrouter: pay-per-token, 0.15 USD/M input, 0.60 USD/M output.
  With the mean TD 1 request of this model (640.7 prompt tokens, 243.7
  completion tokens): 0.000242 USD per request.
"""
import argparse
import json

# Question families and their TD 1 cells (assignment made by Pair C).
FAMILIES = {
    "F1": "C01 C04 C05 C06 C07 C20",
    "F2": "C02 C08 C09 C11",
    "F2b": "C10",
    "F3": "C12",
    "F1+F3": "C03 C13 C14",
    "F1+F2": "C15",
    "F2+F3": "C16",
    "F1+F2+F3": "C17 C19",
    "F1+F2b": "C18",
}

# Correct answers per family in traces-td1.csv (batch of 2026-10-21).
NORTH = {"F1": 6, "F2": 0, "F2b": 0, "F3": 1, "F1+F3": 3, "F1+F2": 0, "F2+F3": 1, "F1+F2+F3": 0, "F1+F2b": 0}
DOTS = {"F1": 6, "F2": 3, "F2b": 1, "F3": 1, "F1+F3": 3, "F1+F2": 0, "F2+F3": 0, "F1+F2+F3": 1, "F1+F2b": 0}
QWEN = {"F1": 5, "F2": 4, "F2b": 1, "F3": 1, "F1+F3": 3, "F1+F2": 0, "F2+F3": 0, "F1+F2+F3": 0, "F1+F2b": 1}
OSS20 = {"F1": 6, "F2": 1, "F2b": 1, "F3": 1, "F1+F3": 3, "F1+F2": 1, "F2+F3": 1, "F1+F2+F3": 2, "F1+F2b": 1}
OSS120 = {"F1": 6, "F2": 4, "F2b": 1, "F3": 1, "F1+F3": 3, "F1+F2": 1, "F2+F3": 1, "F1+F2+F3": 1, "F1+F2b": 1}

RESOURCES = [
    {"id": "cohere/north-mini-code:free", "provider": "openrouter", "access": "free",
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None, "td1": NORTH},
    {"id": "dots-studio/dots-3-note-preview:free", "provider": "openrouter", "access": "free",
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None, "td1": DOTS},
    {"id": "qwen/qwen3.8-27b", "provider": "groq", "access": "free",
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None, "td1": QWEN},
    {"id": "openai/gpt-oss-20b", "provider": "groq", "access": "free",
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None, "td1": OSS20},
    {"id": "openai/gpt-oss-120b", "provider": "groq", "access": "free",
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None, "td1": OSS120},
    # Same model on its paid route: same TD 1 results, different price.
    {"id": "openai/gpt-oss-120b#openrouter", "provider": "openrouter-paid", "access": "tokens",
     "available": True, "cash": 0.000242, "allocation": 0.000242, "reset_minutes": None, "td1": OSS120},
]

# Checks of our rule: family -> use -> check.
NO_AGE = {"dashboard": "none", "customer": "2-of-3 quorum", "payout": "3-of-5 quorum"}
AGE = {"dashboard": "2-of-3 quorum", "customer": "3-of-5 quorum", "payout": "3-of-5 quorum + reference"}
CHECKS = {
    "F1": NO_AGE, "F3": NO_AGE, "F1+F3": NO_AGE,
    "F2": AGE, "F2b": AGE, "F1+F2b": AGE,
    "F1+F2": {"dashboard": "2-of-3 quorum", "customer": "reference", "payout": "reference"},
    "F2+F3": {"dashboard": "2-of-3 quorum", "customer": "3-of-5 quorum", "payout": "reference"},
    "F1+F2+F3": {"dashboard": "2-of-3 quorum", "customer": "reference or review", "payout": "review"},
}


def cases(family):
    return len(FAMILIES[family].split())


def total(resource):
    """TD 1 score out of 20, used only to break ties between free routes."""
    return sum(resource["td1"].values())


def evidence(resource, family):
    """The TD 1 cells that justify calling this model on this family."""
    return f"TD1 {resource['td1'][family]}/{cases(family)} on {FAMILIES[family]}"


def choose(request, resources):
    """Same branch order as the supplied policy: included capacity, then
    deferral, then paid route within budget, then abstention."""
    family = request["family"]
    if family not in FAMILIES:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": "review",
                "reason": f"no TD1 cell for family {family}: eligibility unknown"}
    # Eligible = 100 % correct on the family in TD 1.
    eligible = [r for r in resources if r["td1"][family] == cases(family)]
    checks = CHECKS[family][request["use"]]
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        # All our free routes cost 0: among them, take the model with the lowest
        # TD 1 total, to keep the quota of the stronger models for the families
        # that only they can serve.
        chosen = min(included, key=lambda r: (r["allocation"], total(r), r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "eligible included capacity; " + evidence(chosen, family)}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "recheck availability at wake-up; " + evidence(chosen, family),
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["allocation"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": "available route within the authorised budget; " + evidence(chosen, family)}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no model with 100 % in TD1 on {family} ({FAMILIES[family]}) is reachable within deadline and budget"}


def exhaust(provider):
    """The free quota of one provider is used up; it refills in 60 minutes."""
    return [dict(r, available=False, reset_minutes=60) if r["provider"] == provider else dict(r)
            for r in RESOURCES]


def scenarios():
    base = {"family": "F1", "use": "dashboard", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.30}
    age = {**base, "family": "F2"}
    return [
        ("simple", base, RESOURCES),
        ("complex", age, RESOURCES),
        ("deferrable", age, exhaust("groq")),
        ("urgent", {**age, "can_wait": False, "deadline_minutes": 5}, exhaust("groq")),
        ("budget exhausted", {**age, "can_wait": False, "budget": 0}, exhaust("groq")),
        ("high impact", {**age, "use": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "F4"}, RESOURCES),
        # Added by Pair C: a free route is exhausted but another one is available.
        ("included before deferral", base, exhaust("openrouter")),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
