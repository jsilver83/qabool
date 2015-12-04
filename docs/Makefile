OUTPUTS := 1-initial-requirements.html  \
           1-initial-requirements.xml   \
           3-srs.html                   \
           3-srs.xml                    \
           4-design.html                \
           4-design.xml

all: $(OUTPUTS)

%.html: %.adoc
	asciidoctor -a toc -a data-uri -d book $<

%.xml: %.adoc
	asciidoctor -b docbook -d book -a data-uri! $<

clean:
	rm -f $(OUTPUTS)

.PHONY: all clean
