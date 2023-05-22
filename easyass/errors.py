class Errors(list):
    """
    错误列表
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def error(self, message: str):
        self.append({'level': 'error', 'message': message})
        return self

    def warn(self, message: str):
        self.append({'level': 'warn', 'message': message})
        return self


__all__ = (
    'Errors',
)
