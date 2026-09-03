"""
DISABLED.

This module used to generate the "red glowing network" abstract graphics
that were repeated across every topic slide. It has been disabled and
must never be reachable as a fallback in the presentation pipeline.

See tools/generate_placeholder_library.py for its replacement: a
category-specific, on-brand (white/charcoal/blue) local image library,
and agents/image_selector.py for the semantic selection engine that
replaces any random.choice()/first-result selection logic that pointed
here.

The original file is preserved as generate_assets.py.DISABLED_DO_NOT_USE
for reference only. Do not re-enable it or wire it back into
presentation_builder.py / powerpoint_agent.py as a fallback path.
"""

def generate_assets(*args, **kwargs):
    raise RuntimeError(
        "generate_assets.py is disabled. Use tools/generate_placeholder_library.py "
        "(local placeholders) or tools/download_images.py (real stock photos, "
        "requires real internet + API key) instead."
    )
