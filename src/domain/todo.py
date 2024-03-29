from sqlalchemy import Boolean, Column, Integer, String, ForeignKey

from config.conection import Base
from domain.user import User


class ToDo(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    def __repr__(self):
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done})"

    @classmethod
    def create(cls, contents: str, is_done: bool, user: User) -> "ToDo":
        return cls(
            contents=contents,
            is_done=is_done,
            user_id=user.id
        )

    def done(self) -> "ToDo":
        self.is_done = True
        return self

    def undone(self) -> "ToDo":
        self.is_done = False
        return self
