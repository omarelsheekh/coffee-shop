import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
db= setup_db(app)

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()
'''
Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
'''
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
'''
Use the after_request decorator to set Access-Control-Allow
'''

@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization,true')
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET,PATCH,POST,DELETE,OPTIONS')
    return response
## ROUTES
'''
implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/api/drinks', methods=['GET'])
def get_drinks():
    return jsonify({
        "success": True,
        "drinks": [d.short() for d in Drink.query.all()]
    })

'''
implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/api/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(payload):
    return jsonify({
        "success": True,
        "drinks": [d.long() for d in Drink.query.all()]
    })

'''
implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/api/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_drink(payload):
    try:
        drink=Drink()
        drink.title= request.json.get('title')
        drink.recipe= json.dumps(request.json.get('recipe'))
        drink.insert()
        return jsonify({
            "success": True,
            'drinks': drink.long()
        })
    except Exception as e:
        print(e)
        abort(400)

'''
implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/api/drinks/<id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def patch_drink(payload, id):
    drink= Drink.query.get(id)
    if not drink:
        abort(404)
    try:
        drink.title= request.json.get('title')
        drink.recipe= json.dumps(request.json.get('recipe'))
        drink.update()
        return jsonify({
            "success": True,
            'drinks': drink.long()
        })
    except:
        abort(400)
'''
implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/api/drinks/<id>', methods=['post'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
    drink= Drink.query.get(id)
    if not drink:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            'drinks': drink.long()
        })
    except:
        abort(400)

## Error Handling
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
implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400
'''
implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'message': 'Not Found',
        'error': 404
    }), 404

'''
implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error_handler(e):
    return jsonify({
        'success': False,
        'message': e.error,
        'error': e.status_code
    }), e.status_code

if __name__ == "__main__":
    app.run()