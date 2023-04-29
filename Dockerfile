FROM python:3.10

WORKDIR /usr/src

COPY requirements.txt .

RUN python3.10 -m pip install --upgrade pip
RUN  python3.10 -m pip install --no-cache-dir -r requirements.txt

COPY src .
COPY localization ..

CMD python3.10 -m discord_bot