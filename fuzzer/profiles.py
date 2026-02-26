from __future__ import annotations

# Flags are intentionally conservative to keep runs stable across local d8 builds.
ENGINE_PROFILES: dict[str, list[str]] = {
    "default": [],
    "ignition": ["--jitless"],
    "sparkplug": ["--sparkplug", "--no-maglev", "--no-turbofan"],
    "maglev": ["--maglev", "--no-turbofan"],
    "turbofan": ["--turbofan"],
    "stress": ["--stress-opt", "--always-turbofan"],
}


def resolve_profile_flags(name: str) -> list[str]:
    if name not in ENGINE_PROFILES:
        raise KeyError(f"unknown engine profile: {name}")
    return list(ENGINE_PROFILES[name])
