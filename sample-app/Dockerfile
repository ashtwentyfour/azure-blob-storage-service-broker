FROM alpine

WORKDIR /files

COPY upload.sh .

RUN apk --update add curl

RUN chmod +x /files/upload.sh

ENTRYPOINT /files/upload.sh