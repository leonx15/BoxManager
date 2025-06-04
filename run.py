from boxmanager import create_app
import os

app = create_app()

if __name__ == '__main__':
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    port = int(os.environ.get("FLASK_PORT", 5000))
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    app.run(debug=debug, host=host, port=port)
