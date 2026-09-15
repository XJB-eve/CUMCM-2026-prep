import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const workspaceDir = process.cwd();
const skillDir = 'C:\\Users\\谢俊邦\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.904.11930\\skills\\presentations';
const runtimePython = 'C:\\Users\\谢俊邦\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe';
const buildDir = path.join(workspaceDir, '.stc-ppt-build');
const outputDir = path.join(workspaceDir, 'output', 'pptx');
const finalPath = path.join(outputDir, 'STC-B音乐律动可视化系统答辩PPT.pptx');
await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(outputDir, { recursive: true });
const { resolvePresentationFont, finalizePresentation } = await import(pathToFileURL(path.join(skillDir, 'container_tools', 'artifact_tool_utils.mjs')).href);
const font = resolvePresentationFont({ fontFamily: 'Microsoft YaHei' });
const ppt = Presentation.create({ slideSize: { width: 1280, height: 720 } });

const C = { navy:'#17365D', blue:'#2F75B5', pale:'#EAF2F8', ink:'#17212B', gray:'#5F6B76', line:'#C9D4DF', white:'#FFFFFF', green:'#198754' };
function box(slide, x,y,w,h, fill='none', line='none') { return slide.shapes.add({ geometry:'rect', position:{left:x,top:y,width:w,height:h}, fill, line:{fill:line,width:0} }); }
function text(slide, value, x,y,w,h, size=22, opts={}) {
  const s = slide.shapes.add({ geometry:'textbox', position:{left:x,top:y,width:w,height:h}, fill:'none', line:{fill:'none',width:0} });
  s.text = value;
  s.text.style = { typeface:font, fontSize:size, color:opts.color ?? C.ink, bold:opts.bold ?? false, align:opts.align ?? 'left', autoFit:'shrinkText', verticalAlignment:opts.verticalAlignment ?? 'top' };
  return s;
}
function title(slide, value, n) { text(slide, value, 72, 44, 970, 52, 32, {bold:true}); text(slide, `0${n}`, 1135, 48, 70, 34, 17, {color:C.blue, bold:true, align:'right'}); slide.shapes.add({geometry:'line', position:{left:72,top:111,width:1136,height:0}, line:{fill:C.line,width:1}}); }
function footer(slide) { text(slide, '夏季实训 STC 大作业  谢俊邦 202408010119', 72, 680, 700, 22, 11, {color:C.gray}); }
function bullet(slide, head, body, x,y,w) { text(slide, head, x,y,w,28,19,{bold:true,color:C.navy}); text(slide, body, x,y+27,w,52,16,{color:C.ink}); }

// 1
{ const s=ppt.slides.add(); s.background.fill=C.white; box(s,0,0,1280,720,C.navy); box(s,760,0,520,720,C.blue); text(s,'STC-B 音乐律动\n可视化系统',72,170,640,150,46,{bold:true,color:C.white}); text(s,'最终设计报告答辩',75,340,500,38,23,{color:'#D9E8F6'}); text(s,'计科 2401  谢俊邦\n202408010119',75,515,420,60,19,{color:C.white}); text(s,'声音采集\n实时分析\n串口显示',820,190,300,220,36,{bold:true,color:C.white}); s.speakerNotes.textFrame.setText('依据个人选题表和本地工程内容制作。'); }

// 2
{ const s=ppt.slides.add(); s.background.fill=C.white; title(s,'选题与设计目标',2); text(s,'选题：基于 STC-B 学习板的音乐律动可视化系统',72,145,1060,42,25,{bold:true,color:C.navy}); text(s,'把电脑声音或麦克风声音转化为学习板上直观可见的律动亮条。',72,200,1000,35,19,{color:C.gray}); bullet(s,'为什么这样分工','PC 端处理采样和滤波，STC-B 端集中完成串口校验与显示刷新。',72,295,500); bullet(s,'核心目标','音频强度映射为 0-8 级，数码管以连续亮条显示。',650,295,500); bullet(s,'验收关注点','显示是否跟随声音变化，协议是否可靠，断开后能否自动回退。',72,435,500); bullet(s,'可调参数','音频来源、检测模式、灵敏度、鼓点冲击与环境保留上限。',650,435,500); footer(s); }

// 3 diagram
{ const s=ppt.slides.add(); s.background.fill=C.white; title(s,'系统总体结构',3); const cols=[['声音输入','系统回环\n或麦克风'],['上位机分析','WASAPI 采样\nRMS 与动态平滑'],['串口传输','115200 baud\n固定 6 字节帧'],['STC-B 显示','数码管亮条\nLED 与超时回退']]; cols.forEach((c,i)=>{ const x=72+i*286; box(s,x,265,230,150,i===1?C.blue:C.pale,i===1?C.blue:C.line); text(s,c[0],x+18,286,195,28,20,{bold:true,color:i===1?C.white:C.navy,align:'center'}); text(s,c[1],x+18,335,195,58,17,{color:i===1?C.white:C.ink,align:'center'}); if(i<3) text(s,'→',x+238,315,36,40,30,{bold:true,color:C.blue,align:'center'}); }); text(s,'分层原则：计算密集的音频分析留在 Windows 端，学习板处理低带宽控制数据。',122,505,1036,36,20,{color:C.gray,align:'center'}); footer(s); }

