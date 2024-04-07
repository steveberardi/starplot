import json

from functools import wraps


def merge_dict(dict_1: dict, dict_2: dict) -> None:
    """

    Args:
        dict_1: Base dictionary to merge into
        dict_2: Dictionary to merge into the base (dict_1)

    Returns:
        None (dict_1 is modified directly)
    """
    for k in dict_2.keys():
        if k in dict_1 and isinstance(dict_1[k], dict) and isinstance(dict_2[k], dict):
            merge_dict(dict_1[k], dict_2[k])
        else:
            dict_1[k] = dict_2[k]


def use_style(style_class, style_attr: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            style = kwargs.get("style")
            style_kwargs = {
                kw: value for kw, value in kwargs.items() if kw.startswith("style__")
            }

            if style and style_kwargs:
                raise ValueError(
                    "Too many style arguments types. Specify only style or style kwargs"
                )

            if style and isinstance(style, dict):
                if style_attr is not None:
                    # if style is a dict and there's a base style, then we just want to merge the changes
                    base_style = getattr(args[0].style, style_attr).model_dump_json()
                    base_style = json.loads(base_style)

                    merge_dict(base_style, style)

                    kwargs["style"] = style_class(**base_style)
                else:
                    kwargs["style"] = style_class(**style)

            elif style_kwargs:
                # if style kwargs are used - build style dict and pass as "style" variable
                styling_overrides = {}
                for key, val in style_kwargs.items():
                    t = styling_overrides
                    prev = None
                    for part in key.split("__")[1:]:
                        if prev is not None:
                            t = t.setdefault(prev, {})
                        prev = part
                    t.setdefault(prev, val)
                if style_attr is not None:
                    base_style = getattr(args[0].style, style_attr).model_dump_json()
                    base_style = json.loads(base_style)

                    merge_dict(base_style, styling_overrides)

                    kwargs["style"] = style_class(**base_style)
                else:
                    kwargs["style"] = style_class(**styling_overrides)

                # remove 'style__' kwargs so they're not passed to wrapped function
                kwargs = {
                    kw: value
                    for kw, value in kwargs.items()
                    if not kw.startswith("style__")
                }

            elif style is None and style_attr is not None:
                # if no style overrides and there's a base style, then just pass the base style
                kwargs["style"] = getattr(args[0].style, style_attr, None)

            return func(*args, **kwargs)

        return wrapper

    return decorator
