import {readFile,writeFile,readdir} from 'node:fs/promises';
import path from 'node:path';
const output=path.resolve('dist'),base='/breeze-voice-workflow-skill';
function target(url){
  if(url.startsWith('//') || url===base || url.startsWith(base+'/'))return url;
  if(/^\/codex-reset(?:\/|[?#]|$)/.test(url))return 'https://blog.atipiu.org'+url;
  return base+url;
}
// Astro generates its island/script URLs with base. Authored and frozen legacy HTML need the same prefix.
function quotedUrls(text){return text.replace(/(["'])(\/[^"'\s<>]*)\1/g,(_,quote,url)=>quote+target(url)+quote);}
async function walk(folder){
  for(const entry of await readdir(folder,{withFileTypes:true})){
    const file=path.join(folder,entry.name);
    if(entry.isDirectory())await walk(file);
    else if(entry.name.endsWith('.html'))await writeFile(file,quotedUrls(await readFile(file,'utf8')));
  }
}
await walk(output);
const app=path.join(output,'assets/app.js');await writeFile(app,quotedUrls(await readFile(app,'utf8')));
const searchFile=path.join(output,'search.json'),search=JSON.parse(await readFile(searchFile,'utf8'));
for(const item of search)if(item.url.startsWith('/'))item.url=target(item.url);
await writeFile(searchFile,JSON.stringify(search));
await writeFile(path.join(output,'.nojekyll'),'');
console.log('Prepared GitHub Pages paths; live Codex service stays on blog.atipiu.org.');
