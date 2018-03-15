class Component:
    #Base class for components to minimize boilerplate.
    def set_owner(self, entity):
        self.owner = entity