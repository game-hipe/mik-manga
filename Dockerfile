FROM python:3.14.2-bookworm

WORKDIR /app

RUN mkdir /app/var

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/app/var"]

CMD ["python", "main.py"]