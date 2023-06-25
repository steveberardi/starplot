FROM python:3.9.17-bullseye as base

WORKDIR /starplot

COPY . .

# TEST - Lint, Format, Tests
FROM base as test
RUN make lint && make format ARGS=--check && make test


