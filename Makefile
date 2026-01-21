.PHONY: install run test verify seed help

# Install dependencies
install:
	pip install -r requirements.txt

# Run the FastAPI server
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
run-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run tests
test:
	python scripts/testing/test_server.py
	python scripts/testing/test_endpoints.py
	python scripts/testing/test_new_modules.py

# Verify routes
verify:
	python scripts/verification/verify_routes.py

# Seed database
seed:
	python scripts/seeding/seed_database.py

# Create admin user
admin:
	python scripts/admin/create_admin_user.py

# Help
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run development server"
	@echo "  make run-prod   - Run production server"
	@echo "  make test       - Run all tests"
	@echo "  make verify     - Verify API routes"
	@echo "  make seed       - Seed database"
	@echo "  make admin      - Create admin user"
