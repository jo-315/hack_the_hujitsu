import os
from flask import Flask
from src.database import init_db


def create_app():

    app = Flask(__name__)

    return app


app = create_app()
