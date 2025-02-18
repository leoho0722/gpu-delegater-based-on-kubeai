class BaseController:

    def __init__(self):
        self.setup_routes()

    def setup_routes(self):
        raise NotImplementedError("Subclasses must implement this method")
