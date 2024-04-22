FROM python:3.12-alpine

ENV PYTHONBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=1000

COPY .env .env

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY /src $APP_HOME/src


EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]