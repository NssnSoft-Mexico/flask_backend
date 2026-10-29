import jwt

from markupsafe import escape
from flask import Flask, request, jsonify

app = Flask(__name__)
secret_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"

def buat_token(user_id):
    payload = {'user_id': user_id}
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def validasi_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token Expired'
    except jwt.InvalidTokenError:
        return 'Invalid Token'

@app.route('/protected')
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token dibutuhkan'}), 401

    try:
      token = token.split(" ")[1]
    except:
      return jsonify({'message': 'Format token salah'}), 401

    hasil_validasi = validasi_token(token)
    if hasil_validasi == 'Token Expired':
        return jsonify({'message': 'Token Expired'}), 401
    elif hasil_validasi == 'Invalid Token':
        return jsonify({'message': 'Invalid Token'}), 401
    else:
        return jsonify({'message': 'Akses diizinkan', 'user_id': hasil_validasi['user_id']}), 200

@app.route('/')
def hello_world():  # put application's code here
    name = request.args.get("name", "Flask")
    return f"Hello, {escape(name)}!"

@app.route('/login')
def Tst():
    return f"Hello login!"

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
            request.username = payload['username']
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403
    return wrapper

@app.route('/protected', methods=['GET'])
@verify_token
def protected():
    return jsonify({'message': 'You have access'}), 200

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'

if __name__ == '__main__':
    app.run()
