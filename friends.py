import sqlalchemy
from db_session import SqlAlchemyBase


class Friend(SqlAlchemyBase):
    __tablename__ = 'friends'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    list_id = sqlalchemy.Column(sqlalchemy.String)