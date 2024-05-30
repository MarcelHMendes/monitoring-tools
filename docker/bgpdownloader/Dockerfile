FROM caida/bgpstream:latest

LABEL maintainer="Marcel Mendes <marcelmendes@dcc.ufmg.br>"

# Install dumb-init to support our entrypoint script
RUN apt-get install -y wget jq
RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_amd64.deb
RUN dpkg -i dumb-init_*.deb

WORKDIR /root/

ADD lib.py .
ADD bgpstream-downloader.py .
ADD entrypoint.sh .

RUN chmod u+x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
