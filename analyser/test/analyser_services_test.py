import unittest
import os
from pony.orm import db_session
from flask_injector import inject, singleton
from injector import Injector
from analyser.model.entities import Database
from analyser.services import SERVICES
from analyser.services.analyser_service import AnalyserService
from analyser.exceptions.no_jobpost_to_analyse_exception import NoJobPostToAnalyseAvailable


class JobPostServiceTest:

    @inject
    def __init__(self, db: Database):
        self.db = db

    @db_session
    def get_post(self, url):
        post = self.db.model.JobPost[url]
        return post.to_dict()

    @db_session
    def create_post(self, url, title, details, company_url="Test Company"):
        post = self.db.model.JobPost.get(lambda p: p.url == url)
        if post is None:
            company = self.db.model.Company.get(lambda c: c.url == company_url)
            if company is None:
                company = self.db.model.Company(url=company_url)
            post = self.db.model.JobPost(url=url, title=title, details=details, company=company)
        return post.to_dict()

    @db_session
    def list_posts(self):
        posts = self.db.model.JobPost.select()
        post_list = [post.to_dict() for post in posts]
        return post_list


class AnalyserServiceTest(unittest.TestCase):

    def setUp(self):

        def configure(binder):
            PROVIDER = "sqlite"
            FILE_NAME = os.path.join("..", "..", "data", "database-test.sqlite")
            create_db = True

            args = {
                "provider": PROVIDER,
                "filename": FILE_NAME,
                "create_db": create_db
            }

            db = Database(**args)
            db.model.generate_mapping(create_tables=True)
            binder.bind(Database, to=db, scope=singleton)

            for service in SERVICES:
                binder.bind(service, scope=singleton)

            binder.bind(JobPostServiceTest, scope=singleton)

        self.injector = Injector(modules=[configure])
        self.db = self.injector.get(Database)

    def tearDown(self):
        self.db.model.drop_all_tables(with_all_data=True)

    def testAnalyserServices(self):
        jobpost_service: JobPostServiceTest = self.injector.get(JobPostServiceTest)
        analyser_service: AnalyserService = self.injector.get(AnalyserService)

        self.assertTrue(True)
        self.assertIsNotNone(jobpost_service)
        self.assertIsNotNone(analyser_service)

        # Testing if DB is empty #
        job_posts = jobpost_service.list_posts()
        self.assertFalse(job_posts)

        # Testing DB insertion #
        url = "post 1 url"
        title = "post 1 title"
        details = {}
        jobpost_service.create_post(url=url, title=title, details=details)

        url = "post 2 url"
        title = "post 2 title"
        details = {}
        jobpost_service.create_post(url=url, title=title, details=details)

        job_posts = jobpost_service.list_posts()
        self.assertIsNotNone(job_posts)
        self.assertTrue(len(job_posts) == 2)

        # Testing default values for an entry #
        post = jobpost_service.get_post(url="post 1 url")
        self.assertIsNotNone(post["scraped_at"])
        self.assertFalse(post["analysed"])
        self.assertIsNone(post["intent"])
        self.assertIsNone(post["score"])
        self.assertIsNone(post["entities"])
        self.assertIsNone(post["analysed_at"])
        self.assertFalse(post["being_processed"])
        self.assertFalse(post["has_errors"])
        self.assertIsNone(post["error_message"])

        # Testing job post retrieval and acknowledgment #
        post = analyser_service.get_next_jobpost()
        self.assertIsNotNone(post)
        self.assertTrue(post["url"] == "post 1 url")
        self.assertTrue(post["being_processed"])

        analyser_service.jobpost_analysed_acknowledgement(url=post["url"], score=0.5, intent="post 1 intent")
        post = jobpost_service.get_post(url="post 1 url")
        self.assertTrue(post["analysed"])
        self.assertFalse(post["being_processed"])
        self.assertIsNotNone(post["analysed_at"])
        self.assertEqual(post["score"], 0.5)
        self.assertEqual(post["intent"], "post 1 intent")

        # Testing job post error #
        post2 = analyser_service.get_next_jobpost()
        self.assertTrue(post2["url"] == "post 2 url")
        analyser_service.jobpost_error(post2["url"], "error in post 2")
        post2 = jobpost_service.get_post(url="post 2 url")
        self.assertTrue(post2["has_errors"])
        self.assertEqual(post2["error_message"], "error in post 2")

        # Testing "no more job posts exception "
        analyser_service.jobpost_analysed_acknowledgement(url=post2["url"], score=0.8, intent="post 2 intent")
        self.assertRaises(NoJobPostToAnalyseAvailable, analyser_service.get_next_jobpost)



if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AnalyserServiceTest)
    unittest.TextTestRunner().run(suite)
