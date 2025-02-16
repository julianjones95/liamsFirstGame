.PHONY: all install run clean

# Default target
all: install run

# Install dependencies
install:
	python -m pip install --user -r requirements.txt

# Run the game
run:
	python snake_game.py

# Clean up generated files
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
