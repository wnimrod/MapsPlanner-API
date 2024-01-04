start-dev:
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up
build-dev:
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
stop:
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . down
test:
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.pytest.yml --project-directory . run --rm --name pytest api pytest -vv .


