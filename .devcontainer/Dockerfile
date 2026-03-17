FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install EDA Tools
RUN apt-get update && apt-get install -y \
    iverilog \
    gtkwave \
    yosys \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN python3 -m pip install --upgrade pip

# Create working directory
WORKDIR /workspaces/veriflow

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt
