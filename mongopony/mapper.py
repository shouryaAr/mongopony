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

class SimpleMapper(object):
    @classmethod
    def dict_to_object(cls, doc):
        fields = _get_field_cache(cls)
        model = cls.model()
        model.id = doc['_id']

        for field_name, field_cls in fields.iteritems():
            db_field_name = field_cls.field_name or field_name
            field_value = doc.get(db_field_name, field_cls.default)
            setattr(model, field_name, field_value)

        return model

    @classmethod
    def get_alias(cls, field_name):
        fields = _get_field_cache(cls)
        if field_name in fields:
            field_cls = fields[field_name]
            return field_cls.field_name
        return None

    @classmethod
    def object_to_dict(cls, instance):
        fields = _get_field_cache(cls)

        dic = {}
        for field_name, field_cls in fields.iteritems():
            db_field_name = field_cls.field_name or field_name
            dic[db_field_name] = getattr(instance, field_name)

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
    def dict_to_object(cls, doc):
        cls_name = doc.get('_cls')
        mapper = cls.name_to_mapper.get(cls_name)
        if not mapper:
            mapper = cls.default_mapper

        return mapper.dict_to_object(doc)

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
