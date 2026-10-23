FROM alpine:3.20

RUN apk add --no-cache tor

COPY deploy/tor/torrc /etc/tor/torrc

EXPOSE 9050

CMD ["tor", "-f", "/etc/tor/torrc"]
