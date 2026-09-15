from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.colors import HexColor
from pathlib import Path

OUT = Path(__file__).parent / "output" / "pdf" / "STC-B音乐律动可视化系统最终设计报告.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

try:
    pdfmetrics.registerFont(TTFont("YaHei", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
    FONT = "YaHei"
except Exception:
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    FONT = "STSong-Light"

NAVY = HexColor("#17365D")
BLUE = HexColor("#DCE6F1")
PALE = HexColor("#F4F7FB")
GRAY = HexColor("#666666")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCN", fontName=FONT, fontSize=22, leading=32, alignment=TA_CENTER, textColor=colors.black, spaceAfter=20))
styles.add(ParagraphStyle(name="SubTitleCN", fontName=FONT, fontSize=13, leading=21, alignment=TA_CENTER, textColor=GRAY))
styles.add(ParagraphStyle(name="H1CN", fontName=FONT, fontSize=15, leading=24, textColor=colors.black, spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name="H2CN", fontName=FONT, fontSize=12, leading=20, textColor=colors.black, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyCN", fontName=FONT, fontSize=10.5, leading=19, alignment=TA_JUSTIFY, firstLineIndent=21, spaceAfter=6))
styles.add(ParagraphStyle(name="BodyNoIndent", fontName=FONT, fontSize=10.5, leading=18, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallCN", fontName=FONT, fontSize=8.7, leading=14, textColor=colors.black))
styles.add(ParagraphStyle(name="CaptionCN", fontName=FONT, fontSize=9, leading=14, alignment=TA_CENTER, textColor=GRAY, spaceBefore=4, spaceAfter=8))

def P(text, style="BodyCN"):
    return Paragraph(text, styles[style])

def table(rows, widths, header=True, size="SmallCN"):
    body = [[P(str(c), size) for c in row] for row in rows]
    t = Table(body, colWidths=widths, repeatRows=1 if header else 0, hAlign="CENTER")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
        for col in range(len(rows[0])):
            body[0][col] = Paragraph(str(rows[0][col]), ParagraphStyle("head", parent=styles[size], textColor=colors.white, alignment=TA_CENTER))
        t = Table(body, colWidths=widths, repeatRows=1, hAlign="CENTER")
        commands += [("BACKGROUND", (0, 1), (-1, -1), colors.white), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE])]
    t.setStyle(TableStyle(commands))
    return t

def page_number(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(HexColor("#D9D9D9"))
    canvas.line(2.2*cm, 1.55*cm, A4[0]-2.2*cm, 1.55*cm)
    canvas.setFont(FONT, 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(2.2*cm, 1.05*cm, "STC-B 音乐律动可视化系统最终设计报告")
    canvas.drawRightString(A4[0]-2.2*cm, 1.05*cm, f"第 {doc.page} 页")
    canvas.restoreState()

story = []
story += [Spacer(1, 4.2*cm), P("STC-B 音乐律动可视化系统", "TitleCN"), P("最终设计报告", "TitleCN"), Spacer(1, 0.5*cm), P("课程：夏季实训 STC 大作业", "SubTitleCN"), P("班级：计科 2401　　姓名：谢俊邦　　学号：202408010119", "SubTitleCN"), Spacer(1, 3.8*cm), P("提交内容：最终设计报告 PDF", "SubTitleCN"), PageBreak()]

story += [P("摘要", "H1CN"), P("本项目面向电脑音乐播放、现场拍手或麦克风输入等场景，设计一套由 Windows 上位机与 STC-B 学习板协同完成的音乐律动可视化系统。上位机采集系统回环音频或麦克风音频，经能量分析、动态归一化和包络平滑后得到 0-8 级强度；学习板通过 USB 虚拟串口接收带校验的数据帧，并在 8 位数码管上输出连续亮条或左右声道的上下半段显示。系统将计算量较大的音频处理放在 PC 端，将单片机侧限定为通信校验、显示刷新与超时回退，从而在 STC-B 的硬件资源约束下获得直观、稳定且可调节的可视化效果。"), P("关键词：STC-B；串口通信；音频分析；数码管；音乐律动", "BodyNoIndent"), P("1 设计背景与目标", "H1CN"), P("传统学习板实验常把数码管、UART 和定时器分别演示，缺少一个能够把多个基础模块连成完整交互闭环的应用。本设计以“声音变化被看见”为目标：电脑端把声音转换成低带宽的强度信息，学习板将其显示为亮条。该方案既保留了嵌入式端的实时响应，也避免在 8051 单片机上直接完成高采样率音频处理。"), P("依据个人选题表，本设计需完成数码管亮条显示、115200 baud 串口收发、10 ms 周期任务、按键与 LED 调试提示，并支持系统回环/麦克风输入、低频律动/节拍增强模式、500 ms 失联回退以及上位机参数调节。"), P("2 需求分析", "H1CN"), table([["需求", "对应设计"], ["可见性", "将音频强度映射为 0-8 级，数码管以连续亮条输出。"], ["实时性", "上位机按 50 ms 周期发送最新值，目标刷新约 20 帧/秒。"], ["可靠性", "固定帧头、范围检查与异或校验；500 ms 未收到合法帧自动退出律动显示。"], ["可调性", "提供音频来源、检测模式、灵敏度、鼓点冲击和环境保留上限。"], ["可扩展性", "保留单声道帧，并扩展双声道帧以利用数码管上下半段。"]], [3.2*cm, 12.4*cm]), Spacer(1, 0.3*cm), PageBreak(), P("3 总体方案", "H1CN"), table([["层级", "输入", "处理", "输出"], ["Windows 上位机", "系统回环或麦克风", "采样、音频分析、平滑和量化", "0-8 级串口帧"], ["串口链路", "USB 虚拟串口", "115200 baud，8N1，固定 6 字节帧", "可靠传递等级数据"], ["STC-B 学习板", "合法数据帧", "帧校验、显示映射、10 ms 超时计数", "8 位数码管与 LED 提示"]], [3*cm, 3.8*cm, 5.1*cm, 3.7*cm]), P("图 1 系统采用 PC 端分析与学习板端显示的分层结构", "CaptionCN")]

story += [P("4 硬件与软件组成", "H1CN"), table([["部分", "实现内容", "作用"], ["学习板", "STC15F2K60S2、8 位数码管、LED、蜂鸣器、按键、UART", "完成串口接收、显示与本地交互。"], ["USB 串口", "CH340 虚拟串口，115200 baud", "建立电脑与学习板之间的双向通道。"], ["上位机", "Tauri 2、React、TypeScript、Rust", "提供界面、采集音频并生成控制帧。"], ["音频接口", "Windows WASAPI", "获取默认系统输出回环或默认麦克风输入。"]], [3.0*cm, 6.0*cm, 6.6*cm]), P("提交的固件包以 Keil C51 工程 1.c 为核心，提交的上位机包把音频处理、协议、串口发送分别组织在 audio.rs、protocol.rs、serial.rs 与 service.rs 中。两个工程包还包含按键控制、媒体控制、提醒音、硬件 PIN 认证与本地保险箱等协作开发功能；本报告聚焦本人选题中的音乐律动可视化部分。"), P("团队模块分工依据用户问题调查表：吴宇珂负责 LED 灯光模式、反应测试、蜂鸣器/LED 提示与红外发射；缪朴奂负责 DS1302 时钟、温度采集、超声波测距、按键切换与串口更新；谢俊邦负责红外接收学习与存储、振动阈值逻辑、数码管/LED 信息显示，并完成本次音乐律动核心设计。"), PageBreak(), P("5 音频处理与强度量化", "H1CN"), P("上位机以 48 kHz、双声道浮点数据进行处理。低频律动模式重点观察约 55-260 Hz 的能量，适合鼓点和低音明显的曲目；节拍增强模式综合低、中、高频瞬态，适合节奏密集或打击乐较多的声音。两种模式均以 RMS 能量作为基础量，避免逐采样点判断造成的闪烁。"), table([["步骤", "处理目的"], ["分频/能量计算", "突出低频律动或节拍瞬态，减少无关频段干扰。"], ["动态噪声底与峰值估计", "适应不同歌曲和不同系统音量。"], ["攻击快、释放慢的包络", "声音增强时快速响应，声音降低时平滑回落。"], ["突发增强", "在能量快速上升时提高显示变化，使鼓点更明显。"], ["0-8 级量化", "将连续强度压缩为学习板可直接显示的离散等级。"]], [4.4*cm, 11.2*cm]), P("单声道显示时，任一有效等级均对应 1-8 个连续点亮的数码管；双声道显示时，左声道控制每位的上半段，右声道控制下半段，上下同时激活时显示完整的“8”。因此双声道模式表达的是左右声道能量差异，而不是 8 个独立频段的频谱图。"), PageBreak()]

story += [P("6 串口协议与板端逻辑", "H1CN"), P("音乐律动采用固定长度 6 字节协议，前两个字节为帧头 AA 5A，最后一个字节为类型与载荷的异或校验。板端仅在帧头、类型、范围和校验均正确时更新显示，从而使噪声字节或不完整帧不会造成错误点亮。"), table([["模式", "数据帧", "含义"], ["单声道", "AA 5A 20 序号 等级 校验", "等级为 0-8，兼容基础亮条显示。"], ["双声道", "AA 5A 26 左级别 右级别 校验", "左右级别均为 0-8，映射数码管上下半段。"], ["校验", "类型 XOR 第 4 字节 XOR 第 5 字节", "用于识别传输错误。"]], [3.0*cm, 7.0*cm, 5.6*cm]), P("例如单声道序号为 01、显示 3 格时，帧为 AA 5A 20 01 03 22。双声道的校验则由 26、左级别和右级别异或得到。上位机使用独立发送节奏，每 50 ms 读取最新分析结果并发送，避免音频回调直接阻塞串口。"), P("板端以 10 ms 周期任务维护新鲜度计数。每收到合法音乐帧即清零；连续 50 个周期未收到数据时，即约 500 ms，板端清空律动条并回到温度/空闲显示。该机制覆盖关闭上位机、拔出串口和传输中断等情况，避免旧画面长期残留。"), P("7 人机交互设计", "H1CN"), table([["界面项目", "可选项或反馈"], ["连接设置", "选择 USB 虚拟串口并刷新端口列表。"], ["音频来源", "系统音频 / 麦克风。"], ["检测方式", "低频律动 / 节拍增强。"], ["声道模式", "单声道 / 双声道（上半左、下半右）。"], ["参数调节", "灵敏度、鼓点冲击、环境保留上限。"], ["运行反馈", "当前信号强度、运行状态、帧率和错误提示。"]], [4.4*cm, 11.2*cm]), P("界面的设计重点是让验收时可直接看见输入、参数、运行状态和输出之间的对应关系。演示时优先选择鼓点清晰的音乐，先以系统音频与节拍增强模式展示明显变化，再切换麦克风或双声道模式说明系统的可调性。"), PageBreak()]

story += [P("8 测试与验收说明", "H1CN"), P("本项目按“板端基础功能、协议一致性、上位机处理、整机演示”四层进行核对。板端基础烧录已验证蜂鸣器、LED 与数码管可按程序同步工作；其余项目应在最终工程编译、烧录和上位机运行后，按下表完成现场复核。表中测试口径以可观察结果为准，便于答疑验收。"), table([["测试项", "方法", "预期现象"], ["0-8 级映射", "依次发送 0 至 8 级合法单声道帧", "数码管从全灭到连续 8 位亮条，数量与等级一致。"], ["双声道显示", "发送左右等级不同的 26 帧", "同一数码管的上、下半段分别反映左右声道能量。"], ["错误帧过滤", "修改校验和或发送大于 8 的等级", "板端不更新为错误值。"], ["失联回退", "停止发送并等待超过 500 ms", "亮条清空并恢复空闲显示。"], ["系统音频演示", "播放鼓点明显音乐，选择系统音频", "亮条随鼓点变化，界面持续显示运行状态。"], ["麦克风演示", "切换麦克风并拍手或说话", "强度随外部声音变化。"]], [3.0*cm, 6.0*cm, 6.6*cm]), P("验收演示建议流程：第一步，连接学习板并在上位机选择正确 COM 口；第二步，选择系统音频和节拍增强模式后开始律动；第三步，播放节拍明显的音乐，观察数码管与界面强度同步变化；第四步，切换双声道或麦克风模式，展示扩展能力；第五步，停止上位机，观察约 500 ms 后学习板自动恢复空闲状态。"), P("9 已知边界与改进方向", "H1CN"), P("当前数码管输出的是总体强度的条形显示，双声道模式进一步区分左右声道；它不是多频段频谱瀑布图。若后续需要真正的 8 频段可视化，可扩展帧载荷并使用 LED 点阵或外接屏幕。其次，当前音频设备以默认系统设备为主，后续可增加设备枚举；还可加入串口确认、丢帧统计和参数预设，进一步提升可维护性。"), P("10 结论", "H1CN"), P("本设计以两个提交工程包中的固件和上位机源码为基础，形成从声音采集、实时分析、串口传输到 STC-B 数码管显示的软硬件协同方案。系统以低带宽等级帧替代原始音频传输，并通过校验、范围检查和超时回退处理异常。音乐律动为本人选题的核心功能，其他板端/上位机模块体现团队对同一学习板平台的协作开发。"), Spacer(1, 0.4*cm), P("附录 最终提交工程包", "H1CN"), table([["压缩包", "实际包含内容"], ["大作业工程固件.tar", "Keil C51 工程：1.c、1.uvproj、启动文件、STCBSP_V3.6 库及 BSP 头文件。"], ["大作业工程上位机.tar", "Tauri/React/Rust 工程：音频、协议、串口、控制器、保险箱、界面与设计说明源码。"]], [4.4*cm, 11.2*cm])]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=2.2*cm, leftMargin=2.2*cm, topMargin=2.1*cm, bottomMargin=2.1*cm, title="STC-B 音乐律动可视化系统最终设计报告", author="谢俊邦")
doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
print(OUT)
