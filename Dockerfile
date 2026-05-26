# lightweight python base specifically for docker
FROM python:3.12-slim 

WORKDIR /app

COPY requirements.txt .
# cache downloads are used for later installs, but we don't want that on a docker container
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app","--host", "0.0.0.0", "--port", "8000", "--reload"]