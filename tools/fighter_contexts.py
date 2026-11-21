"""Build-time ownership for the existing CTB4 runtime selectors."""

ACTOR_CONTEXTS = {"GOUKI": 1, "MORRIGAN": 2, "TABASA": 3, "KEN": 4}
CONTEXT_ACTORS = {context: actor for actor, context in ACTOR_CONTEXTS.items()}


def active_contexts(selectors: set[int]) -> dict[str, int]:
    if selectors - (set(CONTEXT_ACTORS) | {255}):
        raise ValueError("table has an unassigned character context")
    return {
        actor: context
        for actor, context in ACTOR_CONTEXTS.items()
        if context in selectors
    }
