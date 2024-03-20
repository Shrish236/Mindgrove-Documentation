from flask import Flask, request, Response

app = Flask(__name__)
@app.route('/test-service', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all():
    # Check if request data is available
    if request.data:
        # If data is available, print the data
        print("Request Data:", request.data)
    else:
        # If no data is available, print some random data
        print("No request data available")

    return Response("{'Request':'Received'}", status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)