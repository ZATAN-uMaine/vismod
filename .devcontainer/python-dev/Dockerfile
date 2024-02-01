FROM python:3.11-bookworm

# create container user
RUN adduser --uid 1000 --disabled-password --gecos "" work

# install global deps
RUN apt-get update && apt-get install -y \
  pipx \
  ansible \
  ansible-lint 

USER work

# Install Python build tool
ENV PATH="${PATH}:/home/work/.local/bin"
RUN pipx install hatch
