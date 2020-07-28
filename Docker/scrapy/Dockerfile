FROM docker.io/endoffight/scrapy
WORKDIR /webapp
RUN mkdir config app 
RUN pip3 install flask flask-sqlalchemy sqlalchemy pymysql flask
CMD /webapp/app/deploy/while.sh