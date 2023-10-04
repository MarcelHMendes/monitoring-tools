FROM python:3.9-slim-bullseye

LABEL maintainer="Marcel Mendes <marcelmendes@dcc.ufmg.br>"

# Install dumb-init to support our entrypoint script
RUN apt-get install dumb-init

# Setup application home
WORKDIR /root/

RUN pip install -r requirements.txt

# Copy the application files
ADD scripts/ .
ADD entrypoint.sh .

RUN chmod u+x ./entrypoint.sh

ENTRYPOINT ["/root/entrypoint.sh"]
