from flask import Flask

app = Flask(__name__, static_folder='Assets')

from app import views, login