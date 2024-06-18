FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8080", "--reload"]
