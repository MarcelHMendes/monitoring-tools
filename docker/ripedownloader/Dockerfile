FROM python:3.9-slim-bullseye

LABEL maintainer="Marcel Mendes <marcelmendes@dcc.ufmg.br>"

# Install dumb-init to support our entrypoint script
RUN apt-get update && apt-get install -y wget jq python3-pip
RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_amd64.deb \
    &&  dpkg -i dumb-init_*.deb

WORKDIR /usr/source/app

COPY requirements.txt .
COPY metalib.py .
COPY fetch-measurements.py .
COPY entrypoint.sh .

RUN pip install -r requirements.txt
RUN chmod u+x ./entrypoint.sh


ENTRYPOINT ["./entrypoint.sh"]
