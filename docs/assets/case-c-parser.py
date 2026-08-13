#!/usr/bin/env python3
"""解析 page.html 中 id='product-table' 的表格，并以 CSV 格式输出到 stdout。

实现使用标准库 html.parser，无第三方依赖。
"""

import csv
import os
import sys
from html.parser import HTMLParser

HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "page.html")


class ProductTableParser(HTMLParser):
    """提取 id='product-table' 表格中的所有行（含表头行）。"""

    def __init__(self):
        super().__init__()
        self.in_product_table = False
        self.table_depth = 0
        self.in_row = False
        self.in_cell = False
        self.current_cell_parts = []
        self.current_row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table" and attrs.get("id") == "product-table":
            self.in_product_table = True
            self.table_depth = 1
            return
        if not self.in_product_table:
            return
        if tag == "table":
            self.table_depth += 1
        elif tag == "tr":
            self.in_row = True
            self.current_row = []
        elif tag in ("th", "td") and self.in_row:
            self.in_cell = True
            self.current_cell_parts = []

    def handle_endtag(self, tag):
        if not self.in_product_table:
            return
        if tag == "table":
            self.table_depth -= 1
            if self.table_depth == 0:
                self.in_product_table = False
        elif tag == "tr" and self.in_row:
            self.rows.append(self.current_row)
            self.current_row = []
            self.in_row = False
        elif tag in ("th", "td") and self.in_cell:
            self.current_row.append("".join(self.current_cell_parts).strip())
            self.current_cell_parts = []
            self.in_cell = False

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell_parts.append(data)


def main():
    with open(HTML_FILE, encoding="utf-8") as f:
        html = f.read()

    parser = ProductTableParser()
    parser.feed(html)

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerows(parser.rows)


if __name__ == "__main__":
    main()
