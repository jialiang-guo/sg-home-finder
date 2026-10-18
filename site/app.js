'use strict';
const $=s=>document.querySelector(s);
let data=null,decisions={},tab='all',selectionReady=false;
function key(i){const u=new URL(i.url);let m;if(u.hostname==='rentinsingapore.com.sg'&&(m=u.pathname.match(/^\/ID(\d+)\/?$/)))return 'RentInSingapore:'+m[1];if(u.hostname==='cove.sg'&&(m=u.pathname.match(/^\/listings\/(\d+)(?:-|\/|$)/)))return 'Cove:'+m[1];return 'legacy:'+i.id;}
function choice(i){return decisions[key(i)]?.decision||'reset';}
function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
async function load(){
 $('#refresh').disabled=true;selectionReady=false;
 try{
  const [r,d]=await Promise.all([fetch('data.json',{cache:'no-store'}),fetch('decisions.json',{cache:'no-store'})]);
  if(!r.ok||!d.ok)throw Error('資料讀取失敗');
  data=await r.json();const saved=await d.json();if(saved.version!==1||!saved.decisions)throw Error('選擇紀錄格式錯誤');decisions=saved.decisions;selectionReady=true;
  const prev=$('#station').value;$('#station').replaceChildren(new Option('所有捷運站',''),...data.criteria.stations.concat(data.criteria.optional_stations).map(s=>new Option(s,s)));$('#station').value=prev;
  $('#updated').textContent=data.last_success?new Date(data.last_success).toLocaleString('zh-TW',{timeZone:'Asia/Singapore'})+' SGT':'尚未成功';
  const ss=data.source_status,age=data.last_success?(Date.now()-Date.parse(data.last_success))/3600000:Infinity;
  $('#status').textContent=ss.errors.length||!ss.refreshed||age>36?'更新需注意：部分資料未更新，請查看來源狀態。':'房源已更新。待確認不等於已符合全部條件。';
  $('#diagnostics').textContent=JSON.stringify(ss,null,2);$('#selection-status').textContent='已載入 GitHub 共同選擇。';render();
 }catch(e){$('#selection-status').textContent='無法載入共同選擇，暫停操作以免誤判排除狀態。請重試。';$('#cards').replaceChildren();}
 finally{$('#refresh').disabled=false;}
}
function request(i,decision){
 if(!selectionReady)return;
 const payload={listing_key:key(i),decision};
 const u=new URL('https://github.com/jialiang-guo/sg-home-finder/issues/new');u.searchParams.set('title','[Home decision] '+key(i)+' '+decision);u.searchParams.set('body',JSON.stringify(payload,null,2));
 window.open(u.href,'_blank','noopener,noreferrer');
 $('#selection-status').textContent='請在 GitHub 按 Create 送出。此處尚未變更；同步完成後按「重新載入選擇」。';
}
function reasons(i){const a=[];
 if(i.price==null)a.push('月租待確認');else if(i.price>data.criteria.budget)a.push('超過預算');
 if(!i.station)a.push('捷運站待確認');
 if(!i.built)a.push('屋齡待確認');else if(new Date().getFullYear()-i.built>10)a.push('屋齡超過10年');
 if(i.property_type==='hdb')a.push('HDB，不符合 Condo');else if(!i.condo)a.push('住宅類型待確認');
 if(i.private_bathroom!==true)a.push(i.private_bathroom===false?'共用衛浴：不符合主臥私人衛浴偏好':'私人衛浴待確認');
 if(i.room==='common')a.push('普通房：需看照片評估裝潢');
 if(i.availability==='unknown')a.push('可租日期待確認');else if(i.availability==='unavailable')a.push('已不可租');
 if(i.stale)a.push('未重新驗證的舊資料');
 return a.length?a:['資料符合已設定條件'];}
function render(){if(!data||!selectionReady)return;
 let items=data.listings.filter(i=>{const c=choice(i);if(tab==='rejected')return c==='reject';if(c==='reject')return false;if(tab==='saved')return c==='keep';if(tab==='all')return i.status!=='excluded';return i.status===tab;});
 const q=$('#search').value.toLowerCase();items=items.filter(i=>(i.title+' '+(i.station||'')+' '+key(i)).toLowerCase().includes(q)&&(!$('#station').value||i.station===$('#station').value)&&(!$('#room').value||i.room===$('#room').value));items.sort($('#sort').value==='price'?(a,b)=>(a.price??Infinity)-(b.price??Infinity):(a,b)=>b.first_seen.localeCompare(a.first_seen));
 $('#cards').replaceChildren();$('#empty').hidden=!!items.length;$('#total').textContent=data.listings.filter(i=>i.status!=='excluded'&&choice(i)!=='reject').length;$('#matches').textContent=data.listings.filter(i=>i.status==='match'&&choice(i)!=='reject').length;$('#saved').textContent=data.listings.filter(i=>choice(i)==='keep').length;
 for(const i of items){const tr=el('tr');
 const title=el('td');const a=el('a',i.title);const u=new URL(i.url);if(u.protocol==='https:'){a.href=u.href;a.target='_blank';a.rel='noopener noreferrer';}title.append(a,el('small',key(i),'source-id'));tr.append(title);
 tr.append(el('td',i.price==null?'待確認':'S$'+i.price.toLocaleString(),i.price>2500?'bad':'price-cell'));
 tr.append(el('td',(i.station||'捷運站待確認')+'\n'+(i.walk_minutes?i.walk_minutes+' 分鐘步行':'步行時間待確認')));
 tr.append(el('td',(i.condo?'Condo':i.property_type==='hdb'?'HDB':'類型待確認')+'\n'+(i.built?i.built+' 完工 · 約'+(new Date().getFullYear()-i.built)+'年':'屋齡待確認')));
 const bath=i.private_bathroom===true?'私人衛浴':i.private_bathroom===false?'共用衛浴':'衛浴待確認';tr.append(el('td',(i.room==='master'?'主臥 / 套房':i.room==='common'?'普通房':'房型待確認')+'\n'+bath));
 const notes=el('td'),ul=el('ul');for(const s of reasons(i))ul.append(el('li',s));notes.append(ul);tr.append(notes);
 const actions=el('td'),c=choice(i);actions.append(el('strong',c==='keep'?'已保留':c==='reject'?'已排除':'尚未選擇','decision-label'));
 for(const [state,label] of c==='reject'?[['reset','復原 ↗']]:[['keep','保留 ↗'],['reject','排除 ↗'],...(c==='keep'?[['reset','取消保留 ↗']]:[])]){const b=el('button',label);b.disabled=c===state;b.onclick=()=>request(i,state);actions.append(b);}tr.append(actions);$('#cards').append(tr);
 }
}
for(const s of ['#search','#station','#room','#sort'])$(s).addEventListener('input',render);
for(const b of document.querySelectorAll('[data-tab]'))b.onclick=()=>{tab=b.dataset.tab;for(const x of document.querySelectorAll('[data-tab]'))x.classList.toggle('active',x===b);render();};
$('#refresh').onclick=load;load();
