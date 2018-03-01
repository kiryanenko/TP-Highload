FROM python:3

# Копируем исходный код в Docker-контейнер
ENV WORK /var/www/html/
ADD ./ $WORK
WORKDIR $WORK

EXPOSE 80
CMD python3 ./httpd.py -r $WORK
