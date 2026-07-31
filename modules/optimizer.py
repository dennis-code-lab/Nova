import re
from modules.logger import log_info

def compress_context_stream(raw_context: str, max_lines: int = 15) -> str:
    """
    Applies sliding-window compaction to prevent token bloat.
    Trims redundant historical loops while preserving the most recent execution state.
    """
    if not raw_context:
        return ""
        
    lines = raw_context.split("\n")
    if len(lines) <= max_lines:
        return raw_context
        
    log_info("ContextOptimizer", f"Compacting raw context stream from {len(lines)} lines down to {max_lines}.")
    
    # Keep the initial header instructions for systemic grounding
    header = lines[:4]
    # Keep the most immediate runtime updates (the tail of the context)
    tail = lines[-(max_lines - 4):]
    
    compacted_text = "\n".join(header) + "\n  [... Context Optimized / Compressed Token Stream ...] \n" + "\n".join(tail)
    return compacted_text

def distill_failure_trajectory(critique_text: str) -> str:
    """
    Extracts the pure actionable directive from raw, verbose execution failure text.
    Removes system stack traces and noisy log signatures.
    """
    if not critique_text:
        return "No feedback recorded."
        
    # Standard cleaning: Strip out raw file paths, hex codes, and standard traceback noise
    clean_text = re.sub(r'File ".*?", line \d+, in .*', '', critique_text)
    clean_text = re.sub(r'AttributeError: .*', '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Isolate the core problem assertion
    words = clean_text.split()
    if len(words) > 30:
        return " ".join(words[:25]) + "... [Trajectory Condensed]"
        
    return clean_text