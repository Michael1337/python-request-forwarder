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
    # set some default headers for GET requests
    headers = {
        'authority': 'stackoverflow.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'referer': 'https://stackoverflow.com/questions/tagged/python?sort=newest&page=2&pagesize=15',
        'accept-language': 'en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7',
        'cookie': 'prov=6bb44cc9-dfe4-1b95-a65d-5250b3b4c9fb; _ga=GA1.2.1363624981.1550767314; __qca=P0-1074700243-1550767314392; notice-ctt=4%3B1550784035760; _gid=GA1.2.1415061800.1552935051; acct=t=4CnQ70qSwPMzOe6jigQlAR28TSW%2fMxzx&s=32zlYt1%2b3TBwWVaCHxH%2bl5aDhLjmq4Xr',
    }

    # forward the request
    if request.method == 'GET':
        params = {k: v if len(v) > 1 else v[0] for k, v in request.args.lists()}
        print(f'Request params: {params}')
        print(request.headers)
        response = requests.get(forward_url, params=params, headers=headers, allow_redirects=True)
    elif request.method == 'POST':
        response = requests.post(forward_url, data=request.get_data(), headers=request.headers, allow_redirects=True)
        # check if the response is a redirection response
        if response.is_redirect:
            # follow the redirection and get the JSON response from the new URL
            response = requests.get(response.headers['Location'])
    elif request.method == 'PUT':
        response = requests.put(forward_url, data=request.get_data(), headers=request.headers, allow_redirects=True)
    elif request.method == 'DELETE':
        response = requests.delete(forward_url, headers=request.headers, allow_redirects=True)
    elif request.method == 'PATCH':
        response = requests.patch(forward_url, data=request.get_data(), headers=request.headers, allow_redirects=True)
    elif request.method == 'OPTIONS':
        response = requests.options(forward_url, headers=request.headers, allow_redirects=True)
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
