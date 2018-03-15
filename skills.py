class Skill(object):
    def __init__(self, name, cost, description):
        self.name = name
        self.cost = cost
        self.description = description


skill_list = [
    Skill('axe', 6, 'Attack and defend with an axe.'),
    Skill('bow', 5, 'Shoot with a bow.'),
    Skill('first aid', 3, 'Tend to minor wounds and bleeding; requires bandages.'),
    Skill('unarmed', 3, 'Fight with bare hands'),
    Skill('shield', 4, 'Defend with a shield.'),
    Skill('spear', 4, 'Attack and defend with a spear.'),
    Skill('sword', 4, 'Attack and defend with a sword.')
]