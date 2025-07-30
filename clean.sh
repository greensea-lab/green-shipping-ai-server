#!/bin/bash
# Green Shipping AI Server - Unix/Linux Clean Script
# Unix/Linux 환경에서 가상환경을 삭제하는 스크립트

echo "🧹 Removing virtual environment..."

if [ -d "venv" ]; then
    rm -rf venv
    echo "✅ Virtual environment removed."
else
    echo "ℹ️ Virtual environment does not exist."
fi 