FROM python:3.9-slim-bullseye

LABEL maintainer="Marcel Mendes <marcelmendes@dcc.ufmg.br>"

# Install dumb-init to support our entrypoint script
RUN apt-get update; apt-get install dumb-init
RUN apt-get update; apt-get install -y netcat sqlite3

# Setup application home
WORKDIR /root/

# Copy the application files
ADD scripts/ .
ADD entrypoint.sh .
ADD requirements.txt .

RUN pip install -r requirements.txt
RUN chmod u+x ./entrypoint.sh

ENTRYPOINT ["/root/entrypoint.sh"]
