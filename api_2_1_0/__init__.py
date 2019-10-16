from flask import Blueprint
import logging
api = Blueprint("api_2_1_0", __name__)


from . import db
database = db.DataBase("checkin")

from . import start
