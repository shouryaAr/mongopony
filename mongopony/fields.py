class SimpleField(object):
    def __init__(self, field_name=None, default=None):
        self.default = default
        self.field_name = field_name


class StringField(SimpleField):
    pass
