# Python Template Project

This project serves as an example and template for python development.

[[_TOC_]]

## Project Structure

All Python projects follow the same base structure, a top level package located
in the root project directory (`hello` in this case). This package should
contain the file `__main__.py`, which is the entrypoint of the application and
executed when the package is run as a module (using `python -m`).

## Quick Start

Start by running the following command from the root project directory

```shell
python -m hello
```

This will display a hello world message on the terminal. Run it with the
`--help` (or `-h`) option to see other invocations options.

## Code Style tools

As with any programming language, it is important that the code not only works
but also adheres to a certain standard of quality. Python has many tools to help
us set a good standard that should be followed by all. To see which tools we
use, have a look at the [Makefile](Makefile) and our [Python Coding
Standards](https://marlo-wiki.atlassian.net/wiki/spaces/TEC/pages/6415549351/Python+Coding+Standards).

## Documentation

[pdoc](https://pdoc.dev/) is used to automatically generate documentation for
this project. This documentation along with test and code style reports are
[available online](https://themarlogroup.gitlab.io/templates/python)
with GitLab Pages.

## Environment and Package Management

This project uses [uv](https://github.com/astral-sh/uv) for managing virtual
environments and installing dependencies. Dependencies are defined in
`pyproject.toml` and a lock file (`uv.lock`) is used for
reproducible builds.

### Setting up with uv

#### 1. Install uv (if you haven't already)

If you don't have `uv` installed, run:

```sh
pip install uv
```

Or see [uv installation docs](https://docs.astral.sh/uv/install/).

#### 2. Create and Sync the Virtual Environment

Just run:

```sh
uv sync
```

This single command will:

- Create a `.venv` if it doesn't exist
- Generate or update `uv.lock` as needed
- Install all dependencies as defined in your `pyproject.toml` and lock file

Rerun the command anytime you make a manual change to `pyproject.toml` in order
to update the lock file and virtual environment.

#### 3. Activate the Virtual Environment

Unlike `pip`, running commands with uv does not need the virtual environment
to be activated in the shell, as uv will automatically detect and use it
regardless. If you still wish to activate it anyway:

On macOS/Linux:

```sh
source .venv/bin/activate
```

On Windows:

```sh
.venv\Scripts\activate
```

### Additional uv commands worth knowing

#### uv run

This performs the same steps as `uv sync` (venv, install dependencies etc.)
but also executes a python script/package. eg.

```bash
uv run -m hello
```

#### uv add

Add a dependency to pyproject.toml and update the lock file. eg.

```bash
uv add pok
```

#### uv remove

Remove a dependecy from pyproject and lock file. eg.

```bash
uv remove pok
```

#### dev flag

uv uses the concept of dependency groups to enable installation of only subsets of project dependencies. There is a special group name called `dev` which is automcatically included with `uv sync` and other related commands. To add dependencies to this group, use the `--dev` flag. eg.

```bash
uv add pok --dev
```

and vice-versa for removing.

To install only the base project requirements without development dependencies, use `--no-dev`:

```bash
uv sync --no-dev
```

#### Further reading

To learn more commands and see the full potential of uv check out [the docs](https://docs.astral.sh/uv/)
