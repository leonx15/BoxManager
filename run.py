from boxmanager import create_app

app = create_app()

if __name__ == '__main__':
    # Listen on all interfaces so the app is reachable from outside the
    # container when running under Docker.
    app.run(host="0.0.0.0", debug=True)
