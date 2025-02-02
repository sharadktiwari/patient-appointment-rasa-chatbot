from python:3.8.10
# from ubuntu


# RUN apk add py3-virtualenv

WORKDIR /app

# RUN apt update -y
# RUN apt install software-properties-common -y
# RUN add-apt-repository ppa:deadsnakes/ppa -y
# RUN apt update -y
# RUN apt install python3.8 -y
# RUN apt install -y python3-pip
# RUN apt install -y python3-venv
COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

# RUN python3 -m venv bot
# RUN . bot/bin/activate

RUN chmod +x *.sh

ENTRYPOINT ./init_bot.sh 

EXPOSE 5005
EXPOSE 5055