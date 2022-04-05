DOCSDIR = docs_src
BUILDDIR = _build
LOCAL_PORT = 8000
GH_PAGES_DIR = docs

# Build docs locally and start a webserver
local_docs:
	cp ./README.rst $(DOCSDIR)
	sphinx-autobuild $(DOCSDIR) $(DOCSDIR)/$(BUILDDIR)

# Build gh_pages docs manually
github_docs:
	rm -rf $(GH_PAGES_DIR)
	mkdir $(GH_PAGES_DIR) && touch $(GH_PAGES_DIR)/.nojekyll
	@make -C $(DOCSDIR) html
	@cp -a $(DOCSDIR)/$(BUILDDIR)/html/* $(GH_PAGES_DIR)

# Build gh_pages docs using Github Actions
github_actions_docs:
	rm -rf $(GH_PAGES_DIR)
	mkdir $(GH_PAGES_DIR) && touch $(GH_PAGES_DIR)/.nojekyll
	rm -rf $(DOCSDIR)/$(BUILDDIR) && mkdir $(DOCSDIR)/$(BUILDDIR)
	sphinx-build -b html $(DOCSDIR) $(DOCSDIR)/$(BUILDDIR)
	@cp -a $(DOCSDIR)/$(BUILDDIR)/* $(GH_PAGES_DIR)
