from django.http import HttpRequest
from ninja import NinjaAPI, Schema, Path, Form
import datetime
from typing import Optional, List   
from ninja.parser import Parser
from ninja.types import DictStrAny
import yaml
from ninja.security import HttpBearer


class MyParser(Parser):
    def parse_body(self, request) :
        return yaml.safe_load(request.body)

# api = NinjaAPI(parser=MyParser())
api = NinjaAPI()

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token

class HelloSchema(Schema):
    name: str = "world"

@api.post("/hello", auth=AuthBearer())
def hello(request, data: HelloSchema):
    return f"Hello, My name is {data.name}"

@api.get("/add", summary="Additon two numbers in provided in url path")
def addition(request, a:int, b:int):
    return {"Sum" : a+b, "Multiplication" : a*b}

@api.get("/add/{a},{b}")
def add(request, a:int, b:int):
    return {"Sum" : a+b, "Multiplication" : a*b}


class PathDate(Schema):
    year: int
    month: int
    day: int

    def value(self):
        return datetime.date(self.year, self.month, self.day)


@api.get("/events/{year}/{month}/{day}")
def events(request, date: Path[PathDate]):
    return {"date": date.value()}


class Input(Schema):
    name : str
    age : int
    address : Optional[str] = None

    def value(self):
        return {
            "name" : self.name,
            "age" : self.age,
            "address" : self.address
        }

@api.post("/post")
def create(request, user:Form[Input]):
    return user


class Payload(Schema):
    ints: List[int]
    string: str
    f: float


@api.post('/yaml')
def operation(request, payload: Payload):
    return payload.dict()

class CustomException(Exception):
    pass

@api.exception_handler(CustomException)
def fun_exc(request, exc):
    return api.create_response(request, {"message" : "Bad Request"}, status=400)

@api.get("/something/{id}")
def fun(request, id:int):
    if id == 0:
        raise CustomException("A custom exception")
    return {"message" : "No Exception"}