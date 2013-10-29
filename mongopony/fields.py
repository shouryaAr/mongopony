class SimpleField(object):
    def __init__(self, field_name=None, default=None, required=False):
        self.default = default
        self.field_name = field_name
        self.required = required


class StringField(SimpleField):
    def __init__(self, max_length=None, choices=None, **kwargs):
        self.max_length = max_length
        self.choices = choices
        super(StringField, self).__init__(**kwargs)


class IntField(SimpleField):
    pass

class FloatField(SimpleField):
    pass

class BooleanField(SimpleField):
    pass

class DateTimeField(SimpleField):
    pass

class ObjectIdField(SimpleField):
    pass

class ComplexField(SimpleField):
    def __init__(self, embedded_field=None, mapper=None, *args, **kwargs):
        super(ComplexField, self).__init__(*args, **kwargs)
        self.mapper = mapper
        self.embedded_field = embedded_field

class ListField(ComplexField):
    def to_dict(self, instance, field_name):
        values = getattr(instance, field_name)
        if self.mapper:
            values = [self.mapper.object_to_dict(value) for value in values]

        return values

    def to_object(self, values):
        if self.mapper:
            values = [
                self.mapper.dict_to_object(value, None) for value in values]
        return values

class DictField(ComplexField):
    def to_dict(self, instance, field_name):
        values = getattr(instance, field_name)
        values = {
            k: self.mapper.object_to_dict(v) for k, v in values.iteritems()
        }
        return values
