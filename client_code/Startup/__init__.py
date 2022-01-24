from ._anvil_designer import StartupTemplate


class Startup(StartupTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
