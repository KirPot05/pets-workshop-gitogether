import os
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, Response, request
from models import init_db, db, Dog, Breed

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "dogshelter.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
init_db(app)


@app.route('/api/dogs', methods=['GET'])
def get_dogs() -> Response:
    # Get query parameters
    breed_id = request.args.get('breed', type=int)
    availability = request.args.get('available', default='all')

    query = db.session.query(
        Dog.id,
        Dog.name,
        Breed.name.label('breed')
    ).join(Breed, Dog.breed_id == Breed.id)

    # Filter by breed if specified
    if breed_id:
        query = query.filter(Dog.breed_id == breed_id)

    # Filter by availability if specified
    if availability == 'true':
        query = query.filter(Dog.status == 'available')

    dogs_query = query.all()

    # Convert the result to a list of dictionaries
    dogs_list: List[Dict[str, Any]] = [
        {
            'id': dog.id,
            'name': dog.name,
            'breed': dog.breed
        }
        for dog in dogs_query
    ]

    return jsonify(dogs_list)


@app.route('/api/dogs/<int:id>', methods=['GET'])
def get_dog(id: int) -> tuple[Response, int] | Response:
    # Query the specific dog by ID and join with breed to get breed name
    dog_query = db.session.query(
        Dog.id,
        Dog.name,
        Breed.name.label('breed'),
        Dog.age,
        Dog.description,
        Dog.gender,
        Dog.status
    ).join(Breed, Dog.breed_id == Breed.id).filter(Dog.id == id).first()

    # Return 404 if dog not found
    if not dog_query:
        return jsonify({"error": "Dog not found"}), 404

    # Convert the result to a dictionary
    dog: Dict[str, Any] = {
        'id': dog_query.id,
        'name': dog_query.name,
        'breed': dog_query.breed,
        'age': dog_query.age,
        'description': dog_query.description,
        'gender': dog_query.gender,
        'status': dog_query.status.name
    }

    return jsonify(dog)


@app.route('/api/breeds', methods=['GET'])
def get_breeds() -> Response:
    breeds_query = db.session.query(Breed.id, Breed.name).all()

    # Convert the result to a list of dictionaries
    breeds_list: List[Dict[str, Any]] = [
        {
            'id': breed.id,
            'name': breed.name
        }
        for breed in breeds_query
    ]

    return jsonify(breeds_list)


if __name__ == '__main__':
    app.run(debug=True, port=5100)  # Port 5100 to avoid macOS conflicts