// 4
{ const s=ppt.slides.add(); s.background.fill=C.white; title(s,'音乐律动核心实现',4); text(s,'音频处理',72,152,300,35,24,{bold:true,color:C.navy}); bullet(s,'输入来源','系统音频和麦克风均可作为输入。',72,205,430); bullet(s,'两种分析模式','低频律动适合鼓点和低音；节拍增强强调瞬态变化。',72,305,430); bullet(s,'稳定显示','动态噪声底、峰值估计和快攻慢释包络降低闪烁。',72,415,430); text(s,'板端显示与通信',650,152,420,35,24,{bold:true,color:C.navy}); bullet(s,'0-8 级亮条','单声道将等级显示为连续点亮的数码管。',650,205,440); bullet(s,'双声道模式','上半段代表左声道，下半段代表右声道。',650,305,440); bullet(s,'异常处理','帧头、范围和异或校验通过后才刷新；500 ms 无新帧则退出律动显示。',650,415,440); footer(s); }

// 5
{ const s=ppt.slides.add(); s.background.fill=C.white; title(s,'协议与演示流程',5); const rows=[['单声道','AA 5A 20 序号 等级 校验','等级 0-8'],['双声道','AA 5A 26 左级别 右级别 校验','上下半段显示'],['刷新节奏','每 50 ms 发送最新值','约 20 帧/秒'],['失联处理','连续 500 ms 无合法帧','恢复空闲显示']]; const table=s.tables.add({ left:72,top:150,width:1136,height:210, rows:5, columns:3 }); const vals=[['项目','协议或条件','效果'],...rows]; for(let r=0;r<vals.length;r++) for(let c=0;c<3;c++){ const cell=table.getCell(r,c); cell.value=vals[r][c]; cell.text.style={typeface:font,fontSize:16,color:r===0?C.white:C.ink,bold:r===0,align:r===0?'center':'left',autoFit:'shrinkText'}; cell.fill=r===0?C.navy:(r%2?C.white:C.pale); cell.border={color:C.line,width:1}; }
 text(s,'现场演示：连接 COM 口，选择系统音频，播放鼓点明显的音乐，观察亮条变化；停止上位机后观察自动回退。',92,445,1080,66,20,{color:C.ink,align:'center'}); footer(s); }

// 6
{ const s=ppt.slides.add(); s.background.fill=C.white; title(s,'调查表中的团队分工',6); text(s,'以下内容依据“用户问题调查表与选题流程表”，反映团队在 STC-B 基础模块上的职责分配。',72,145,1130,42,19,{color:C.gray}); const data=[['成员','调查表中负责的模块','与本项目的关系'],['吴宇珂','LED 灯光模式、反应测试；蜂鸣器与 LED 提示；红外发射。','提供板载显示与声光交互经验。'],['缪朴奂','DS1302 时钟、温度采集、超声波测距；按键切换与串口更新。','提供定时、传感和串口交互模块。'],['谢俊邦','红外接收学习与存储、振动阈值逻辑、数码管/LED 信息显示；本次负责音乐律动核心。','完成音频强度到数码管亮条的可视化。']]; const table=s.tables.add({left:72,top:230,width:1136,height:300,rows:4,columns:3}); for(let r=0;r<data.length;r++) for(let c=0;c<3;c++){const cell=table.getCell(r,c);cell.value=data[r][c];cell.text.style={typeface:font,fontSize:r===0?17:16,color:r===0?C.white:C.ink,bold:r===0,align:r===0?'center':'left',autoFit:'shrinkText'};cell.fill=r===0?C.navy:(r%2?C.white:C.pale);cell.border={color:C.line,width:1};} text(s,'本次答辩聚焦谢俊邦的“音乐律动可视化”选题，同时说明团队模块可在同一学习板平台复用。',72,575,1100,35,18,{color:C.green,align:'center'}); footer(s); }

// 7
{ const s=ppt.slides.add(); s.background.fill=C.white; title(s,'总结与答疑要点',7); text(s,'项目结论',72,150,250,35,25,{bold:true,color:C.navy}); text(s,'系统完成“声音采集—实时分析—串口传输—板端显示”的协同设计。',72,203,1020,44,22,{color:C.ink}); text(s,'可能提问',72,315,250,35,25,{bold:true,color:C.navy}); bullet(s,'为什么不在单片机上直接采音频？','PC 端可以调用系统音频接口并进行浮点滤波，学习板只接收 0-8 级数据，资源压力更小。',72,365,500); bullet(s,'这是频谱显示吗？','当前是总体强度的条形显示；双声道模式区分左右声道，不等同于 8 个独立频段。',650,365,500); text(s,'谢谢老师',72,590,1136,52,34,{bold:true,color:C.blue,align:'center'}); footer(s); }

const candidatePath = path.join(buildDir, 'candidate.pptx');
await (await PresentationFile.exportPptx(ppt)).save(candidatePath);
await finalizePresentation({ workspaceDir, candidatePath, finalPath, pythonExecutable:runtimePython, integrityValidatorPath:path.join(skillDir,'container_tools','inspect_presentation_package_integrity.py'), layoutValidatorPath:path.join(skillDir,'container_tools','inspect_presentation_layout_geometry.py'), layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','5','--require-native-table-slide','6'], requiredNativeTableOwnerSlides:[5,6], fontPolicy:{basis:'design',families:[font]}, verifyArtifactToolImport:true, receiptPath:path.join(buildDir,'validation.json') });
console.log(finalPath);
