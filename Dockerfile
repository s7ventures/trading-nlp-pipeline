FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
