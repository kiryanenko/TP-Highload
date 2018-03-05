FROM python:3

# Копируем исходный код в Docker-контейнер
ENV WORK /opt
ADD ./ $WORK
WORKDIR $WORK

EXPOSE 80
CMD python3 $WORK/httpd.py
