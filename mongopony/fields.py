class SimpleField(object):
    def __init__(self, field_name=None, default=None):
        self.default = default
        self.field_name = field_name


class StringField(SimpleField):
    pass


class IntField(SimpleField):
    pass


class ComplexField(SimpleField):
    def __init__(self, mapper=None, *args, **kwargs):
        super(ComplexField, self).__init__(*args, **kwargs)
        self.mapper = mapper

class ListField(ComplexField):
    def to_dict(self, instance, field_name):
        values = getattr(instance, field_name)
        values = [self.mapper.object_to_dict(value) for value in values]
        return values
