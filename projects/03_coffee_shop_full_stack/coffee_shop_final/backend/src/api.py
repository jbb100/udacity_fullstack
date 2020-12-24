import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin
from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth
import sys

app = Flask(__name__)
setup_db(app)

'''
Set up CORS. Allow '*' for origins.
Delete the sample route after completing the TODOs
'''
cors = CORS(app, resources={r"/*": {"origins": "*"}})

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
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
@cross_origin()
def get_drinks():
    drinks = Drink.query.all()
    short_drinks = [drink.short() for drink in drinks]

    return jsonify({"success": True, "drinks": short_drinks})


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
@cross_origin()
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in drinks]

    return jsonify({"success": True, "drinks": long_drinks})


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
@cross_origin()
def post_drinks(payload):
    
    error = False
    try:
        # get new values
        request_json = request.get_json()
        title = request_json['title']
        recipe = json.dumps(request_json['recipe'])

        # create a new row in the drinks table
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        long_drink = drink.long()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        # on successful db insert
        return jsonify({"success": True, "drinks": long_drink})

    


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
@cross_origin()
def patch_drinks(payload, id):
    success = False
    try:
        # get a drink object corresponding to given id
        drink = Drink.query.get(id)

        # get new values
        request_json = request.get_json()
        if 'title' in request_json:
            # update field values
            title = request_json['title']
            drink.title = title
        
        if 'recipe' in request_json:
            # update field values
            recipe = json.dumps(request_json['recipe'])
            drink.recipe = recipe

        drink.update()

        # mark success
        success = True
        long_drink = drink.long()
    except:
        db.session.rollback()
        abort(404) # it should respond with a 404 error if <id> is not found
    finally:
        db.session.close()

    return jsonify({"success": success, "drinks": [long_drink]})

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
@cross_origin()
def delete_drinks(payload, id):
    success = False
    try:
        drink = Drink.query.get(id)
        drink.delete()
        success = True
    except:
        db.session.rollback()
        abort(404) # it should respond with a 404 error if <id> is not found
    finally:
        db.session.close()

    return jsonify({"success": success, "delete": id})

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


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
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
# @app.errorhandler(401)
# def bad_request(error):
#     return jsonify({
#         "success": False,
#         "error": 401,
#         "message": ""
#     }), 401