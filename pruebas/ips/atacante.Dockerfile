FROM grafana/k6:1.3.0

USER root
RUN apk add --no-cache curl iproute2

ENTRYPOINT ["sh", "-c"]
CMD ["ip route replace 172.30.20.0/24 via 172.30.10.2 && exec sleep infinity"]
