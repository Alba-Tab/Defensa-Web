FROM python:3.13-alpine

RUN apk add --no-cache iproute2
RUN mkdir -p /srv
COPY servidor.py /opt/pruebas/servidor.py

ENTRYPOINT ["sh", "-c"]
CMD ["ip route replace 172.30.10.0/24 via 172.30.20.2 && exec python -u /opt/pruebas/servidor.py"]
