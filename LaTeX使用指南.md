# LaTeX 使用指南（数模国赛写作员必读）

> 目标：让写作员能把 CUMCMThesis 模板**跑通并顺手写论文**。
> 模板已克隆在 `CUMCMThesis/`，论文骨架在 `CUMCMThesis/论文正文.tex`。

---

## 一、LaTeX 是什么、为什么用它

LaTeX（读作"拉泰赫"）是一个**排版系统**：你写纯文本 `.tex` 源码 + 排版命令，它编译成排版精美的 PDF。和 Word 最大的区别是——**你只管内容，格式交给模板**。数模国赛用它的理由：
- 公式排版天下第一（Word 公式又丑又难对齐）
- 参考文献、图表、公式**自动编号 + 交叉引用**，改一处全文自动更新
- 官方 CUMCMThesis 模板已把承诺书、编号页、字体、页边距全配好，**格式零失分**

**核心心智模型**：`源码.tex` --（xelatex 编译）--> `成品.pdf`。你改源码 → 重新编译 → 看 PDF。

---

## 二、两条路：先跑通，二选一

### 路线 A：Overleaf 在线（**零安装，最快，强烈推荐先用这个**）
1. 打开 https://www.overleaf.com 注册（可用 Google/邮箱）
2. 新建项目 → Upload Project → 把 `CUMCMThesis` 文件夹压成 zip 上传
3. 左上 Menu → **Compiler 选 XeLaTeX** →（重要，不然中文报错）
4. 打开 `论文正文.tex`，点 **Recompile**，右边就出 PDF
- 优点：不用装任何东西、自动编译、可多人协作（适合三人一起写）
- 缺点：要联网；免费版编译有时间限制（够用）

### 路线 B：本地 MiKTeX（断网也能用，我已在帮你装）
1. 我已用 `winget install MiKTeX.MiKTeX` 装了引擎（首次编译会自动下缺的宏包，点 Install 即可）
2. 装一个编辑器 **TeXstudio**：`winget install TeXstudio.TeXstudio`
3. TeXstudio 里：Options → Configure → Build → 默认编译器选 **XeLaTeX**
4. 打开 `CUMCMThesis/论文正文.tex`，按 **F5**（编译并查看）
- 命令行方式（在 `CUMCMThesis/` 目录下）：
  ```bash
  xelatex 论文正文
  # 或（更省心，自动跑多遍解决交叉引用）
  latexmk -xelatex 论文正文
  ```

> ⚠️ **铁律：必须用 XeLaTeX 编译，不能用 pdfLaTeX**——中文和字体靠 XeLaTeX 才正常。

---

## 三、写论文最常用的 5 个语法（够用 90%）

### 1. 章节
```latex
\section{模型的建立与求解}
\subsection{问题一模型}
\subsubsection{模型求解}
```

### 2. 公式（数模的命根子）
```latex
行内公式：$E=mc^2$
不编号：\[ E=mc^2 \]
带编号可引用：
\begin{equation}
  \min f(x)=\sum_{i=1}^n (y_i-\hat y_i)^2 \label{eq:obj}
\end{equation}
正文里引用：见式\cref{eq:obj}
```
不会打的符号：用 https://detexify.kirelabs.org 手写识别，或截图丢 https://mathpix.com

### 3. 三线表（国赛表格标准，别用竖线）
```latex
\begin{table}[!htbp]
  \caption{结果对比}\label{tab:res}\centering
  \begin{tabular}{ccc}
    \toprule[1.5pt]
    方法 & 精度 & 耗时 \\
    \midrule[1pt]
    模型A & 98.2\% & 3s \\
    \bottomrule[1.5pt]
  \end{tabular}
\end{table}
```

### 4. 插图（图放 `figures/` 下，**图名用英文数字，别用中文**）
```latex
\begin{figure}[!htbp]
  \centering
  \includegraphics[width=.6\textwidth]{result1}
  \caption{求解结果}\label{fig:r1}
\end{figure}
正文引用：如\cref{fig:r1}所示
```

### 5. 交叉引用（改序号全自动）
- 引用图/表/公式统一用 `\cref{标签}`，标签用 `\label{fig:xxx}` 定义
- 好处：中间插入一张图，后面所有编号自动 +1，不用手改

---

## 四、避坑清单

| 坑 | 解决 |
|----|------|
| 中文全乱码/报错 | 编译器没选 XeLaTeX，改成 XeLaTeX |
| 图插不进 | 图名别用中文；用 png/jpg/pdf，别用 bmp/eps |
| 交叉引用显示 `??` | 多编译一遍（或用 `latexmk` 自动多遍） |
| 公式对齐乱 | 用 `align` 环境，`&` 标对齐位置 |
| 摘要页超过一页 | 精简摘要，控制在一页内（硬性要求） |
| 提交电子版还带封面 | 文档类加 `[withoutpreface]` 选项 |

---

## 五、给写作员的工作流建议

1. **先用 Overleaf 跑通** `论文正文.tex`，确认能出 PDF、中文正常（今天就能做完）。
2. 比赛不是最后才写——**从建模讨论就开始填**问题重述、假设、符号说明。
3. 图统一让编程员导出 `png`（300dpi）放 `figures/`，命名如 `q1_result.png`。
4. 定稿前**最后2小时专做"摘要↔正文逐条对照"**——这是最易失分点。
5. 常用命令记不住就查本文件，或看 `CUMCMThesis/example.tex`（模板自带完整示例）。
