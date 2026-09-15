from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, Table,
    TableStyle, KeepTogether, Flowable,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "pdf" / "创新设计报告_谢俊邦_STC-B音乐律动.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

try:
    pdfmetrics.registerFont(TTFont("YaHei", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
    FONT = "YaHei"
except Exception:
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    FONT = "STSong-Light"

BLACK = colors.black
GRAY = HexColor("#666666")
LINE = HexColor("#A6A6A6")
LIGHT = HexColor("#F3F3F3")
NAVY = HexColor("#1F4E79")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle", fontName=FONT, fontSize=24, leading=36,
    alignment=TA_CENTER, textColor=BLACK, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="CoverMeta", fontName=FONT, fontSize=14, leading=30,
    alignment=TA_LEFT, textColor=BLACK,
))
styles.add(ParagraphStyle(
    name="Abstract", fontName=FONT, fontSize=10.5, leading=21,
    alignment=TA_LEFT, firstLineIndent=21, textColor=BLACK, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="Body", fontName=FONT, fontSize=10.5, leading=21,
    alignment=TA_LEFT, firstLineIndent=21, textColor=BLACK, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="BodyNoIndent", fontName=FONT, fontSize=10.5, leading=20,
    alignment=TA_LEFT, textColor=BLACK, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="H1", fontName=FONT, fontSize=15, leading=25, textColor=BLACK,
    spaceBefore=13, spaceAfter=8, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="H2", fontName=FONT, fontSize=12, leading=22, textColor=BLACK,
    spaceBefore=10, spaceAfter=5, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="Small", fontName=FONT, fontSize=8.8, leading=15, textColor=BLACK,
))
styles.add(ParagraphStyle(
    name="Caption", fontName=FONT, fontSize=9, leading=15, alignment=TA_CENTER,
    textColor=GRAY, spaceBefore=3, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="TOC", fontName=FONT, fontSize=11, leading=20, textColor=BLACK,
    leftIndent=12, firstLineIndent=-12,
))
styles.add(ParagraphStyle(
    name="TOC2", fontName=FONT, fontSize=10, leading=18, textColor=BLACK,
    leftIndent=30, firstLineIndent=-12,
))


def p(text, style="Body"):
    return Paragraph(text, styles[style])


def heading1(text):
    return Paragraph(text, styles["H1"])


def heading2(text):
    return Paragraph(text, styles["H2"])


def make_table(rows, widths, header=True):
    body = [[p(str(cell), "Small") for cell in row] for row in rows]
    if header:
        body[0] = [Paragraph(str(cell), ParagraphStyle(
            "head", parent=styles["Small"], textColor=colors.white,
            alignment=TA_CENTER,
        )) for cell in rows[0]]
    table = Table(body, colWidths=widths, repeatRows=1 if header else 0, hAlign="CENTER")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ])
    table.setStyle(TableStyle(commands))
    return table


