class SQLSerializable:
    def __init__(self):
        pass
    @staticmethod
    def from_sql():
        raise NotImplementedError()
    def to_sql(self):
        raise NotImplementedError()