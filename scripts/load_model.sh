#!/bin/bash

# Load environment variables from .env file
MODEL_NAME=skyllama
MODEL_VERSION=latest
source .env

# Check if the model is already loaded and remove it if it exists
if ollama list | grep -q "$MODEL_NAME:$MODEL_VERSION"; then
  echo "Removing existing model '$MODEL_NAME:$MODEL_VERSION'..."
  ollama rm $MODEL_NAME:$MODEL_VERSION
fi

echo "Loading model '$MODEL_NAME:$MODEL_VERSION' from Modelfile..."
ollama create $MODEL_NAME:$MODEL_VERSION -f Modelfile
