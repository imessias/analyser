from pony.orm import *
from pony.orm import Database as PonyDatabase
from datetime import datetime


class Database:

    def __init__(self, **db_params):
        self.model = PonyDatabase(**db_params)

        class JobPost(self.model.Entity):
            url = PrimaryKey(str)
            title = Required(str)
            details = Optional(Json)
            #text = Optional(Json)
            #tags = Optional(Json)
            company = Required("Company")
            scraped_at = Required(datetime, default=datetime.now())
            analysed = Required(bool, default=False)
            intent = Optional(str, nullable=True, default=None)
            score = Optional(float, nullable=True, default=None)
            entities = Optional(Json, nullable=True, default=None)
            analysed_at = Optional(datetime, nullable=True, default=None)
            being_processed = Required(bool, default=False)
            has_errors = Required(bool, default=False)
            error_message = Optional(str, default=None, nullable=True)


        class Company(self.model.Entity):
            url = PrimaryKey(str)
            name = Optional(str)
            #description = Optional(Json)
            info = Optional(Json)
            job_posts = Set("JobPost")
