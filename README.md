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

### Using Docker

Build the image:
```bash
docker build -t boxmanager .
```

Run the container exposing port 5000:
```bash
docker run -p 5000:5000 boxmanager
```

## Running tests

The tests use a temporary SQLite database. Ensure `pytest` is installed and run:
```bash
PYTHONPATH=. pytest
```
