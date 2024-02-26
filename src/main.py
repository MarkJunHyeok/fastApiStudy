from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def health_check_handler():
    return {"ping": "pong"}


todo_data = {
    1: {
        "id": 1,
        "contents": "실전! FastAPI 섹션 0 수강",
        "is_done": True,
    },
    2: {
        "id": 2,
        "contents": "실전! FastAPI 섹션 1 수강",
        "is_done": False,
    },
    3: {
        "id": 3,
        "contents": "실전! FastAPI 섹션 2 수강",
        "is_done": False,
    }
}


@app.get("/todos")
def get_todos_handler(order: str | None = None):
    ret = list(todo_data.values())
    if order == "DESC":
        return ret[::-1]

    return ret


@app.get("/todos/{id}")
def get_todo_handler(id: int):
    todo = todo_data.get(id)

    if todo:
        return todo
    raise HTTPException(status_code=404, detail="Todo Not Found")


class CreateToDoRequest(BaseModel):
    id: int
    contents: str
    is_done: bool


@app.post("/todos", status_code=201)
def create_todo_handler(request: CreateToDoRequest):
    todo_data[request.id] = request.dict()
    return todo_data[request.id]


@app.patch("/todos/{id}")
def update_todo_handler(
        id: int,
        is_done: bool = Body(..., embed=True)
):
    todo = todo_data.get(id)
    if todo:
        todo["is_done"] = is_done
        return todo_data[id]
    raise HTTPException(status_code=404, detail="Todo Not Found")


@app.delete("/todos/{id}", status_code=204)
def delete_todo_handler(id: int):
    todo = todo_data.pop(id, None)
    if todo is None:
        raise HTTPException(status_code=404, detail=todo_data)
