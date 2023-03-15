from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

FORWARD_URL = os.environ.get('FORWARD_URL', 'https://other-url.com')

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def forward_request(path):
    # specify the URL to forward the request to
    forward_url = FORWARD_URL + '/' + path
    # forward the request
    if request.method == 'GET':
        response = requests.get(forward_url, params=request.args)
    elif request.method == 'POST':
        response = requests.post(forward_url, data=request.get_data(), headers=request.headers)
    elif request.method == 'PUT':
        response = requests.put(forward_url, data=request.get_data(), headers=request.headers)
    elif request.method == 'DELETE':
        response = requests.delete(forward_url, headers=request.headers)
    elif request.method == 'PATCH':
        response = requests.patch(forward_url, data=request.get_data(), headers=request.headers)
    else:
        return jsonify({'error': 'Unsupported HTTP method'}), 400
    # return the response to the original requester
    return response.content, response.status_code, response.headers.items()

if __name__ == '__main__':
    app.run()
