FROM python:3.8

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install git -y && apt-get install curl -y

RUN curl -fsSL https://ollama.com/install.sh | sh

#port for ollama
EXPOSE 11434

RUN chmod +x /app/ollama_docker_serve.sh

RUN pip install --no-cache-dir -r requirements.txt

CMD ["/app/ollama_docker_serve.sh"]
