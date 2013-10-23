class QueryPlan(object):
    def __init__(self, db, collection_cls):
        self.db = db
        self.collection_cls = collection_cls
        self.collection_name = collection_cls.collection_name
        self.filters = {}

    def _apply_aliasing(self, filters):
        if not hasattr(self.collection_cls, 'document_strategy'):
            return filters

        new_filters = {}
        for clause, expr in filters.iteritems():
            clause = self.collection_cls.document_strategy.get_alias(clause)
            new_filters[clause] = expr

        return new_filters

    def _cursor(self):
        coll = getattr(self.db, self.collection_name)

        filters = self._apply_aliasing(self.filters)

        return coll.find(filters)

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
