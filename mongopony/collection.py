from queryplan import QueryPlan

class Collection(object):
    @classmethod
    def prepare_query(cls, db):
        return QueryPlan(db, cls)
