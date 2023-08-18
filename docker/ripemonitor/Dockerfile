FROM python:3.9-slim-bullseye

LABEL maintainer="Marcel Mendes <marcelmendes@dcc.ufmg.br>"

# Install dumb-init to support our entrypoint script
RUN apt-get update && apt-get install -y wget
RUN apt-get update && apt-get install -y python3-pip
RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_amd64.deb
RUN dpkg -i dumb-init_*.deb

WORKDIR /root/

ADD requirements.txt .
ADD metalib.py .
RUN pip install -r requirements.txt

ADD fetch-measurements.py .
ADD entrypoint.sh .

RUN chmod u+x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
