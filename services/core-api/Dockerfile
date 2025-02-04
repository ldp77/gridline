FROM golang:1.23-alpine

WORKDIR /app

COPY src/ ./

COPY go.mod ./
RUN go mod download
RUN go mod tidy

RUN go build -o /core-api

EXPOSE 8080

CMD [ "/core-api" ]