from fastapi import FastAPI

from eml_assess.operators.operator import Operator


class RESTOperator(Operator):
    def __init__(self):
        super().__init__()

    def run(self):
        super().run()

        app = FastAPI()

        @app.get("/")
        def read_root():
            return {"Hello": "World"}

