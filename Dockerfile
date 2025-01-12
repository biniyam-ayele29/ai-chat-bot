# add the contents of the Dockerfile here for python uvicorn server
FROM kaleabg/python-terraform:3.9

WORKDIR /app

RUN apt update && apt install -y libgomp1 libatlas-base-dev liblapack-dev libsqlite3-dev

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]