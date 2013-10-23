from fields import SimpleField

_field_cache = {}

def _populate_field_cache(cls):
    fields = {}
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if isinstance(attr, SimpleField):
            fields[attr_name] = attr
    _field_cache[cls] = fields
            
def _get_field_cache(cls):
    fields = _field_cache.get(cls, {})
    if not fields:
        _populate_field_cache(cls)
        fields = _field_cache[cls]
    return fields

class SimpleStrategy(object):
    @classmethod
    def dict_to_object(cls, doc):
        fields = _get_field_cache(cls)
        model = cls.model()

        for field_name, field_cls in fields.iteritems():
            db_field_name = field_cls.field_name or field_name
            field_value = doc.get(db_field_name, field_cls.default)
            setattr(model, field_name, field_value)

        return model

    @classmethod
    def get_alias(cls, field_name):
        fields = _get_field_cache(cls)
        field_cls = fields[field_name]
        return field_cls.field_name or field_name

