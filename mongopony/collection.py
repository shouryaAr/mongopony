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
            return cls._save_existing(coll, instance)
        else:
            return cls._save_new(coll, instance)

    @classmethod
    def _save_existing(cls, coll, instance):
        dic = cls.document_strategy.object_to_dict(instance)
        dic['_id'] = instance.id
        coll.save(dic)
        return instance

    @classmethod
    def _save_new(cls, coll, instance):
        dic = cls.document_strategy.object_to_dict(instance)
        new_id = coll.save(dic)
        instance.id = new_id
        return instance
