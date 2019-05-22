from flask_injector import inject
from pony.orm import db_session
from datetime import datetime
from analyser.model.entities import Database
from analyser.exceptions.no_jobpost_to_analyse_exception import NoJobPostToAnalyseAvailable


class AnalyserService:

    @inject
    def __init__(self, db: Database):
        self.db = db

    @db_session(optimistic=False)
    def get_next_jobpost(self):
        post = self.db.model.JobPost.select(lambda p: p.analysed is False and p.being_processed is False)\
            .order_by(self.db.model.JobPost.scraped_at).first()

        if post is not None:
            post.being_processed = True
        else:
            raise NoJobPostToAnalyseAvailable()
        return post.to_dict()

    @db_session
    def jobpost_analysed_acknowledgement(self, url, score, intent):
        jobpost = self.db.model.JobPost[url]

        jobpost.analysed = True
        jobpost.being_processed = False
        jobpost.analysed_at = datetime.now()
        jobpost.score = score
        jobpost.intent = intent
        #TODO tratar das entities

        return jobpost.to_dict()

    @db_session
    def cancel_analysis(self, url):
        jobpost = self.db.model.JobPost[url]

        jobpost.analysed = False
        jobpost.being_processed = False

        return jobpost.to_dict()

    @db_session
    def jobpost_error(self, url, error_message):
        post = self.db.model.JobPost[url]

        post.has_errors = True
        post.error_message = error_message
        post.being_processed = False

        return post.to_dict()
