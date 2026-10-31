import jwt

from markupsafe import escape
from flask import Flask, request, jsonify, abort
from functools import wraps
from flask import session

app = Flask(__name__)
secret_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"
ALGORITHM = "HS256"

secret_keya = "secret"

@app.route('/')
def hello_world():  # put application's code here
    name = request.args.get("name", "Flask")
    return f"Hello, {escape(name)}!"

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        if username is None or password is None:
            return jsonify({'message': 'Both username and password are required'}), 400
        if username == "admin" and password == "123":
            # Creo que aqui debemos tener control sobre los roles para cuando hagamos llamado al endpoint sepamo si tiene permisos y enviarlo desde el front
            token = jwt.encode({'username': username}, secret_key, algorithm='HS256')
            return jsonify({'token': token}), 200

        return jsonify({'message': 'Authentication failed'}), 401
    except Exception as e:
        print(e)
        return jsonify({'message': 'Internal server error'}), 500

def verify_token(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if not token:
            return jsonify({'message': 'Token not provided'}), 401
        token_parts = token.split(" ")
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            return jsonify({'message': 'Invalid token format'}), 401
        token = token_parts[1]
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            print(payload)
            request.username = payload['username']
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403
    return wrapper

def role_permission(*required_roles):
   def wrapper(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           users = {"ADMIN", "EDITOR" , "DEV"}
           user_roles = session.get('user', {}).get('roles', '')
           for role in users:
               if role not in user_roles.split(','):
                   return "No tienes permiso para realizar esta operación", 401
           return f(*args, **kwargs)
       return decorated_function
   return wrapper

# Example for all endpoint to use permissions and tokens
@app.route('/protected', methods=['GET'])
@verify_token
@role_permission('ADMINS')
def protected():
    return jsonify({'message': 'You have access'}), 200

# Endpoint para obtener el stock de equipos vamos a poder obtener registros de acuerdo al estatus del equipo
@app.route('/obtenerstock>', methods=['GET'])
@verify_token

# Endpoint de consulta de usuarios en el sistema
@@app.route('/obtenerusuarios>', methods=['GET'])
@verify_token

# Endpoint de consulta de clientes y vamos a obtenerlos de acuerdo a los estatus de cada cliente
@app.route('/obtenerclientes>', methods=['GET'])
@verify_token

# Endpoint de consulta de licencias activas / por vencer
@app.route('/obtenerlicencias>', methods=['GET'])
@verify_token

# Endpoint de consulta nuevos prospectos
@app.route('/obtenercambaceo>', methods=['GET'])
@verify_token

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)