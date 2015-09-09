from fields import SimpleField, ComplexField

_field_cache = {}

            
def _get_field_cache(cls):
    return cls._fields


class SimpleDocumentMeta(type):
    def __new__(cls, name, bases, dct):
        # Collect all the fields up and move them onto a private attribute
        # called _fields.
        fields = {}
        for attr_name, attr_value in dct.iteritems():
            if isinstance(attr_value, (SimpleField, ComplexField)):
                fields[attr_name] =  attr_value

        # Only need to remove the current classes fields, base fields can
        # be added to the field cache later.
        for field_name in fields.iterkeys():
            del dct[field_name]

        for base in bases:
            fields.update(getattr(base, '_fields', {}))

        dct['_fields'] = fields

        # Move all fields into a fields attribute
        new_class = type.__new__(cls, name, bases, dct)

        return new_class


class SimpleDocument(object):
    __metaclass__ = SimpleDocumentMeta

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def dict_to_object(cls, doc, only_fields):
        fields = _get_field_cache(cls)
        model = cls()

        # Embedded documents do not always have IDs
        if '_id' in doc:
            model.id = doc['_id']

        for field_name, field_cls in fields.iteritems():
            if only_fields and field_name not in only_fields:
                continue
            db_field_name = field_cls.field_name or field_name
            if isinstance(field_cls, ComplexField):
                if db_field_name in doc:
                    field_value = field_cls.to_object(doc[db_field_name])
                else:
                    field_value = field_cls.default
            else:
                field_value = doc.get(db_field_name, field_cls.default)
            setattr(model, field_name, field_value)

        return model

    @classmethod
    def get_alias(cls, field_name):
        if '.' in field_name:
            field_name, children = field_name.split('.', 1)
        else:
            children = None

        fields = _get_field_cache(cls)
        if field_name in fields:
            field_cls = fields[field_name]

            if children:
                if not isinstance(field_cls, ComplexField):
                    raise ValueError('%s is not a ComplexField' % field_name)
                return "%s.%s" % (
                    field_cls.field_name or field_name,
                    field_cls.mapper.get_alias(children))
            else:
                return field_cls.field_name
        return None

    @classmethod
    def object_to_dict(cls, instance):
        fields = _get_field_cache(cls)

        dic = {}
        for field_name, field_cls in fields.iteritems():
            db_field_name = field_cls.field_name or field_name
            if isinstance(field_cls, ComplexField):
                value = field_cls.to_dict(instance, field_name)
            else:
                value = getattr(instance, field_name)

            dic[db_field_name] = value

        return dic


