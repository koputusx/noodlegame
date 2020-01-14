from builtins import object
class Component(object):
    #Base class for components to minimize boilerplate.
    def set_owner(self, entity):
        self.owner = entity