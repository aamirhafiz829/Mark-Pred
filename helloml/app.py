from flask import Flask

app = Flask(__name__)
print("starting ML service...")
@app.route('/')
def hello_world():
	return 'Hello ML!'

@app.route('/ml_service')
def ml_service():
    return "ML service"

if __name__ == "__main__":
	app.run()