class ArrowFlow(Flowable):
    """Simple, source-code-only architecture figure."""
    def __init__(self):
        Flowable.__init__(self)
        self.width = 16.0 * cm
        self.height = 3.4 * cm

    def draw(self):
        c = self.canv
        boxes = [
            (0.1*cm, 1.1*cm, 3.35*cm, 1.15*cm, "声音输入\n系统回环 / 麦克风"),
            (4.15*cm, 1.1*cm, 3.7*cm, 1.15*cm, "上位机分析\n能量、平滑、量化"),
            (8.55*cm, 1.1*cm, 3.35*cm, 1.15*cm, "串口链路\n115200 baud，6 字节帧"),
            (12.6*cm, 1.1*cm, 3.25*cm, 1.15*cm, "STC-B 显示\n数码管亮条"),
        ]
        c.setStrokeColor(NAVY)
        c.setFillColor(HexColor("#EAF2F8"))
        for x, y, w, h, label in boxes:
            c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
            c.setFillColor(BLACK)
            c.setFont(FONT, 8.5)
            lines = label.split("\n")
            for index, line in enumerate(lines):
                c.drawCentredString(x + w/2, y + h - 0.43*cm - index*0.38*cm, line)
            c.setFillColor(HexColor("#EAF2F8"))
        c.setFillColor(NAVY)
        for x in (3.55, 7.95, 12.0):
            y = 1.68 * cm
            c.line(x*cm, y, (x+0.45)*cm, y)
            c.line((x+0.45)*cm, y, (x+0.26)*cm, y+0.11*cm)
            c.line((x+0.45)*cm, y, (x+0.26)*cm, y-0.11*cm)


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(filename, pagesize=A4, leftMargin=2.35*cm, rightMargin=2.35*cm,
                         topMargin=2.2*cm, bottomMargin=2.0*cm)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="main")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[frame], onPage=self.cover_page),
            PageTemplate(id="body", frames=[frame], onPage=self.body_page),
        ])

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            if style_name == "H1":
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))
            elif style_name == "H2":
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))

    def cover_page(self, canvas, doc):
        pass

    def body_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.3)
        canvas.line(2.35*cm, A4[1]-1.35*cm, A4[0]-2.35*cm, A4[1]-1.35*cm)
        canvas.setFont(FONT, 8.5)
        canvas.setFillColor(GRAY)
        canvas.drawString(2.35*cm, A4[1]-1.0*cm, "创新设计报告  STC-B 音乐律动可视化系统")
        canvas.drawRightString(A4[0]-2.35*cm, 1.05*cm, str(doc.page - 1))
        canvas.restoreState()


story = []

# Cover follows the supplied template's information-block structure.
story.extend([
    Spacer(1, 3.1*cm),
    p("创新设计报告", "CoverTitle"),
    Spacer(1, 1.6*cm),
    Table([
        [p("课  程 名 称：", "CoverMeta"), p("系统编程与创新设计", "CoverMeta")],
        [p("设计项目名称：", "CoverMeta"), p("基于 STC-B 学习板的音乐律动可视化系统", "CoverMeta")],
        [p("专  业 班 级：", "CoverMeta"), p("计科 2401", "CoverMeta")],
        [p("姓        名：", "CoverMeta"), p("谢俊邦", "CoverMeta")],
        [p("学        号：", "CoverMeta"), p("202408010119", "CoverMeta")],
        [p("指 导 教 师：", "CoverMeta"), p("", "CoverMeta")],
        [p("完 成 时 间：", "CoverMeta"), p("2026 年 9 月", "CoverMeta")],
    ], colWidths=[5.2*cm, 9.0*cm], style=TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])),
    Spacer(1, 3.3*cm),
    p("计算机学院", "CoverTitle"),
    PageBreak(),
])

story.extend([
    p("摘  要", "H1"),
    p("本设计围绕本人负责的音乐律动功能，完成了 Windows 上位机与 STC-B 学习板之间的声音可视化链路。上位机从系统回环或麦克风获取声音数据，经能量估计、动态归一化、包络平滑和离散量化得到 0-8 级强度；学习板通过 USB 虚拟串口接收带校验的控制帧，并用 8 位数码管输出连续亮条或左右声道的上下半段。设计将计算量较大的音频处理安排在 PC 端，把单片机侧聚焦于通信校验、显示刷新和失联回退，适配 STC-B 的硬件资源约束。针对串口传输中断、异常等级和显示残留等问题，设计了固定帧格式、范围检查和约 500 ms 的超时回退机制。该功能能将音乐节奏和环境声音变化转化为直观的板端显示，为数码管、串口与定时任务的综合应用提供了一个可演示的实例。", "Abstract"),
    p("关键词：STC-B；音乐律动；串口通信；音频分析；数码管显示", "BodyNoIndent"),
    Spacer(1, 0.3*cm),
    p("目  录", "H1"),
])

toc = TableOfContents()
toc.levelStyles = [styles["TOC"], styles["TOC2"]]
toc.dotsMinLevel = 0
story.extend([toc, PageBreak()])

