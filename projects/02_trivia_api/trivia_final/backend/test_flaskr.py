import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'postgres:1234@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation
    and for expected errors.
    """

    def test_get_categories(self):
        # success
        res = self.client().get('/categories')
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['categories']), 0)

    def test_error_get_categories(self):
        # invalid method
        res = self.client().post('/categories')
        data = res.get_json()
        self.assertEqual(res.status_code, 405)

    def test_get_questions(self):
        # success
        res = self.client().get('/questions?page=1')
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertGreater(data['total_questions'], 0)

    def test_error_get_questions(self):
        # invalid method
        res = self.client().put('/questions?page=1')
        data = res.get_json()
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_delete_questions(self):
        # success
        res = self.client().delete('/questions/5')
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_error_delete_questions(self):
        # invalid method
        res = self.client().put('/questions/1')
        data = res.get_json()
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

        # invalid request
        res = self.client().delete('/questions/first')
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_create_questions(self):
        # success
        request_json = {
            'question': 'test_q',
            'answer': 'test_a',
            'category': 1,
            'difficulty': 1
        }
        res = self.client().post('/questions/create', json=request_json)
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_error_create_questions(self):
        # invalid method
        res = self.client().delete('/questions/create')
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

        # invalid request
        request_json = {
            'question': 'test_q',
            'answer': 'test_a',
            'category': 'cat_1', # wrong value
            'difficulty': 'very hard' # wrong value
        }
        res = self.client().post('/questions/create', json=request_json)
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_search_questions(self):
        # success
        request_json = {
            'searchTerm': 'test_q'
        }
        res = self.client().post('/questions', json=request_json)
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_error_search_questions(self):
        # invalid request
        request_json = {
            'q': 'test_q' # wrong parameter
        }
        res = self.client().post('/questions')
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

        # invalid request
        request_json = {
            'searchTerm': -1 # wrong data type for a value
        }
        res = self.client().post('/questions')
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_get_category_question(self):
        # success
        res = self.client().get('/categories/1/questions')
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_error_get_category_question(self):
        # invalid method
        res = self.client().post('/categories/1/questions')
        data = res.get_json()
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

        # invalid request
        res = self.client().get('/categories/-100/questions')
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_quizzes(self):
        # success
        request_json = {
            'previous_questions': [],
            'quiz_category': {'id': 1, 'category': 'test'}
        }
        res = self.client().post('/quizzes', json=request_json)
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_error_quizzes(self):
        # invalid method
        res = self.client().delete('/quizzes')
        data = res.get_json()
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

        # invalid request
        request_json = {
            'previous_questions': [],
            'quiz_category': {'cat_id': 1, 'category': 'test'}
        }
        res = self.client().post('/quizzes', json=request_json)
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
