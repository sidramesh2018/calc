# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = CALC
SOURCEDIR     = .
BUILDDIR      = _build
DJANGODIR     = static

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

html: Makefile
	rm -rf $(BUILDDIR) $(DJANGODIR)
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	mkdir -p $(DJANGODIR)
	cp -R $(BUILDDIR)/html $(DJANGODIR)/docs/

	# https://github.com/snide/sphinx_rtd_theme/issues/359
	sed -i.bak 's/font\/fontawesome_/fonts\/fontawesome-/g' \
	$(DJANGODIR)/docs/_static/css/badge_only.css

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
