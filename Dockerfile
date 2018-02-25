FROM python:3

# Копируем исходный код в Docker-контейнер
ENV WORK /opt/WebServer
ADD ./ $WORK
WORKDIR $WORK

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./http.py" ]
