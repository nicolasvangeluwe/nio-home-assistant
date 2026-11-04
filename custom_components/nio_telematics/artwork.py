"""Packaged model and paint choices; no file reads during Home Assistant flows."""

PAINTS_BY_MODEL = {
    "ET5": ("cloud-white", "deep-black", "star-gray", "stratosphere-blue", "airspace-blue", "arctic-green", "first-light-kiss", "sunbath-yellow", "luminous-orange"),
    "ET5 Touring": ("cloud-white", "deep-black", "star-gray", "stratosphere-blue", "airspace-blue", "arctic-green", "first-light-kiss", "sunbath-yellow", "luminous-orange", "sunlight-gold"),
    "EL6": ("cloud-white", "deep-black", "star-gray", "stratosphere-blue", "airspace-blue", "arctic-green", "galaxy-shadow", "sunlight-gold", "southern-star", "luminous-orange"),
    "ET7": ("cloud-white", "deep-black", "star-gray", "sunrise-beige", "southern-star"),
    "EL7": ("cloud-white", "deep-black", "star-gray", "southern-star", "airspace-blue", "arctic-green", "luminous-orange"),
    "EL8": ("cloud-white", "deep-black", "new-moon-silver", "sunlight-gold", "nebula-green"),
    "ES8": ("cloud-white", "deep-black", "star-gray", "southern-star", "arctic-green"),
}

ALL_PAINTS = frozenset(paint for paints in PAINTS_BY_MODEL.values() for paint in paints)


def effective_model(model: str, name: str = "") -> str | None:
    """Use an explicit model or the longest model name in the vehicle title."""
    if model in PAINTS_BY_MODEL:
        return model
    if model != "auto":
        return None
    return next(
        (item for item in sorted(PAINTS_BY_MODEL, key=len, reverse=True) if item.lower() in name.lower()),
        None,
    )


def valid_paint(model: str, paint: str, name: str = "") -> bool:
    """Keep existing automatic artwork while validating explicit appearance."""
    return paint == "auto" or paint in PAINTS_BY_MODEL.get(effective_model(model, name), ())


def pin_model_for_paint(preferences: dict, name: str = "") -> dict:
    """Keep an explicit paint attached to its car after an entry is renamed."""
    if preferences["model"] == "auto" and preferences["paint"] != "auto":
        model = effective_model("auto", name)
        if model is not None:
            preferences = {**preferences, "model": model}
    return preferences
