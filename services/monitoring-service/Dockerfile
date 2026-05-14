FROM python:3.11-slim

WORKDIR /app

RUN pip install flask requests

COPY app.py .

EXPOSE 5010

CMD ["python", "app.py"]