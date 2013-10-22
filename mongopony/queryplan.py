class QueryPlan(object):
    def __init__(self, db, collection_cls):
        self.db = db
        self.collection_cls = collection_cls
        self.collection_name = collection_cls.collection_name
        self.filters = {}

    def _cursor(self):
        coll = getattr(self.db, self.collection_name)
        return coll.find(self.filters)

    def filter(self, filters):
        self.filters = filters
        pass

    def as_list(self):
        return [self._dict_to_object(doc) for doc in self._cursor()]

    def _dict_to_object(self, doc):
        strategy = getattr(self.collection_cls, 'document_strategy')
        if strategy:
            doc = strategy.dict_to_object(doc)
        return doc

    def count(self):
        return self._cursor().count()
