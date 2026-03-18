from __future__ import annotations

import copy
import sys
import zipfile
from pathlib import Path

from lxml import etree

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
W = f"{{{NS['w']}}}"


def _first(items):
    return items[0] if items else None


def _load_xml(docx_path: Path, member: str) -> etree._Element:
    with zipfile.ZipFile(docx_path) as zf:
        return etree.fromstring(zf.read(member))


def _find_template_toc_parts(root: etree._Element) -> tuple[etree._Element, etree._Element, etree._Element]:
    paragraphs = root.xpath(".//w:body/w:p", namespaces=NS)
    toc_title = None
    for paragraph in paragraphs:
        instr = "".join(paragraph.xpath(".//w:instrText/text()", namespaces=NS))
        if "TOC " in instr:
            toc_title = paragraph
            break
    if toc_title is None:
        raise RuntimeError("Template TOC block was not found.")

    seen_title = False
    toc1 = None
    toc2 = None
    toc1_style = None
    for paragraph in paragraphs:
        if paragraph is toc_title:
            seen_title = True
            continue
        if not seen_title:
            continue
        pstyle = _first(paragraph.xpath("./w:pPr/w:pStyle", namespaces=NS))
        if pstyle is None:
            continue
        style_id = pstyle.get(W + "val")
        if toc1 is None:
            toc1 = paragraph
            toc1_style = style_id
            continue
        if style_id != toc1_style:
            toc2 = paragraph
            break
    if toc1 is None or toc2 is None:
        raise RuntimeError("Template TOC level archetypes were not found.")
    return toc_title, toc1, toc2


def _find_target_toc_paragraphs(root: etree._Element) -> list[etree._Element]:
    for sdt in root.xpath(".//w:sdt", namespaces=NS):
        instr = "".join(sdt.xpath(".//w:instrText/text()", namespaces=NS))
        if "TOC " not in instr:
            continue
        content = _first(sdt.xpath("./w:sdtContent", namespaces=NS))
        if content is None:
            continue
        paragraphs = content.xpath("./w:p", namespaces=NS)
        if paragraphs:
            return paragraphs
    raise RuntimeError("Target TOC content control was not found.")


def _replace_ppr(
    dst_paragraph: etree._Element,
    src_paragraph: etree._Element,
    *,
    keep_style: bool,
    drop_ind: bool = False,
) -> None:
    src_ppr = _first(src_paragraph.xpath("./w:pPr", namespaces=NS))
    current_ppr = _first(dst_paragraph.xpath("./w:pPr", namespaces=NS))
    current_style = _first(dst_paragraph.xpath("./w:pPr/w:pStyle", namespaces=NS))
    if current_ppr is not None:
        dst_paragraph.remove(current_ppr)
    if src_ppr is None:
        return

    new_ppr = copy.deepcopy(src_ppr)
    if keep_style:
        for node in new_ppr.xpath("./w:pStyle", namespaces=NS):
            new_ppr.remove(node)
        if current_style is not None:
            new_ppr.insert(0, copy.deepcopy(current_style))
    if drop_ind:
        for node in new_ppr.xpath("./w:ind", namespaces=NS):
            new_ppr.remove(node)
    dst_paragraph.insert(0, new_ppr)


def _replace_run_rpr(dst_run: etree._Element, src_run: etree._Element) -> None:
    current_rpr = _first(dst_run.xpath("./w:rPr", namespaces=NS))
    if current_rpr is not None:
        dst_run.remove(current_rpr)
    src_rpr = _first(src_run.xpath("./w:rPr", namespaces=NS))
    if src_rpr is not None:
        dst_run.insert(0, copy.deepcopy(src_rpr))


def _first_visible_run(paragraph: etree._Element) -> etree._Element:
    for run in paragraph.xpath(".//w:r", namespaces=NS):
        if run.xpath("./w:t", namespaces=NS):
            return run
    raise RuntimeError("No visible run found in paragraph.")


def _set_title_paragraph(dst_title: etree._Element, src_title: etree._Element) -> None:
    _replace_ppr(dst_title, src_title, keep_style=False)
    for child in list(dst_title):
        if child.tag != W + "pPr":
            dst_title.remove(child)

    src_run = _first_visible_run(src_title)
    new_run = copy.deepcopy(src_run)
    text_node = _first(new_run.xpath("./w:t", namespaces=NS))
    if text_node is not None:
        text_node.text = "目　　录"
    dst_title.append(new_run)


def _format_toc_entry(paragraph: etree._Element, src_paragraph: etree._Element, *, drop_ind: bool = False) -> None:
    _replace_ppr(paragraph, src_paragraph, keep_style=True, drop_ind=drop_ind)
    sample_run = _first_visible_run(src_paragraph)
    for run in paragraph.xpath(".//w:r", namespaces=NS):
        _replace_run_rpr(run, sample_run)


def _patch_document_xml(template_xml: bytes, target_xml: bytes) -> bytes:
    template_root = etree.fromstring(template_xml)
    target_root = etree.fromstring(target_xml)

    title_tpl, toc1_tpl, toc2_tpl = _find_template_toc_parts(template_root)
    target_paragraphs = _find_target_toc_paragraphs(target_root)
    if not target_paragraphs:
        raise RuntimeError("Target TOC paragraph list is empty.")

    _set_title_paragraph(target_paragraphs[0], title_tpl)

    for paragraph in target_paragraphs[1:]:
        pstyle = _first(paragraph.xpath("./w:pPr/w:pStyle", namespaces=NS))
        style_id = pstyle.get(W + "val") if pstyle is not None else ""
        if style_id == "10":
            _format_toc_entry(paragraph, toc1_tpl)
        elif style_id == "11":
            _format_toc_entry(paragraph, toc2_tpl)
        elif style_id == "7":
            _format_toc_entry(paragraph, toc2_tpl, drop_ind=True)

    return etree.tostring(target_root, xml_declaration=True, encoding="UTF-8", standalone="yes")


def patch_toc_from_template(template_path: Path, target_path: Path) -> None:
    with zipfile.ZipFile(template_path) as template_zip:
        template_xml = template_zip.read("word/document.xml")

    with zipfile.ZipFile(target_path) as target_zip:
        files = {info.filename: target_zip.read(info.filename) for info in target_zip.infolist()}

    files["word/document.xml"] = _patch_document_xml(template_xml, files["word/document.xml"])

    temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED) as out_zip:
        for name, data in files.items():
            out_zip.writestr(name, data)
    temp_path.replace(target_path)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python patch_toc_dom.py <template.docx> <target.docx>")
        return 1
    patch_toc_from_template(Path(argv[1]), Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
