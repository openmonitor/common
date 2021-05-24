class OpenmonitorError(Exception):
    pass

class OpenmonitorConfigError(OpenmonitorError):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args)
        self.time_str = kwargs.get('time_str')

class OpenmonitorNotSupported(OpenmonitorError):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args)
        self.time_str = kwargs.get('time_str')