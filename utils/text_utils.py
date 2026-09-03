"""
utils/text_utils.py
 
Tiny, dependency-free text helpers. Kept separate from any single agent so
both `PresentationBuilder` (content assembly) and `PowerPointAgent`
(rendering) can enforce the same word ceilings without duplicating logic.
"""
 
 
def truncate_words(text: str, max_words: int, ellipsis: str = "…") -> str:
    """
    Truncate `text` to at most `max_words` words. Appends an ellipsis when
    truncation actually occurs so it's visually obvious content was cut,
    never silently drops words mid-sentence without a marker.
    """
    if not text:
        return ""
 
    words = text.strip().split()
 
    if len(words) <= max_words:
        return " ".join(words)
 
    return " ".join(words[:max_words]).rstrip(",.;:") + ellipsis
 
 
def first_non_empty(*values: str) -> str:
    """Return the first non-empty/non-whitespace string, else ''."""
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""