# Container & CI notes

This file documents how the container image for this project is built, pushed, and tested.

Image
- Docker Hub: `docker.io/olefile221/car_classifier`
- Tag used: `latest` (and Git SHA tag from CI)

Local build & run
```bash
# Build locally (already done previously)
docker build -t ai-app-containerization:local .

# Run locally (maps Gradio port 7860)
docker run --rm -p 7860:7860 ai-app-containerization:local
```

Push to Docker Hub (already done)
```bash
docker tag ai-app-containerization:local olefile221/car_classifier:latest
docker push olefile221/car_classifier:latest
```

CI / GitHub Actions
- Workflow path: `.github/workflows/docker-publish.yml`
- What it does: runs a small Python import smoke test, builds the image with Buildx, and pushes `:latest` and `:${{ github.sha }}` to Docker Hub.
- Required repo secrets:
  - `DOCKER_USERNAME` = `olefile221`
  - `DOCKER_PASSWORD` = Docker Hub password or access token

Triggering CI
- Create or modify a file on `main` (or run the workflow manually in the Actions tab). Avoid using `[ci skip]` in the commit message.

Verification
- Verify Actions run succeeded in GitHub → Actions.
- Verify tags appear on Docker Hub: https://hub.docker.com/repository/docker/olefile221/car_classifier
- Pull & run from another machine:
```bash
docker pull olefile221/car_classifier:latest
docker run --rm -p 7860:7860 olefile221/car_classifier:latest
# then open http://localhost:7860
```

Security
- Do NOT commit `.env` or API keys. Use GitHub Secrets and Kubernetes Secrets for deployment.

Notes
- The CI workflow does not modify repository files — it only builds and pushes images.
# Containerization & CI Notes

Image: `docker.io/olefile221/car_classifier:latest`

CI workflow: `.github/workflows/docker-publish.yml`

Required GitHub Secrets:
- `DOCKER_USERNAME` (example: `olefile221`)
- `DOCKER_PASSWORD` (Docker Hub password or access token)
- (Optional) `GEMINI_API_KEY` for any CI tests that call the API

How to reproduce locally:
```bash
# build locally
docker build -t car_classifier:local .

# run locally
docker run --rm -p 7860:7860 car_classifier:local
# then open http://localhost:7860
```

How CI works:
- On push to `main`, the workflow installs Python deps and runs a smoke import test.
- If the smoke test passes, it builds the Docker image and pushes to Docker Hub with tags:
  - `olefile221/car_classifier:latest`
  - `olefile221/car_classifier:<git-sha>`

Verification steps (after CI completes):
1. Check GitHub Actions: repo → Actions → "Build, Test and Publish Docker image" → latest run.
2. Confirm smoke test prints "Smoke test passed" and the build/push step shows pushed tags.
3. Confirm Docker Hub contains the new tag: https://hub.docker.com/repository/docker/olefile221/car_classifier
4. From another machine (or after removing local image):
```bash
docker pull olefile221/car_classifier:latest
docker run --rm -p 7860:7860 olefile221/car_classifier:latest
# open http://localhost:7860
```

Notes:
- Do not commit `.env` or any secret keys. Use GitHub Secrets and Kubernetes Secrets when deploying.
- If CI fails, open the failing step logs in Actions and copy any errors for debugging.
