#!/bin/bash
set -e

cd ~
echo "1. Downloading Ollama binary..."
curl -L -o ollama-linux-amd64.tar.zst https://github.com/ollama/ollama/releases/download/v0.30.7/ollama-linux-amd64.tar.zst

echo "2. Extracting archive..."
tar -I zstd -xf ollama-linux-amd64.tar.zst

echo "3. Starting Ollama Server in the background..."
nohup ./bin/ollama serve > ollama.log 2>&1 &

echo "Waiting for server to start..."
sleep 5

echo "4. Pulling llama3 model (This will take a long time)..."
./bin/ollama pull llama3

echo "5. Installation complete! Llama3 is ready."
