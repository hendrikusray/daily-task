.PHONY: help install setup run stop clean test verify deploy docker-run

help:
	@echo "CMS Project - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install all dependencies"
	@echo "  make setup         - Setup virtual environment"
	@echo ""
	@echo "Running Application:"
	@echo "  make run           - Start the application"
	@echo "  make stop          - Stop the application"
	@echo "  make restart       - Restart the application"
	@echo ""
	@echo "Development:"
	@echo "  make verify        - Verify project setup"
	@echo "  make clean         - Clean cache & temp files"
	@echo "  make reset-db      - Reset database"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-run    - Run with Docker"
	@echo "  make docker-stop   - Stop Docker container"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-replit - Deploy to Replit"
	@echo "  make deploy-railway - Deploy to Railway"
	@echo ""

install:
	@echo "Installing dependencies..."
	python3 -m pip install -r requirements.txt

setup:
	@echo "Setting up virtual environment..."
	python3 -m venv venv
	@echo "Virtual environment created. Run: source venv/bin/activate"

run:
	@echo "Starting CMS Application..."
	./run.sh

stop:
	@echo "Stopping application... (Press Ctrl+C in terminal)"

restart: stop run

verify:
	@echo "Verifying project setup..."
	./verify.sh

clean:
	@echo "Cleaning cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned"

reset-db:
	@echo "Resetting database..."
	rm -f app/konten.db
	@echo "✓ Database deleted. Restart app to recreate."

docker-run:
	@echo "Running with Docker Compose..."
	docker-compose up

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-build:
	@echo "Building Docker image..."
	docker-compose build

deploy-replit:
	@echo "Deployment guide: See deployment/DEPLOYMENT.md"
	@echo "1. Go to https://replit.com"
	@echo "2. Import this GitHub repo"
	@echo "3. Click 'Run'"

deploy-railway:
	@echo "Deployment guide: See deployment/DEPLOYMENT.md"
	@echo "1. Go to https://railway.app"
	@echo "2. Connect GitHub repo"
	@echo "3. Auto-deploy on push"

.PHONY: help install setup run stop restart verify clean reset-db docker-run docker-stop docker-build deploy-replit deploy-railway
