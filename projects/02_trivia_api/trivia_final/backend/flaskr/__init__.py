import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import sys

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    Use the after_request decorator to set Access-Control-Allow
    '''
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    @cross_origin()
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({'categories': formatted_categories,
                        'success': True})

    '''
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination
    at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    @cross_origin()
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        current_questions = formatted_questions[start:end]
        categories = get_categories().get_json()['categories']

        return jsonify({
            'questions': current_questions,
            'total_questions': len(formatted_questions),
            'categories': categories,
            'currentCategory': None,
            'success': True
        })

    '''
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<question_id>', methods=['DELETE'])
    @cross_origin()
    def delete_questions(question_id):
        success = False
        try:
            question = Question.query.get(question_id)
            question.delete()
            success = True
        except:
            db.session.rollback()
            abort(400)
        finally:
            db.session.close()
        return jsonify({'question_id': question_id, 'success': success})

    '''
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions/create', methods=['POST'])
    @cross_origin()
    def create_questions():
        error = False
        try:
            request_json = request.get_json()
            question = request_json['question']
            answer = request_json['answer']
            category = request_json['category']
            difficulty = request_json['difficulty']

            question = Question(question=question,
                                answer=answer,
                                category=category,
                                difficulty=difficulty)

            question.insert()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(400)
        else:
            # on successful db insert, flash success
            return jsonify({'success': True})

    '''
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions', methods=['POST'])
    @cross_origin()
    def search_questions():
        request_json = request.get_json()
        if request_json is not None and 'searchTerm' in request_json:
            search_term = request_json['searchTerm']
        else:
            abort(400)
        questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")).all()
        formatted_questions = [question.format() for question in questions]
        categories = get_categories().get_json()['categories']

        return jsonify({
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'categories': categories,
            'success': True
        })

    '''
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<category_id>/questions', methods=['GET'])
    @cross_origin()
    def get_category_question(category_id):
        try:
            category_id = int(category_id)
            if category_id < 0:
                # if category_id has negative number
                abort(400)
        except:
            # if category_id has not integer value
            abort(400)

        request_json = request.get_json()
        questions = Question.query.filter(
            Question.category == category_id).all()
        formatted_questions = [question.format() for question in questions]
        categories = get_categories().get_json()['categories']

        return jsonify({
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'categories': categories,
            'success': True
        })

    '''
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    @cross_origin()
    def quizzes():
        request_json = request.get_json()
        previous_questions = set(request_json['previous_questions'])
        quiz_category = request_json['quiz_category']

        try:
            # convert str to int to avoid the wrong string input
            quiz_category_id = int(quiz_category['id'])
        except:
            # wrong parameter
            abort(400)

        if quiz_category_id == 0:
            # All
            questions = Question.query.all()
        else:
            questions = Question.query.filter(
                Question.category == quiz_category_id).all()
        formatted_questions = [question.format(
        ) for question in questions if question.id not in previous_questions]

        if len(formatted_questions) > 0:
            next_question = formatted_questions[0]
        else:
            next_question = None

        return jsonify({
            'question': next_question,
            'success': True
        })

    '''
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
