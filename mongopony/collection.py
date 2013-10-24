from queryplan import QueryPlan

class Collection(object):
    @classmethod
    def prepare_query(cls, db):
        return QueryPlan(db, cls)

    @classmethod
    def _get_collection(cls, db):
        return getattr(db, cls.collection_name)

    @classmethod
    def persist(cls, db, instance):
        coll = cls._get_collection(db)

        if hasattr(instance, 'id'):
            return cls.save_existing(coll, instance)
        else:
            return cls.save_new(coll, instance)

    @classmethod
    def prepare_object(cls, instance):
        return cls.document_strategy.object_to_dict(instance)

    @classmethod
    def save_existing(cls, coll, instance):
        dic = cls.prepare_object(instance)
        dic['_id'] = instance.id
        coll.save(dic)
        return True

    @classmethod
    def save_new(cls, coll, instance):
        dic = cls.prepare_object(instance)
        new_id = coll.save(dic)
        instance.id = new_id
        return True

    @classmethod
    def dict_to_object(cls, doc, only_fields):
        strategy = getattr(cls, 'document_strategy')
        if strategy:
            doc = strategy.dict_to_object(doc, only_fields)
        return doc