story.extend([
    heading1("1 绪论"),
    heading2("1.1 选题背景"),
    p("在学习板实验中，数码管、UART 和定时器通常以相互独立的例程出现，难以直接体现软硬件协同的过程。音乐律动可视化将声音采集、数据处理、串口传输和板端显示串成闭环：用户播放音乐或对着麦克风发声，强弱变化被转换为数码管亮条。相比在 8051 单片机上进行高采样率音频运算，把分析任务放在电脑端能够降低板端计算压力，同时保留学习板对通信、显示和时序控制的实践价值。"),
    heading2("1.2 任务与功能"),
    p("本人的工作范围限定为音乐律动可视化功能，不展开说明团队其他外设功能。该功能需要完成四项任务：第一，获取系统回环或麦克风声音；第二，按音频能量生成 0-8 级显示强度；第三，通过 115200 baud 串口将强度稳定发送至学习板；第四，完成板端合法帧校验、数码管映射和失联回退。上位机提供系统音频/麦克风、低频律动/节拍增强、单声道/双声道等可选项，便于在验收时展示输入源和显示效果的对应关系。"),
    heading2("1.3 本文结构"),
    p("第 1 章说明音乐律动功能的背景、目标与范围；第 2 章给出功能总体结构、数据流和本人负责的接口；第 3 章说明与本功能有关的学习板显示和串口硬件；第 4 章介绍音频处理、协议与板端软件逻辑；第 5 章给出测试方法和验收观察点；第 6 章总结设计并提出改进方向；第 7 章说明 AI 协作情况。"),
    heading1("2 系统总体设计与个人工作范围"),
    heading2("2.1 功能总体结构"),
    p("音乐律动功能采用“PC 分析、串口传输、板端显示”的分层结构。上位机负责采集声音并计算等级，串口链路仅传递紧凑的控制数据，STC-B 负责接收、校验和显示。这样既避免原始音频在串口上传输，也避免单片机承担频域计算。"),
    ArrowFlow(),
    p("图 1 音乐律动功能的数据流", "Caption"),
    heading2("2.2 关键设计要点"),
    make_table([
        ["设计点", "本人完成的处理"],
        ["强度表达", "把连续声音能量压缩为 0-8 级，直接对应数码管亮条长度。"],
        ["刷新节奏", "上位机以约 50 ms 的独立发送周期输出最新结果，避免音频回调阻塞串口。"],
        ["异常处理", "板端核验帧头、类型、范围和异或校验；超时后清空亮条并恢复空闲显示。"],
        ["显示扩展", "单声道显示整体强度；双声道分别利用数码管上、下半段表达左右声道等级。"],
    ], [3.4*cm, 11.0*cm]),
    heading2("2.3 工程接口与本人范围"),
    p("最终提交工程由固件 TAR 与上位机 TAR 组成。本功能在固件工程中以串口接收、数码管映射和周期超时处理为接口，在上位机工程中以 audio.rs、protocol.rs、serial.rs 与 service.rs 等模块为接口。本报告只围绕这些与音乐律动有关的文件、数据格式和逻辑进行说明，不将其他同学负责的功能写入本人实现部分。"),
    PageBreak(),
    heading1("3 硬件电路原理"),
    heading2("3.1 与音乐律动相关的硬件组成"),
    p("音乐律动使用 STC-B 学习板上的 STC15F2K60S2 单片机、8 位数码管、LED 指示和串口接口。电脑端通过 USB 转串口芯片形成虚拟 COM 口，串口采用 115200 baud、8N1 配置。数码管承担主输出，LED 可作为运行状态的辅助提示；蜂鸣器不参与音乐音频播放，仅可用于板端基础联调提示。"),
    make_table([
        ["硬件模块", "与本功能的关系", "工作要点"],
        ["USB 虚拟串口", "连接上位机与学习板", "接收 6 字节等级帧，不传输原始 PCM 音频。"],
        ["UART 接收", "取得控制数据", "按字节解析帧头、类型、载荷与校验。"],
        ["8 位数码管", "可视化输出", "单声道连续点亮；双声道以每位上、下半段表示左右强度。"],
        ["定时任务", "维护显示时效", "以约 10 ms 周期累计新鲜度，防止断连后旧画面残留。"],
    ], [3.2*cm, 4.7*cm, 6.5*cm]),
    heading2("3.2 数码管显示映射原理"),
    p("当接收到单声道等级 N 时，N=0 表示全部熄灭，N=1 至 8 表示从低位到高位连续点亮 N 位。双声道帧包含左、右两个等级：左声道等级控制每一位数码管的上半段，右声道等级控制下半段；两半段同时点亮时显示为完整的“8”。该方式展示的是整体能量或左右声道差异，不等同于八个独立频段的频谱图。"),
    heading2("3.3 超时回退"),
    p("板端每收到一个合法音乐帧即重置新鲜度计数；若连续约 500 ms 没有合法帧到达，立即清空律动亮条并回到空闲显示。该处理覆盖上位机关闭、串口拔出和数据异常等情况，能够避免最后一帧长期保留在数码管上。"),
    PageBreak(),
    heading1("4 软件设计与实现"),
    heading2("4.1 上位机音频处理"),
    p("上位机从 Windows 系统回环或默认麦克风取得音频采样。低频律动模式重点观测约 55-260 Hz 的能量，适合鼓点和低音较明显的音乐；节拍增强模式综合多个频段的瞬态变化，适合节奏密集的声音。处理过程使用 RMS 能量作为基础量，再结合动态噪声底、峰值估计和包络平滑，使不同歌曲音量下的显示变化保持可见而不频繁闪烁。"),
    make_table([
        ["处理步骤", "作用"],
        ["能量计算", "把连续采样转换为稳定的声音强度指标。"],
        ["动态归一化", "根据环境噪声底和近期峰值适配不同音量。"],
        ["攻击快、释放慢的平滑", "增强时快速响应，减弱时平滑下降，降低闪烁感。"],
        ["突发增强", "在能量快速上升时突出鼓点和拍手等短时变化。"],
        ["离散量化", "将结果限制为 0-8，供板端直接映射。"],
    ], [5.0*cm, 11.2*cm]),
    heading2("4.2 串口协议"),
    p("律动协议固定为 6 字节：前两个字节为帧头 AA 5A，第 3 字节为类型，第 4、5 字节为载荷，第 6 字节为异或校验。单声道类型为 20，载荷为序号和等级；双声道类型为 26，载荷为左、右等级。校验由类型与两个载荷字节异或得到。板端只有在帧头、类型、等级范围和校验均正确时才刷新显示。"),
    make_table([
        ["模式", "帧格式", "说明"],
        ["单声道", "AA 5A 20 序号 等级 校验", "等级范围为 0-8。示例：AA 5A 20 01 03 22。"],
        ["双声道", "AA 5A 26 左级别 右级别 校验", "左右级别均限制为 0-8。"],
        ["校验", "类型 XOR 第 4 字节 XOR 第 5 字节", "用于过滤错误或不完整的传输数据。"],
    ], [3.0*cm, 7.2*cm, 6.0*cm]),
    heading2("4.3 板端处理流程"),
    p("固件采用非阻塞方式接收串口字节。接收状态机识别帧头后收集剩余字节，再进行类型、范围和校验判断；合法帧更新单声道或双声道等级并清零超时计数，非法帧丢弃。显示任务根据最新等级生成段码，周期任务同时检查超时条件。该结构将通信解析和显示刷新分开，便于定位协议或显示问题。"),
    heading2("4.4 关键人工调整"),
    p("在功能联调中，重点调整了三类内容：一是将等级范围严格限定为 0-8，避免异常数据越界点亮；二是将串口发送与音频采样解耦，固定约 50 ms 的发送节奏；三是根据数码管显示特性明确双声道的上、下半段映射，并增加超时清屏。上述内容直接服务于验收时的稳定观察和故障解释。"),
    heading1("5 系统测试与分析"),
    heading2("5.1 测试环境"),
    p("测试对象为 STC-B 学习板、USB 串口连接和 Windows 上位机工程。固件工程为 Keil C51 工程，上位机工程使用 Tauri/React/Rust 组织音频、协议、串口与界面代码。板端基础联调已确认蜂鸣器、LED 与数码管能够按程序响应；音乐律动整机效果以现场编译、烧录和上位机运行时的可观察现象为验收口径。"),
    heading2("5.2 功能测试用例"),
    make_table([
        ["测试项", "方法", "验收观察点"],
        ["等级映射", "依次发送 0-8 的合法单声道帧", "亮条由全灭到连续 8 位，点亮数量与等级一致。"],
        ["双声道显示", "发送左右等级不同的 26 帧", "同一数码管上、下半段分别变化。"],
        ["错误帧过滤", "修改校验或发送大于 8 的等级", "板端不以错误值刷新显示。"],
        ["失联回退", "停止发送，等待超过约 500 ms", "律动亮条清空，恢复空闲显示。"],
        ["系统音频", "播放鼓点清晰音乐，选择系统音频", "数码管随鼓点强弱变化，上位机状态正常。"],
        ["麦克风", "切换麦克风后拍手或说话", "亮条对外部声音强弱产生响应。"],
    ], [3.0*cm, 5.7*cm, 7.5*cm]),
    heading2("5.3 结果分析与验收建议"),
    p("验收时可先选择系统音频和节拍增强模式，播放鼓点明显的音乐，展示声音强弱与亮条长度之间的同步关系；随后切换双声道或麦克风模式，说明功能的可调性；最后停止上位机或断开串口，观察超时回退。若显示变化不明显，可优先提高灵敏度、降低环境保留上限，并检查是否选中了正确的 COM 口和音频输入源。"),
    heading1("6 总结与展望"),
    p("本人完成的音乐律动功能构成了从声音输入、上位机分析、串口控制到 STC-B 数码管显示的完整闭环。方案采用 0-8 级低带宽数据代替原始音频传输，利用固定帧、异或校验、范围检查和超时回退提高了链路的可解释性与稳定性。当前数码管输出的是整体强度亮条，双声道模式只进一步区分左右能量，并非多频段频谱。后续可扩展多频段帧载荷、加入设备枚举和丢帧统计，或更换 LED 点阵/外接屏以获得更丰富的可视化效果。"),
    PageBreak(),
    heading1("7 AI 协作说明"),
    p("使用的 AI 工具：ChatGPT（Codex）。", "BodyNoIndent"),
    p("AI 参与代码比例：约 30% 的音乐律动相关代码由 AI 生成初稿或辅助生成。该比例仅针对本人负责的音乐律动功能估计，不包含团队其他功能模块。", "BodyNoIndent"),
    p("人工修改的主要内容：", "BodyNoIndent"),
    p("1. 根据 STC-B 数码管硬件特性确定 0-8 级亮条和双声道上、下半段的显示映射，并检查其与板端段码逻辑的对应关系。", "BodyNoIndent"),
    p("2. 对串口帧的帧头、类型、等级范围、异或校验和超时回退进行人工核对和调整，保证异常数据不直接刷新显示。", "BodyNoIndent"),
    p("3. 结合实际验收场景调整上位机的发送周期、灵敏度和节拍响应参数，并整理测试步骤、工程提交清单和本报告内容。", "BodyNoIndent"),
    heading1("参考文献"),
    p("[1] 宏晶科技. STC15 系列单片机技术手册[EB/OL]. https://www.stcmcudata.com/, 2026-09-11.", "BodyNoIndent"),
    p("[2] Microsoft. WASAPI audio capture documentation[EB/OL]. https://learn.microsoft.com/windows/win32/coreaudio/wasapi, 2026-09-11.", "BodyNoIndent"),
    p("[3] Tauri. Tauri v2 documentation[EB/OL]. https://v2.tauri.app/, 2026-09-11.", "BodyNoIndent"),
])


doc = ReportDoc(str(OUT))
doc.multiBuild(story)
print(OUT)
