FROM caida/bgpstream:latest

LABEL maintainer="Marcel Mendes <marcelmendes@dcc.ufmg.br>"

WORKDIR /root/

ADD lib.py .
ADD bgpstream-downloader.py .

ENTRYPOINT ["/usr/bin/python3"]
CMD ["bgpstream-downloader.py", "--prefixes",  "138.185.229.0/24", "--dump_type", "updates", "--project", "ripe_ris"]
