import os
import json
import argparse
import itertools

import PyPDF2


def dump_refs(fp, filename):
    pdf = PyPDF2.PdfFileReader(fp)

    o = pdf.getNamedDestinations()
    pages = [pdf.getPage(i).getObject() for i in range(pdf.getNumPages())]
    annots = [
        [a.getObject()
         for a in p.get('/Annots', [])]
        for p in pages
    ]

    with open(filename, 'w') as fp:
        json.dump({'nameddests': o, 'annots': annots},
                  fp, indent=0, sort_keys=True, default=repr)

    if not o:
        print("Warning: No named destinations")

    anchors = {
        k: [v + 1 for k_, v in vs]
        for k, vs in itertools.groupby(
            sorted(set((a.getObject().get('/A', {}).get('/D', ''), i)
                       for i, p in enumerate(pages)
                       for a in p.get('/Annots', []))),
            key=lambda x: x[0])
    }

    objects = sorted(pdf.getNamedDestinations().items(),
                     key=lambda x: -x[1]['/Top'])
    references = [k for k, v in objects if k.startswith('cite.')]

    for i, ref in enumerate(references):
        print('%d. %s cited in %r' % (i + 1, ref, anchors.get(ref)))
    if not references:
        print("No references found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    base = os.path.splitext(os.path.basename(args.filename))[0]
    out = base + '-destinations.json'

    with open(args.filename, 'rb') as fp:
        dump_refs(fp, out)


if __name__ == "__main__":
    main()
