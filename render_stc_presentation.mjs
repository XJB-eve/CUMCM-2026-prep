import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';

const input = path.join(process.cwd(), 'output', 'pptx', 'STC-B音乐律动可视化系统答辩PPT.pptx');
const output = path.join(process.cwd(), 'output', 'pptx', 'qa-artifact');
await fs.mkdir(output, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(input));
for (const [i, slide] of presentation.slides.items.entries()) {
  const image = await slide.export({ format: 'png', scale: 1 });
  await fs.writeFile(path.join(output, `slide-${i + 1}.png`), new Uint8Array(await image.arrayBuffer()));
}
console.log(output);
