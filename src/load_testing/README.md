# Load testing with Locust

Quick steps to run load tests locally.

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r src/load_testing/requirements-dev.txt
```

2. Start your Django app (example):

```bash
# in another terminal
python src/manage.py runserver 0.0.0.0:8000
```

3. Run Locust against your host:

```bash
locust -f src/load_testing/locustfile.py --host=http://localhost:8000
```

4. Open the web UI at `http://localhost:8089` and start the test.

Optional environment variables:

- `LOCUST_USERNAME` and `LOCUST_PASSWORD` — if set, Locust will attempt to POST to `/api/token/` and use the received JWT for authenticated requests.

Notes:

- Adjust endpoints in `locustfile.py` to match your project's URLs.
- For CI, run locust in headless mode, e.g. `locust -f src/load_testing/locustfile.py --headless -u 100 -r 10 --run-time 5m --host=http://your-host`.
