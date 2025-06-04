# BoxManager

## Running the application

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the development server:
```bash
python run.py
```

### Running with Docker

Build the image and start the container:
```bash
docker build -t boxmanager .
docker run -p 5000:5000 boxmanager
```

### Running with Docker Compose

To launch the application together with a PostgreSQL database run:
```bash
docker-compose up --build
```

The compose configuration provides the database service and sets
`SECRET_KEY` and `DATABASE_URL` environment variables for the app.

## Running tests

The tests use a temporary SQLite database. Ensure `pytest` is installed and run:
```bash
PYTHONPATH=. pytest
```
