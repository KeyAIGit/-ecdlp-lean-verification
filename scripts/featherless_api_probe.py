#!/usr/bin/env python3
"""Zero-token Featherless plan/model probe with sanitized diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from hypothesis_model_drafter import USER_AGENT, classify_http_error


API_BASE = "https://api.featherless.ai/v1"
DEFAULT_MODELS = (
    "deepseek-ai/DeepSeek-V4-Flash",
    "deepseek-ai/DeepSeek-V4-Pro",
    "moonshotai/Kimi-K2.6",
    "zai-org/GLM-5.1",
)


def request_json(path: str, api_key: str) -> dict[str, Any]:
    request = urllib.request.Request(
        API_BASE + path,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
            "HTTP-Referer": "https://github.com/KeyAIGit/-ecdlp-lean-verification",
            "X-Title": "KeyAI Featherless API Probe",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Featherless response is not an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("featherless-api-probe.json")
    )
    parser.add_argument("--model", action="append", dest="models")
    args = parser.parse_args()

    api_key = os.environ.get("FEATHERLESS_API_KEY", "").strip()
    report: dict[str, Any] = {
        "schema_version": "0.1",
        "provider": "featherless",
        "key_present": bool(api_key),
        "token_generation_attempted": False,
        "status": "unknown",
        "plan": None,
        "models": [],
    }
    if not api_key:
        report["status"] = "missing_secret"
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 2

    try:
        plan = request_json("/plan", api_key)
        report["plan"] = {
            key: plan.get(key)
            for key in (
                "id",
                "name",
                "max_context_length",
                "max_model_size",
                "concurrency",
            )
        }
        for model in args.models or DEFAULT_MODELS:
            encoded = urllib.parse.quote(model, safe="")
            detail = request_json(f"/models/{encoded}", api_key)
            report["models"].append(
                {
                    "id": model,
                    "status": detail.get("status"),
                    "available_on_current_plan": detail.get(
                        "available_on_current_plan"
                    ),
                    "context_length": detail.get("context_length"),
                    "max_completion_tokens": detail.get(
                        "max_completion_tokens"
                    ),
                }
            )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        report["status"] = classify_http_error(exc.code, body)
        report["http_status"] = exc.code
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 3
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report["status"] = "transport_or_response_error"
        report["error_type"] = type(exc).__name__
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 4

    available = [
        item
        for item in report["models"]
        if item["available_on_current_plan"] is True
    ]
    report["status"] = "ready" if available else "no_preferred_model_available"
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if available else 5


if __name__ == "__main__":
    raise SystemExit(main())
