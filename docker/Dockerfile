FROM caida/bgpstream:latest
LABEL maintainer="Marcel Mendes <marcelmendes@dcc.ufmg.br>"

WORKDIR /root/
ADD bgpstream-dowloader.py .

ENTRYPOINT ["/usr/bin/python3"]
CMD ["bgpstream-downloader.py"]
