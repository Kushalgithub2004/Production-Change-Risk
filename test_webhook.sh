#!/bin/bash

# Simulates a GitHub Pull Request Webhook event
# This will be ingested by FastAPI and published to Kafka for async ML processing.

curl -X POST http://localhost:8000/api/v1/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d '{
    "action": "opened",
    "pull_request": {
      "number": 42,
      "head": {
        "ref": "feature/risky-db-migration"
      }
    },
    "repository": {
      "full_name": "my-org/core-service"
    }
  }'

echo -e "\n\nWebhook sent! Check the docker-compose logs to see the Kafka Worker pick it up."
