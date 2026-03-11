FROM ghcr.io/astral-sh/uv:python3.13-bookworm
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

WORKDIR /app

# The workspace project file
COPY pyproject.toml .
COPY uv.lock .
RUN uv venv

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the project into the image
COPY src src
COPY README.md .


# Build the actual code
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

ENTRYPOINT uv run write 'I succeeded this time' --filename output/output.txt
