# Workflow
- alway plan first for the task you are going to do
- base on the plan to implement
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance

# system lunch for testing
- DB, Redis, chroma already started within docker, no need to start again.
- always use venv from backend to run python app with uvicorn app.main:app for testing instead of running it via docker
- use local model to run frontend and worker as well for testing