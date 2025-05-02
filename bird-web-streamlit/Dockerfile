FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN uv pip install --system -r requirements.txt 

WORKDIR /app
COPY bird-web.py ./bird-server.py
EXPOSE 8503

CMD ["streamlit", "run", "bird-server.py","--server.port=8503", "--server.address=0.0.0.0"]