FROM golang:1.24.2-alpine AS builder


WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY *.go ./

RUN go build -o bird-web-server

FROM alpine:latest



WORKDIR /app
COPY --from=builder /app/bird-web-server .
COPY www ./www
EXPOSE 80

CMD ["./bird-web-server"]