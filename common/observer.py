from . import interfaces

class Observer(interfaces.Callable):
    def __init__(
        self,
        name: str,
        callback: str,
    ):
        self.name = name
        super(Observer, self).__init__(callback=callback)
