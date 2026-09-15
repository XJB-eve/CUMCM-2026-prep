# -*- coding: utf-8 -*-
"""095学习报告2.docx → PDF（Word COM）。文件式脚本避免中文路径乱码。
运行前先 taskkill //F //IM WINWORD.EXE 清残留进程。
"""
import os
from docx2pdf import convert

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 数模/
src = os.path.join(BASE, '学习报告2', '095学习报告2.docx')
dst = os.path.join(BASE, '学习报告2', '095学习报告2.pdf')
convert(src, dst)
print('ok:', dst)
