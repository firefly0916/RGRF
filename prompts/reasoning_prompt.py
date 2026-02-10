import os


def reasoning_instructions():
    enabled = os.getenv("RGRF_REASONING_MODE", "0")
    if str(enabled).strip().lower() in ("1", "true", "yes", "on"):
        return (
            "\n[Reasoning]\n"
            "Provide brief reasoning (<=4 sentences), then give the required [FINAL_*] line.\n"
        )
    return ""
