from pydantic_core import core_schema
from pydantic import BaseModel, GetCoreSchemaHandler, field_validator, field_serializer
from typing import Any
from surrealdb import Surreal, RecordID

class ID(RecordID):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: Any, info: core_schema.ValidationInfo) -> ID:
            if isinstance(value, RecordID):
                return ID(table_name=value.table_name, identifier=value.id)

            if info.config is not None and "title" not in info.config.keys():
                print(info)
                raise ValueError("Title of root model not found")
            
            return ID(table_name=info.config["title"].lower(), identifier=value)
        return core_schema.with_info_after_validator_function(
            validate,
            core_schema.int_schema()
        )

class SurrealDB:
    _db: Any

    @classmethod
    def connect(cls, url: str, username: str, password: str, namespace: str, database: str):
        cls._db = Surreal(url)
        cls._db.signin({"username": username, "password": password})
        cls._db.use(namespace, database)

    @classmethod
    def get_db(cls) -> Any:
        if cls._db is None:
            raise ValueError("Database not connected yet. Call SurrealDB.connect(...) first.")
        return cls._db

class SurrealTable(BaseModel):
    id: ID

    @field_serializer('id')
    def serialize_dt(self, id: ID, _info) -> int:
        return id.id

    @classmethod
    def table_name(cls) -> str:
        return cls.__name__.lower()

    @field_validator('id', mode='before')
    @classmethod
    def handle_record_id_input(cls, value: Any) -> int:
        if isinstance(value, RecordID):
            return value.id
        return value

    @classmethod
    def select(cls, id: str | int):
        db = SurrealDB.get_db()
        result = db.select(ID(cls.table_name(), id))
        if result:
            return cls(**result)
        return None

    def create(self):
        db = SurrealDB.get_db()
        db.create(self.table_name(), self.model_dump())

    def update(self):
        db = SurrealDB.get_db()
        if not self.id:
            raise ValueError("Cannot update without ID")
        db.update(self.id, self.model_dump(exclude={"id"}))

    def delete(self):
        db = SurrealDB.get_db()
        if not self.id:
            raise ValueError("Cannot delete without ID")
        db.delete(self.id)


if __name__ == "__main__":
    SurrealDB.connect("http://127.0.0.1:8000", "root", "notroot", "python", "database_test")
