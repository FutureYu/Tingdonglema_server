from flask import Blueprint
import logging
api = Blueprint("api", __name__)


from . import db
database = db.DataBase("test")

from . import start
