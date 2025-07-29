# Gmail, Calendar, and Maps MCP Server Makefile

.PHONY: help install setup test run clean

# Default target
help:
	@echo "Gmail, Calendar, and Maps MCP Server"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install    - Install Python dependencies"
	@echo "  setup      - Run Google API setup script"
	@echo "  test       - Run test suite"
	@echo "  run        - Start the MCP server"
	@echo "  example    - Run example usage script"
	@echo "  clean      - Clean up generated files"
	@echo "  help       - Show this help message"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Setup Google APIs
setup:
	@echo "Setting up Google APIs..."
	python setup_google_apis.py

# Run tests
test:
	@echo "Running test suite..."
	python test_server.py

# Start the server
run:
	@echo "Starting MCP server..."
	python server.py

# Run examples
example:
	@echo "Running example usage..."
	python example_usage.py

# Clean up generated files
clean:
	@echo "Cleaning up..."
	rm -f credentials.json
	rm -f .env
	@echo "Note: client_secrets.json is not removed (contains your OAuth credentials)"

# Quick start - install, setup, and test
quickstart: install setup test
	@echo "Quick start completed!"
	@echo "Run 'make run' to start the server"

# Development setup
dev: install setup
	@echo "Development environment ready!"
	@echo "Run 'make test' to verify setup"
	@echo "Run 'make run' to start the server" 