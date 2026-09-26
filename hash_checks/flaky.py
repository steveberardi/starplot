def flake(func):
    """
    Marks a hash check as flaky: if it fails, that failure won't count towards
    the overall check run failing (it's tracked separately instead).
    """
    func.flaky = True
    return func
