FROM python:3.9.7-slim

COPY main.py /app/


COPY requirements.txt /app/


WORKDIR /app/

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "main:app", "--reload"]