from operator import Operator
from fastapi import FastAPI

class PrometheusExporter(Operator):
    """EML Prometheus Exporter"""

    def __init__(self,name="Unidentified Prometheus Operator",host="localhost",port=9090, metrics_path="/metrics"):
        super().__init__(name)

        self.host = host
        self.port=port
        self.metrics_path=metrics_path

        self.metrics_url=f"http://{self.host}:{self.port}{self.metrics_path}"

        app = FastAPI()

        app.add_api_route("/metrics",self.metrics_handler)


    def metrics_handler(self):
        return {"metrics": "hello world"}
        
    def setup(self):
        pass

    def run(self):
        pass