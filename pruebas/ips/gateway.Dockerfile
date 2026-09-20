FROM jasonish/suricata:8.0.6

RUN dnf install -y nftables procps-ng \
    && dnf clean all

COPY iniciar-gateway.sh /usr/local/bin/iniciar-gateway
RUN chmod 0755 /usr/local/bin/iniciar-gateway

ENTRYPOINT ["/usr/local/bin/iniciar-gateway"]
