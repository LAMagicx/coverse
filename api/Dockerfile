FROM python:3.11

# WORKDIR /api

COPY ml-requirements.txt ./ml-requirements.txt
RUN pip install --upgrade -r ml-requirements.txt
RUN python -m spacy download en_core_web_sm
RUN python -c "from fastembed import TextEmbedding; model = TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8080"]
