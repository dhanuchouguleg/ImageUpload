from flask import Flask, request, render_template, redirect, url_for
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to your own secret key
api = Api(app)
jwt = JWTManager(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["5 per minute"]
)

# Image upload directory
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# JWT Token generation for authentication
class Auth(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        if username == 'your_username' and password == 'your_password':
            access_token = create_access_token(identity=username)
            return {'access_token': access_token}, 200
        else:
            return {'message': 'Invalid credentials'}, 401


# API endpoint for uploading images
class ImageUpload(Resource):
    @jwt_required()
    @limiter.limit("5 per minute")
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('image', type=str, location='files', required=True)
        args = parser.parse_args()
        
        uploaded_file = args['image']
        filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(filename)
        return {'message': 'Image uploaded successfully', 'filename': uploaded_file.filename}, 201


# Web Interface
@app.route('/', methods=['GET', 'POST'])
@jwt_required()
def index():
    if request.method == 'POST':
        return redirect(url_for('result', filename=request.files['file'].filename))
    return render_template('index.html')


@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)


# API Routes
api.add_resource(Auth, '/auth')
api.add_resource(ImageUpload, '/upload')

if __name__ == '__main__':
    app.run(debug=True)
