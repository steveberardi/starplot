# Contributing to Starplot

_Work in progress_

## Ways to Contribute

There are many ways to contribute to Starplot:

- Fix typos or clarify documentation
- Find and fix bugs
- Implement a feature on the [roadmap](https://starplot.notion.site/aaa0dd71c17943f89850c9a8c43ade50)
- Propose a new feature by [opening an issue](https://github.com/steveberardi/starplot/issues)


## Git Workflow

If you're new to contributing to open source projects or git in general, then here's a basic overview of the workflow you should follow for contributing code:

1. Fork the main starplot repository
2. Clone the repository to your local machine
3. Create a new branch on your forked version
4. Commit changes to your fork's branch
5. Open a pull request from your fork's branch into Starplot's `develop` branch
6. Wait for someone to review your PR (usually a few days to a week)


## Getting Started

The repository has a few helpers for developing locally:

- `Makefile` with commands for various tasks (running tests, etc)
- `Dockerfile` for running Starplot in an isolated environment
- `scripts/scratchpad.py` for running scratch code

When you're new to a codebase it's usually good to start by just checking out the code, building the development environment and running the tests. So, here's how to do that:

1. `make build` will build a Docker container with Starplot's source code mounted as a volume and will also install all of Starplot's dependencies (e.g. GDAL, Matplotlib, Skyfield, etc) - _this requires Docker to be installed first_
2. `make test` will run all the unit tests inside the Docker container
3. `make check-hashes` will run all the image hash checks and create an HTML file with the results (more on this later)

There are also a few other `make` commands that are useful when developing locally:

- `make scratchpad` will run `scripts/scratchpad.py` inside the docker container. The `scratchpad.py` file is not checked in to the repo (so you'll have to create it on your machine), but it's a way to run code with the current state of Starplot on your machine -- very helpful when trying things out.
- `make shell` will open a Python shell on the Docker container


_Work in progress_

## Code of Conduct

Starplot supports peace and equality. Please be nice to eachother and respect that we all have different ideas and ways of thinking about things. At the end of the day, we're just here to make maps of the sky.

Please review our complete Code of Conduct [here](CODE_OF_CONDUCT.md).

