#!/bin/sh

ollama serve &

sleep 5

ollama pull tinyllama

ipython
