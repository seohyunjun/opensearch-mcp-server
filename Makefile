.PHONY: release

release:
	@if [ -z "$(version)" ]; then \
		echo "Please specify version: e.g, make release version=v0.0.6"; \
		exit 1; \
	fi
	@echo "Updating version to $(version:v%=%)"
	@python -c 'import tomli; import tomli_w; \
		data = tomli.load(open("pyproject.toml", "rb")); \
		data["project"]["version"] = "$(version:v%=%)"; \
		tomli_w.dump(data, open("pyproject.toml", "wb"))'
	@git add pyproject.toml
	@git commit -m "release: update version to $(version:v%=%)"
	@git push origin main
	@git tag $(version)
	@git push origin $(version)
	@echo "Version updated and tag pushed. GitHub Actions will handle the release."
