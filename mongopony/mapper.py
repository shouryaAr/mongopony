from fields import SimpleField, ComplexField

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

class SimpleMapper(object):
    @classmethod
    def dict_to_object(cls, doc, only_fields):
        fields = _get_field_cache(cls)
        model = cls.model()

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
                return field_cls.field_name or field_name
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

    @classmethod
    def create(cls, *args, **kwargs):
        instance = cls.model()
        fields = _get_field_cache(cls)
        for field_name in kwargs.iterkeys():
            if field_name not in fields:
                raise ValueError('%s does not have field %s' % (
                    cls.model, field_name))
            setattr(instance, field_name, kwargs[field_name])
        return instance
    
class ClassFieldDelegator(object):
    @classmethod
    def dict_to_object(cls, doc, only_fields):
        cls_name = doc.get('_cls')
        mapper = cls.name_to_mapper.get(cls_name)
        if not mapper:
            mapper = cls.default_mapper

        return mapper.dict_to_object(doc, only_fields)

    @classmethod
    def get_alias(cls, field_name):
        strategies = set(cls.name_to_mapper.values())
        strategies.add(cls.default_mapper)

        for strategy in strategies:
            alias = strategy.get_alias(field_name)
            if alias:
                return alias
        return field_name

    @classmethod
    def _get_most_specific_mapper(cls, instance):
        match_name, match_mapper = None, None
        for cls_name, mapper in cls.name_to_mapper.iteritems():
            if isinstance(instance, mapper.model):
                if match_name:
                    if issubclass(mapper.model, match_mapper.model):
                        match_name = cls_name
                        match_mapper = mapper
                else:
                    match_name = cls_name
                    match_mapper = mapper

        if not match_name:
            raise ValueError('Unexpected type %s' % instance.__class__)

        return match_name, match_mapper

    @classmethod
    def object_to_dict(cls, instance):
        cls_name, mapper = cls._get_most_specific_mapper(instance)

        dic = mapper.object_to_dict(instance)
        dic['_cls'] = cls_name
        return dic
