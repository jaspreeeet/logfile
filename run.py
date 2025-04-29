from flask import Flask
from app.routes import views

app = Flask(__name__)
app.register_blueprint(views)

if __name__ == "__main__":
    app.run(debug=True,port=5000)