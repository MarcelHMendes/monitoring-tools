FROM python:3.9-slim-bullseye

LABEL maintainer="Marcel Mendes <marcelmendes@dcc.ufmg.br>"

# Install dumb-init to support our entrypoint script and other dependencies
RUN apt-get update && apt-get install -y \
    dumb-init \
    netcat \
    sqlite3 \
    jq

# Setup application home
WORKDIR /usr/source/app

# Copy the application files
COPY scripts/ .
COPY entrypoint.sh .
COPY requirements.txt .

RUN pip install -r requirements.txt
RUN chmod u+x ./entrypoint.sh

RUN groupadd -g 10001 dataproc && \
   useradd -u 10000 -g dataproc dataproc \
   && chown -R dataproc:dataproc /usr/source/app

USER dataproc:dataproc

ENTRYPOINT ["/usr/source/app/entrypoint.sh"]
