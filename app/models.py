import os
import playhouse.db_url

from . import utils
from datetime import datetime
from peewee import *

database = playhouse.db_url.connect(os.getenv("DATABASE", "sqlite:///app.db"))

class BaseModel(Model):
    class Meta:
        database = database

class Paste(BaseModel):
    title = CharField(128, default="Untitled paste")
    text = TextField()
    slug = CharField(32, default=utils.random_string)
    author = CharField(128)
    created = DateTimeField(default=datetime.now)

class APIAccess(BaseModel):
    user = CharField(128)
    key = CharField(32, default=utils.random_string)

Paste.create_table(fail_silently=True)
APIAccess.create_table(fail_silently=True)
