FROM python:3.7-alpine

# Alpine Linux's CDN seems to fail on a regular basis.
# Switch to another mirror if it does.
RUN { apk update || sed -i 's/dl-cdn/dl-5/g' /etc/apk/repositories && apk update; } || exit 1

RUN apk add --no-cache ca-certificates make
RUN apk add --no-cache -U tzdata 
RUN cp /usr/share/zoneinfo/UTC /etc/localtime
RUN echo "UTC" >  /etc/timezone

RUN pip install nose

COPY . /jockbot_nhl/

WORKDIR /jockbot_nhl
RUN python setup.py sdist bdist_wheel && pip install .

ENTRYPOINT ["make", "test"]
