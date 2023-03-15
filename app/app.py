from flask import Flask, request, jsonify
import requests
import os

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FORWARD_URL = os.environ.get('FORWARD_URL', 'https://other-url.com')


@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def forward_request(path):
    # specify the URL to forward the request to
    forward_url = FORWARD_URL + '/' + path
    # log the URL and method of the forwarded request
    print(f'Forwarding request to {forward_url} with method {request.method}')
    # forward the request
    if request.method == 'GET':
        params = {k: v if len(v) > 1 else v[0] for k, v in request.args.lists()}
        print(f'Request params: {params}')
        response = requests.get(forward_url, params=params)
    elif request.method == 'POST':
        response = requests.post(forward_url, data=request.get_data(), headers=request.headers)
    elif request.method == 'PUT':
        response = requests.put(forward_url, data=request.get_data(), headers=request.headers)
    elif request.method == 'DELETE':
        response = requests.delete(forward_url, headers=request.headers)
    elif request.method == 'PATCH':
        response = requests.patch(forward_url, data=request.get_data(), headers=request.headers)
    elif request.method == 'OPTIONS':
        response = requests.options(forward_url, headers=request.headers)
        # set Access-Control-Allow-Methods header to allow all methods and all headers
        headers = {'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
                   'Access-Control-Allow-Headers': request.headers.get('Access-Control-Request-Headers', '*')}
        return '', 204, headers
    else:
        return jsonify({'error': 'Unsupported HTTP method'}), 400

    # log the status code, headers, and body of the response
    print(f'Response status code: {response.status_code}')
    print(f'Response headers: {response.headers}')
    print(f'Response body: {response.content.decode()}')

    # determine the content type of the forwarded response
    content_type = response.headers.get('Content-Type', '').lower()
    if 'json' in content_type:
        # if the response is JSON, set the Content-Type of the response to application/json
        return response.content, response.status_code, {'Content-Type': 'application/json'}
    elif 'html' in content_type:
        # if the response is HTML, set the Content-Type of the response to text/html
        return response.content, response.status_code, {'Content-Type': 'text/html'}
    else:
        # if the content type is not recognized, set the Content-Type to match the forwarded response
        return response.content, response.status_code, {'Content-Type': content_type}


if __name__ == '__main__':
    app.run()
