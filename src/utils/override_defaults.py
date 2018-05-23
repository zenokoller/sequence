def override_defaults(defaults: dict, overrides: dict) -> dict:
    args = defaults.copy()
    args.update(
        {k: v for k, v in overrides.items() if k in defaults.keys() and v is not None}
    )
    return args
