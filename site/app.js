'use strict';
const $=s=>document.querySelector(s);
let data=null, favorites=new Set(), tab='all';
try { favorites=new Set(JSON.parse(localStorage.getItem('sg-public-favorites')||'[]')); } catch {}
async function saveFavorites(){localStorage.setItem('sg-public-favorites',JSON.stringify([...favorites]));}
async function load(){
 try{
  const r=await fetch('data.json',{cache:'no-store'}); if(!r.ok)throw Error('HTTP '+r.status);data=await r.json();
  $('#station').replaceChildren(new Option('所有捷運站',''),...data.criteria.stations.concat(data.criteria.optional_stations).map(s=>new Option(s,s)));
  $('#updated').textContent=data.last_success?new Date(data.last_success).toLocaleString('zh-TW',{timeZone:'Asia/Singapore'})+' SGT':'尚未成功';
  const ss=data.source_status,age=data.last_success?(Date.now()-Date.parse(data.last_success))/3600000:Infinity;
  $('#status').textContent=ss.errors.length||!ss.refreshed||age>36?'更新需注意：尚未取得完整即時資料。候選連結可先瀏覽，租金、屋齡與可租狀態請向原站確認。':'已更新候選房源。待確認項目不代表已符合全部條件。';
  $('#diagnostics').textContent=JSON.stringify(ss,null,2);render();
 }catch(e){$('#status').textContent='房源資料載入失敗，請重新整理。'+e.message;}
}
function element(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
function render(){if(!data)return;let items=data.listings.filter(i=>{if(tab==='saved')return favorites.has(i.id);if(tab==='all')return i.status!=='excluded';return i.status===tab;});const q=$('#search').value.toLowerCase();items=items.filter(i=>(i.title+' '+(i.station||'')).toLowerCase().includes(q)&&(!$('#station').value||i.station===$('#station').value)&&(!$('#room').value||i.room===$('#room').value));items.sort($('#sort').value==='price'?(a,b)=>(a.price??Infinity)-(b.price??Infinity):(a,b)=>b.first_seen.localeCompare(a.first_seen));
 $('#cards').replaceChildren();$('#empty').hidden=!!items.length;$('#total').textContent=data.listings.filter(i=>i.status!=='excluded').length;$('#matches').textContent=data.listings.filter(i=>i.status==='match').length;$('#saved').textContent=favorites.size;
 for(const i of items){const c=element('article',undefined,'card'),top=element('div',undefined,'card-top'),body=element('div',undefined,'card-body');top.append(element('span',i.station||'捷運站待確認'));const star=element('button',favorites.has(i.id)?'♥':'♡');star.setAttribute('aria-label','收藏 '+i.title);star.setAttribute('aria-pressed',favorites.has(i.id));star.onclick=async()=>{favorites.has(i.id)?favorites.delete(i.id):favorites.add(i.id);try{await saveFavorites();}catch{$('#status').textContent='無法保存收藏，請確認瀏覽器允許本機儲存。';}render();};top.append(star);body.append(element('h2',i.title),element('div',i.price===null?'租金待確認':'S$'+i.price.toLocaleString()+' / 月','price'));const pills=element('div',undefined,'pills');for(const t of [i.room==='master'?'獨立衛浴':i.room==='common'?'共用衛浴':'衛浴待確認',i.built?i.built+' 年完工':'屋齡待確認',i.status==='match'?'符合條件':i.status==='excluded'?'不符合':'待確認',...(i.stale?['舊資料']:[])])pills.append(element('span',t,'pill'));body.append(pills,element('p',(i.walk_minutes?i.walk_minutes+' 分鐘步行 · ':'')+'可租狀態：'+(i.availability==='unavailable'?'已租出':i.availability==='available'?'可租':'需詢問'),'detail'),element('p','來源 '+i.source+' · 最近讀取 '+(i.last_seen?new Date(i.last_seen).toLocaleDateString('zh-TW'):'尚未即時驗證'),'detail'));const a=element('a','查看原始房源 ↗');try{const u=new URL(i.url);if(u.protocol==='https:'){a.href=u.href;a.target='_blank';a.rel='noopener noreferrer';body.append(a);}}catch{}c.append(top,body);$('#cards').append(c);}}
for(const s of ['#search','#station','#room','#sort'])$(s).addEventListener('input',render);
for(const b of document.querySelectorAll('[data-tab]'))b.onclick=()=>{tab=b.dataset.tab;for(const x of document.querySelectorAll('[data-tab]'))x.classList.toggle('active',x===b);render();};

load();
