HTML := 1-initial-requirements.html  \
        2-detailed-requirements.html \
        3-srs.html                   \
        4-design.html

PDF :=  1-initial-requirements.pdf  \
        2-detailed-requirements.pdf \
        3-srs.pdf                   \
        4-design.pdf

all: html pdf

html: $(HTML)
pdf: $(PDF)

%.html: %.adoc
	asciidoctor -a toc -a data-uri -d book $<

%.xml: %.adoc
	asciidoctor -b docbook -d book -a data-uri! $<

%.pdf: %.xml
	@echo "PDF output is not implemented yet"

clean:
	rm -f $(HTML) $(PDF)

.PHONY: all clean html pdf
