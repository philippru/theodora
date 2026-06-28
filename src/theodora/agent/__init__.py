"""Agent layer — *LLM proposes, Theodora decides*.

Optional (`[agent]` extra). Every LLM proposal is re-checked by the deterministic validation
engine; nothing is accepted that doesn't pass. That is what makes provider choice safe — even a
weak or locally-hosted model can only ever propose, never decide.
"""
