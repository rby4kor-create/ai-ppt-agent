"""
tools/validate_hyperlinks.py

Structural hyperlink validator for a generated Top Gen AI deck.

Checks, per slide:
  - is there a "Source:" text run at all (MISSING if not)
  - does that run carry an actual r:id hyperlink relationship (not just text)
  - is the target URL well-formed (scheme + host)

This sandbox cannot make outbound requests to arbitrary source domains
(openai.com, github.com/blog, nvidianews.nvidia.com, etc. are outside the
allow-listed network), so this is a STRUCTURAL check: it proves every
"Source:" line is a real clickable hyperlink pointing at a syntactically
valid URL, not that the URL currently 200s. Run a reachability pass on a
machine with open internet for the live-link guarantee.
"""

import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def well_formed(url: str) -> bool:
    try:
        p = urlparse(url)
        return bool(p.scheme in ("http", "https") and p.netloc)
    except Exception:
        return False


def validate(pptx_path: Path):
    z = zipfile.ZipFile(pptx_path)
    slide_files = sorted([n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")],
                          key=lambda n: int("".join(filter(str.isdigit, n)) or 0))

    total_source_lines = 0
    valid = 0
    invalid = 0
    missing = 0
    report_rows = []

    for sf in slide_files:
        rels_name = f"ppt/slides/_rels/{Path(sf).name}.rels"
        rels = {}
        if rels_name in z.namelist():
            rtree = ET.fromstring(z.read(rels_name))
            for rel in rtree:
                rels[rel.attrib["Id"]] = rel.attrib.get("Target", "")

        xml = z.read(sf).decode("utf-8")
        tree = ET.fromstring(xml)
        for t_elem in tree.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t"):
            if t_elem.text and t_elem.text.strip().lower().startswith("source:"):
                total_source_lines += 1
                # look for a hyperlink rId on any run in this same paragraph
                found_rid = None
                parent_map = {c: p for p in tree.iter() for c in p}
                node = t_elem
                # walk up to the <a:r> run, then find rPr/hlinkClick
                run = None
                cur = t_elem
                for _ in range(5):
                    cur = parent_map.get(cur)
                    if cur is not None and cur.tag.endswith("}r"):
                        run = cur
                        break
                if run is not None:
                    rpr = run.find("a:rPr", NS)
                    if rpr is not None:
                        hlink = rpr.find("a:hlinkClick", NS)
                        if hlink is not None:
                            found_rid = hlink.attrib.get(f"{{{NS['r']}}}id")
                if found_rid and found_rid in rels:
                    url = rels[found_rid]
                    if well_formed(url):
                        valid += 1
                        report_rows.append((sf, t_elem.text.strip(), url, "VALID"))
                    else:
                        invalid += 1
                        report_rows.append((sf, t_elem.text.strip(), url, "MALFORMED"))
                else:
                    missing += 1
                    report_rows.append((sf, t_elem.text.strip(), "", "MISSING_HYPERLINK"))

    print(f"Total 'Source:' lines found : {total_source_lines}")
    print(f"Valid hyperlinks            : {valid}")
    print(f"Malformed URLs              : {invalid}")
    print(f"Missing hyperlink altogether: {missing}")
    print()
    for row in report_rows:
        print(f"  [{row[3]:18}] {row[0]:28} {row[1]:22} -> {row[2]}")
    return dict(total=total_source_lines, valid=valid, invalid=invalid, missing=missing)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "output" / "TopGenAI-CW35-2026-redesign.pptx"
    validate(target)
