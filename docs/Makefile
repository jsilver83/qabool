HTML := 1-initial-requirements.html  \
        2-detailed-requirements.html \
        3-charter.html               \
        4-srs.html                   \
        5-design.html

PDF :=  1-initial-requirements.pdf  \
        2-detailed-requirements.pdf \
        3-charter.pdf               \
        4-srs.pdf                   \
        5-design.pdf

all: html pdf

html: $(HTML)
pdf: $(PDF)

%.html: %.adoc
	asciidoctor -a toc -a sectnums -a icons=font -a data-uri -d book $<

%.xml: %.adoc
	asciidoctor -b docbook -d book -a data-uri! $<

%.pdf: %.xml
	@echo "PDF output is not implemented yet"

clean:
	rm -f $(HTML) $(PDF)

.PHONY: all clean html pdf
