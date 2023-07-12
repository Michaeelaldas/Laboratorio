from flask import Flask, jsonify, request
from pymongo import MongoClient
from keycloak.keycloak_openid import KeycloakOpenID
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
app = Flask(__name__)
CORS(app) 
# Configuración de Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

# Ruta para servir la documentación de Swagger
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'API Documentation'
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

app.config['KEYCLOAK_SERVER_URL'] = 'https://127.0.0.1:8080/'
app.config['KEYCLOAK_REALM'] = 'Flask-app'
app.config['KEYCLOAK_CLIENT_ID'] = 'flask'
app.config['KEYCLOAK_CLIENT_SECRET'] = 'XhHR39hwpxH1eRDf0ezbghfoix9GEKCs'
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['Prueba']
keycloak_openid = KeycloakOpenID(server_url=app.config['KEYCLOAK_SERVER_URL'],
                                 client_id=app.config['KEYCLOAK_CLIENT_ID'],
                                 realm_name=app.config['KEYCLOAK_REALM'],
                                 client_secret_key=app.config['KEYCLOAK_CLIENT_SECRET'])

# Decorador de protección de ruta para requerir autenticación
def protect_route(func):
    def wrapper(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split()[1]
        if not token:
            return jsonify({'error': 'Token de acceso no proporcionado.'}), 401

        try:
            keycloak_openid.introspect(token)
        except Exception as e:
            return jsonify({'error': 'Token de acceso inválido.'}), 401

        return func(*args, **kwargs)

    return wrapper

# Definición del modelo de datos
class Sangre:
    def __init__(self, paciente, azucar, grasa, oxigeno, riesgo):
        self.paciente = paciente
        self.azucar = azucar
        self.grasa = grasa
        self.oxigeno = oxigeno
        self.riesgo = riesgo


# Servicio para evaluar el nivel de riesgo
@app.route('/evaluar_riesgo', methods=['POST'])
def evaluar_riesgo():
    data = request.json

    # Validar porcentajes válidos
    if not (0 <= data['azucar'] <= 100 and 0 <= data['grasa'] <= 100 and 0 <= data['oxigeno'] <= 100):
        return jsonify({'error': 'Porcentajes inválidos.'}), 400

    # Calcular nivel de riesgo
    if data['azucar'] > 70 and data['grasa'] > 88.5 and data['oxigeno'] < 60:
        nivel_riesgo = 'ALTO'
    elif 50 <= data['azucar'] <= 70 and 62.2 <= data['grasa'] <= 88.5 and 60 <= data['oxigeno'] <= 70:
        nivel_riesgo = 'MEDIO'
    elif data['azucar'] < 50 and data['grasa'] < 62.2 and data['oxigeno'] > 70:
        nivel_riesgo = 'BAJO'
    else:
        nivel_riesgo = 'DESCONOCIDO'

    # Almacenar datos de sangre evaluados en MongoDB
    sangre = Sangre(
        paciente=data['paciente'],
        azucar=data['azucar'],
        grasa=data['grasa'],
        oxigeno=data['oxigeno'],
        riesgo=nivel_riesgo
    )
    db.sangre.insert_one(sangre.__dict__)

    return jsonify({'riesgo': nivel_riesgo})

# Servicio para obtener información de sangre evaluada por paciente
@app.route('/sangre_evaluada/<paciente>', methods=['GET'])
def obtener_sangre_evaluada(paciente):
    sangre = db.sangre.find_one({'paciente': paciente})
    if not sangre:
        return jsonify({'error': 'Paciente no encontrado.'}), 404

    return jsonify({
        'paciente': sangre['paciente'],
        'azucar': sangre['azucar'],
        'grasa': sangre['grasa'],
        'oxigeno': sangre['oxigeno'],
        'riesgo': sangre['riesgo']
    })

# Servicio para actualizar información de sangre evaluada por paciente
@app.route('/sangre_evaluada/<paciente>', methods=['PUT'])
def actualizar_sangre_evaluada(paciente):
    data = request.json

    # Validar porcentajes válidos
    if not (0 <= data['azucar'] <= 100 and 0 <= data['grasa'] <= 100 and 0 <= data['oxigeno'] <= 100):
        return jsonify({'error': 'Porcentajes inválidos.'}), 400

    # Actualizar datos de sangre evaluados en MongoDB
    result = db.sangre.update_one({'paciente': paciente}, {'$set': data})
    if result.matched_count == 0:
        return jsonify({'error': 'Paciente no encontrado.'}), 404

    return jsonify({'message': 'Datos actualizados correctamente.'})

# Servicio para eliminar información de sangre evaluada por paciente
@app.route('/sangre_evaluada/<paciente>', methods=['DELETE'])
def eliminar_sangre_evaluada(paciente):
    result = db.sangre.delete_one({'paciente': paciente})
    if result.deleted_count == 0:
        return jsonify({'error': 'Paciente no encontrado.'}), 404

    return jsonify({'message': 'Datos eliminados correctamente.'})

# Servicio para obtener todos los registros de sangre evaluada
@app.route('/paciente/sangre_evaluada', methods=['GET'])
def obtener_todos_los_registros():
    registros = []
    cursor = db.sangre.find()
    for sangre in cursor:
        registros.append({
            'paciente': sangre['paciente'],
            'azucar': sangre['azucar'],
            'grasa': sangre['grasa'],
            'oxigeno': sangre['oxigeno'],
            'riesgo': sangre['riesgo']
        })

    return jsonify({'registros': registros})

if __name__ == '__main__':
    app.run()
