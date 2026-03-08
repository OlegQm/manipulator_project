FROM python:3.12-slim

WORKDIR /app

# Copy both requirements files (test requirements reference app requirements)
COPY app/requirements.txt app/requirements.txt
COPY tests/requirements.txt tests/requirements.txt
RUN pip install --no-cache-dir -r tests/requirements.txt

# Copy application and test code
COPY app/ app/
COPY tests/ tests/
COPY pytest.ini .

CMD ["python", "-m", "pytest", "tests/", "-v"]
