ensure:
	uv sync

build: ensure
	uv run python -m build

publish: build
	uv run python -m twine upload dist/*
	rm -r dist
