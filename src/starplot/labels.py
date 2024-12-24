"""
Each plotted label attempt is combination of:
    - style (could change size, anchor point, offset)
    - position

    
"""


class LabelCollisionHandler:
    max_fallbacks: int = 10
    max_retries: int = 3

    def fallbacks(self):
        pass

    def on_fail(self):
        pass
