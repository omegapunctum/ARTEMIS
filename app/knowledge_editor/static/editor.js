const $ = (id) => document.getElementById(id);
const API = '/api/knowledge-editor';
const state = {token:null,user:null,record:null,dirty:false,busy:false,drafts:[],queue:[],published:[]};
const labels = {
  workflow:{draft:'Черновик',submitted:'На проверке',changes_requested:'Нужны исправления',request_changes:'Нужны исправления',accepted:'Принято редакционно',rejected:'Отклонено',published:'Опубликовано'},
  source:{unknown:'Неизвестен',primary:'Первичный',scholarly:'Научная публикация',institutional:'Институциональный',other:'Другой'},
  kind:{factual:'Проверяемое сведение',observation:'Наблюдение',inference:'Вывод',interpretation:'Интерпретация',hypothesis:'Гипотеза',counterfactual:'Условный сценарий'},
  confidence:{unknown:'Не определена',low:'Низкая',medium:'Средняя',high:'Высокая'},
  relation:{supports:'Поддерживает',challenges:'Оспаривает',contextualizes:'Даёт контекст'},
  strength:{direct:'Источник прямо сообщает это',indirect:'Ограниченный вывод из источника',background:'Общий контекст'},
  review:{owner_self_review:'Проверка автором записи',separate_principal_review:'Проверка другим аккаунтом',distinct_editorial_review:'Проверка другим аккаунтом'}
};
for(const [id,values] of [['source_type',labels.source],['claim_kind',labels.kind],['claim_confidence',labels.confidence],['evidence_relation',labels.relation],['evidence_strength',labels.strength]]){
  for(const [value,label] of Object.entries(values)){const option=document.createElement('option');option.value=value;option.textContent=label;$(id).append(option);}
}
const defaults = () => ({entity:{name:'',description:''},source:{title:'',author:null,source_type:'unknown',url:null,bibliographic_reference:null,publication:null,accessed_on:null,rights:'unknown'},claim:{statement:'',claim_kind:'factual',origin:'user',confidence:'unknown',confidence_basis:null,uncertainty:''},evidence:{locator:'',relation_to_claim:'contextualizes',evidence_strength:'background',native_expression:'',native_precision:'unresolved'},human_authored_attestation:false});
const bindings = {entity_name:['entity','name'],entity_description:['entity','description'],source_title:['source','title'],source_url:['source','url'],source_reference:['source','bibliographic_reference'],source_author:['source','author'],source_type:['source','source_type'],source_rights:['source','rights'],source_publication:['source','publication'],source_expression:['evidence','native_expression'],claim_statement:['claim','statement'],claim_kind:['claim','claim_kind'],claim_confidence:['claim','confidence'],confidence_basis:['claim','confidence_basis'],claim_uncertainty:['claim','uncertainty'],evidence_locator:['evidence','locator'],evidence_relation:['evidence','relation_to_claim'],evidence_strength:['evidence','evidence_strength']};
function notice(text){$('message').textContent=text;$('message').hidden=!text;}
function clearError(){$('error').hidden=true;$('error').textContent='';}
function explain(error){
  const messages={401:'Сессия завершилась. Войдите снова; введённый текст остаётся в форме.',403:'У этого аккаунта нет разрешения на действие.',404:'Запись не найдена или недоступна этому аккаунту.',409:'Версия записи изменилась. Проверьте актуальную версию перед повторным действием.',429:'Слишком много запросов. Повторите действие немного позже.',503:'Сервер сейчас не может сохранить запись. Текст остаётся в форме; повторите сохранение позже.'};
  let text=error.name==='AbortError'?'Сервер не ответил вовремя. Сохранение не подтверждено. Текст остаётся в форме; повторите запрос.':error.status?messages[error.status]||`Действие не выполнено (код ${error.status}). Проверьте поля и повторите запрос.`:'Нет связи с сервером ARTEMIS. Сохранение не подтверждено. Проверьте подключение и повторите запрос.';
  if(error.status===422){text='Запись не готова к этому действию. Проверьте обязательные поля: название объекта и источника, ссылка или библиография, утверждение, точный locator, исходная формулировка и подтверждение авторства.';}
  if(error.status===401&&error.path==='/api/auth/login')text='Не удалось войти. Проверьте электронную почту и пароль.';
  if(error.status===422&&Array.isArray(error.detail)){
    const invalid=error.detail.find(item=>item.loc?.includes('url'));
    if(invalid)text='Проверьте ссылку на источник: нужен полный адрес http:// или https:// без пароля и пробелов.';
    if(error.detail.some(item=>String(item.msg).includes('confidence_basis_required')))text='Для выбранной оценки уверенности укажите основание, либо оставьте уверенность неопределённой.';
  }
  if(typeof error.detail==='string' && error.status!==500 && error.status!==503){text+=' '+error.detail;}
  $('error').textContent=text;$('error').hidden=false;
  if(error.status===409&&state.record)$('conflict-panel').hidden=false;
  if(error.status===401){state.token=null;$('auth-panel').hidden=false;}
}
async function request(path,{method='GET',body,authenticated=true,retry=true}={}){
  const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),20000);
  try{
    const headers={'Accept':'application/json'};if(body!==undefined)headers['Content-Type']='application/json';if(authenticated&&state.token)headers.Authorization=`Bearer ${state.token}`;
    const response=await fetch(path,{method,headers,credentials:'same-origin',body:body===undefined?undefined:JSON.stringify(body),signal:controller.signal});
    if(response.status===401&&authenticated&&retry){await refresh();return request(path,{method,body,authenticated,retry:false});}
    let data=null;try{data=await response.json();}catch{}
    if(!response.ok){const error=new Error('Request failed');error.status=response.status;error.detail=data?.detail;error.path=path;throw error;}
    return data;
  }finally{clearTimeout(timeout);}
}
async function refresh(){const data=await request('/api/auth/refresh',{method:'POST',authenticated:false});state.token=data.access_token;}
function setBusy(busy){state.busy=busy;document.body.setAttribute('aria-busy',String(busy));for(const button of document.querySelectorAll('button')){button.disabled=busy;button.setAttribute('aria-busy',String(busy));}if(!busy)renderPermissions();}
async function act(work){if(state.busy)return;clearError();setBusy(true);try{await work();}catch(error){explain(error);}finally{setBusy(false);}}
function fill(content){for(const [id,[section,key]] of Object.entries(bindings))$(id).value=id==='source_rights'&&content?.source?.rights==='unknown'?'':content?.[section]?.[key]??'';$('author_attestation').checked=Boolean(content?.human_authored_attestation);state.dirty=false;}
function readContent(){const content=structuredClone(state.record?.content||defaults());for(const [id,[section,key]] of Object.entries(bindings)){const value=$(id).value;content[section][key]=value.trim()?value:(['author','url','bibliographic_reference','publication','confidence_basis'].includes(key)?null:key==='rights'?'unknown':'');}content.human_authored_attestation=$('author_attestation').checked;return content;}
function renderPermissions(){
  const record=state.record;const can=record?.capabilities||{};const editable=!record||Boolean(can.can_edit);
  $('record-fields').disabled=state.busy||!editable;
  $('save-draft').hidden=!editable;$('save-draft').disabled=state.busy;
  $('submit-review').hidden=!editable;$('submit-review').disabled=state.busy||!record;
  $('review-panel').hidden=!can.can_review;
  $('publication-panel').hidden=!can.can_publish&&!record?.published_snapshot_id;
  $('publish-record').hidden=!can.can_publish;$('publish-record').disabled=state.busy;
  $('correction-panel').hidden=!can.can_correct;
  $('start-correction').disabled=state.busy;
  $('history-panel').hidden=!record;
  $('record-state').textContent=state.dirty?'Есть несохранённые изменения':record?(labels.workflow[record.state]||record.state)+(record.published_snapshot_id?' · опубликовано':''):'Не сохранён';
  $('record-title').textContent=record?.content?.entity?.name||'Новый объект';
  $('record-guidance').textContent=editable?'Пустые поля допустимы в черновике. Для проверки заполните источник, утверждение, locator и исходную формулировку.':'Эта версия доступна для чтения. Решения относятся к точно сохранённому содержимому.';
  $('review-mode').textContent=record?.owner_id===state.user?.id?'Вы проверяете собственную запись. Это будет явно указано в публикации; независимая проверка не заявляется.':'Проверка другим аккаунтом будет записана в истории. Разделение аккаунтов само по себе не доказывает независимость.';
  $('review-digest').textContent=record?.submitted_digest?`Сохранённая версия: ${record.version}. SHA-256: ${record.submitted_digest}`:'';
  $('public-link').hidden=!record?.published_snapshot_id;if(record?.published_snapshot_id)$('public-link').href=`/editor/?object=${encodeURIComponent(record.entity_id)}`;
}
function okayToLeave(){return !state.dirty||window.confirm('В форме есть несохранённый текст. Переключить запись без сохранения?');}
function resetRecord(){state.record=null;fill(defaults());$('review-reason').value='';$('correction-reason').value='';$('history-list').replaceChildren();$('conflict-panel').hidden=true;renderPermissions();$('entity_name').focus();}
function itemTitle(item){return item.content?.entity?.name||item.entity?.name||item.name||'Без названия';}
function renderList(target,items,open){$(target).replaceChildren();for(const item of items){const li=document.createElement('li');const button=document.createElement('button');button.type='button';button.textContent=itemTitle(item);if(state.record?.id===item.id)button.setAttribute('aria-current','true');const small=document.createElement('small');small.textContent=labels.workflow[item.state]||'Опубликованная карточка';button.append(small);button.addEventListener('click',()=>{if(okayToLeave())act(()=>open(item));});li.append(button);$(target).append(li);}}
function items(response){return Array.isArray(response)?response:response?.items||response?.drafts||response?.objects||[];}
function updateLists(){const query=$('record-search').value.trim().toLocaleLowerCase('ru');renderList('draft-list',state.drafts.filter(item=>itemTitle(item).toLocaleLowerCase('ru').includes(query)),item=>loadRecord(item.id));$('draft-empty').hidden=state.drafts.length>0;renderList('review-queue',state.queue,item=>loadRecord(item.id));$('queue-empty').hidden=state.queue.length>0;renderList('published-list',state.published,item=>showPublic({object:item.entity_id}));}
async function lists(){state.drafts=items(await request(`${API}/drafts`));const capabilities=await request(`${API}/capabilities`);$('review-queue-panel').hidden=!capabilities.can_review;state.queue=capabilities.can_review?items(await request(`${API}/review-queue`)):[];state.published=items(await request(`${API}/public/objects`,{authenticated:false}));updateLists();}
function date(value){if(!value)return '';const parsed=new Date(value);return Number.isNaN(parsed.valueOf())?String(value):parsed.toLocaleString('ru-RU');}
async function history(){const response=await request(`${API}/drafts/${encodeURIComponent(state.record.id)}/history`);const entries=response?.events||[];const actions={created:'Черновик создан',saved:'Черновик сохранён',submitted:'Отправлено на проверку',accepted:'Принято редакционно',request_changes:'Запрошены исправления',rejected:'Отклонено',published:'Опубликовано',correction_created:'Создана поправка'};$('history-list').replaceChildren();for(const entry of entries){const li=document.createElement('li');li.textContent=[actions[entry.action]||entry.action,entry.payload?.reason,date(entry.recorded_at),labels.review[entry.payload?.review_mode]||'',entry.payload?.version?`версия ${entry.payload.version}`:''].filter(Boolean).join(' · ');$('history-list').append(li);}}
async function loadRecord(id){state.record=await request(`${API}/drafts/${encodeURIComponent(id)}`);fill(state.record.content);$('conflict-panel').hidden=true;$('review-reason').value='';$('public-card').hidden=true;$('workspace').hidden=false;renderPermissions();updateLists();await history();}
async function save(){const content=readContent();state.record=state.record?await request(`${API}/drafts/${encodeURIComponent(state.record.id)}`,{method:'PUT',body:{expected_version:state.record.version,content}}):await request(`${API}/drafts`,{method:'POST',body:{content}});fill(state.record.content);renderPermissions();await lists();await history();notice('Черновик сохранён на сервере. Можно продолжить позже.');}
function readyToSubmit(){const required=['entity_name','source_title','claim_statement','evidence_locator','source_expression'];const missing=required.filter(id=>!$(id).value.trim());if(!$('source_url').value.trim()&&!$('source_reference').value.trim())missing.push('source_url');if(!$('author_attestation').checked)missing.push('author_attestation');if(!missing.length)return true;const control=$(missing[0]);control.focus();$('error').textContent='Для проверки заполните название объекта и источника, ссылку или библиографию, одно утверждение, точное место и исходную формулировку в источнике; подтвердите авторство. Сейчас выделено первое незаполненное поле.';$('error').hidden=false;return false;}
async function review(decision){const reason=$('review-reason').value.trim();if(!reason){$('review-reason').focus();notice('Укажите основание решения.');return;}state.record=await request(`${API}/drafts/${encodeURIComponent(state.record.id)}/review`,{method:'POST',body:{expected_version:state.record.version,submitted_digest:state.record.submitted_digest,expected_predecessor_revision_id:state.record.predecessor_revision_id??null,decision,reason}});fill(state.record.content);renderPermissions();await lists();await history();notice(decision==='accept'?'Запись принята редакционно. Публикация требует отдельного действия.':'Решение сохранено.');}
async function session(){const previousUser=state.user;state.user=await request('/api/me');if(previousUser&&previousUser.id!==state.user.id)resetRecord();$('account-name').textContent=state.user.email;$('account').hidden=false;$('auth-panel').hidden=true;$('workspace').hidden=false;await lists();renderPermissions();}
$('login-form').addEventListener('submit',event=>{event.preventDefault();act(async()=>{const data=await request('/api/auth/login',{method:'POST',body:{email:$('email').value.trim(),password:$('password').value},authenticated:false});state.token=data.access_token;$('password').value='';await session();notice('Вы вошли в редактор.');});});
$('register-submit').addEventListener('click',()=>{if(!$('login-form').reportValidity())return;act(async()=>{const data=await request('/api/auth/register',{method:'POST',body:{email:$('email').value.trim(),password:$('password').value},authenticated:false});state.token=data.access_token;$('password').value='';await session();notice('Аккаунт создан. Права проверяющего назначаются оператором сервера отдельно.');});});
$('logout').addEventListener('click',()=>{if(!okayToLeave())return;act(async()=>{await request('/api/auth/logout',{method:'POST',authenticated:false});state.token=null;state.user=null;state.record=null;state.drafts=[];state.queue=[];state.published=[];fill(defaults());$('account').hidden=true;$('workspace').hidden=true;$('auth-panel').hidden=false;notice('Вы вышли. Сохранённые записи остаются на сервере.');});});
$('new-draft').addEventListener('click',()=>{if(okayToLeave()){clearError();notice('');resetRecord();}});
$('record-search').addEventListener('input',updateLists);
$('refresh-list').addEventListener('click',()=>act(lists));
$('record-form').addEventListener('input',()=>{state.dirty=true;renderPermissions();});
$('record-form').addEventListener('submit',event=>{event.preventDefault();act(save);});
$('submit-review').addEventListener('click',()=>{if(state.dirty){notice('Сначала сохраните изменения, затем отправьте точную сохранённую версию.');return;}clearError();if(!readyToSubmit())return;act(async()=>{state.record=await request(`${API}/drafts/${encodeURIComponent(state.record.id)}/submit`,{method:'POST',body:{expected_version:state.record.version}});fill(state.record.content);renderPermissions();await lists();await history();notice('Сохранённая версия отправлена на проверку.');});});
for(const [id,decision] of [['review-accept','accept'],['review-request-changes','request_changes'],['review-reject','reject']])$(id).addEventListener('click',()=>act(()=>review(decision)));
$('publish-record').addEventListener('click',()=>act(async()=>{state.record=await request(`${API}/drafts/${encodeURIComponent(state.record.id)}/publish`,{method:'POST',body:{expected_version:state.record.version,accepted_revision_id:state.record.accepted_revision_id,accepted_revision_digest:state.record.accepted_revision_digest,expected_object_version:state.record.object_version,expected_publication_id:state.record.published_snapshot_id??null}});renderPermissions();await lists();await history();notice('Карточка опубликована. Редакционное одобрение не подтверждает историческую истинность.');}));
$('start-correction').addEventListener('click',()=>act(async()=>{const reason=$('correction-reason').value.trim();if(!reason){$('correction-reason').focus();notice('Укажите причину поправки.');return;}const record=await request(`${API}/revisions/${encodeURIComponent(state.record.accepted_revision_id)}/corrections`,{method:'POST',body:{expected_revision_id:state.record.accepted_revision_id,expected_object_version:state.record.object_version,reason}});await lists();await loadRecord(record.id);notice('Создан черновик исправления. Предыдущая публикация сохранена.');}));
$('reload-record').addEventListener('click',()=>{if(okayToLeave())act(()=>loadRecord(state.record.id));});
window.addEventListener('beforeunload',event=>{if(state.dirty){event.preventDefault();event.returnValue='';}});
function element(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function field(dl,label,value){dl.append(element('dt',label),element('dd',value||'Неизвестно'));}
function safeLink(url,text){const link=element('a',text);try{const parsed=new URL(url);if(!['http:','https:'].includes(parsed.protocol))return element('span',text);link.href=parsed.href;link.target='_blank';link.rel='noopener noreferrer';}catch{return element('span',text);}return link;}
async function showPublic({object,snapshot}){
  const response=await request(snapshot?`${API}/public/snapshots/${encodeURIComponent(snapshot)}`:`${API}/public/objects/${encodeURIComponent(object)}`,{authenticated:false});
  const publishedSnapshots=response.published_snapshots||await request(`${API}/public/objects/${encodeURIComponent(response.entity_id)}/history`,{authenticated:false});
  const card=$('public-card');card.replaceChildren();card.hidden=false;$('workspace').hidden=true;$('auth-panel').hidden=true;
  card.append(element('h1',response.entity.name),element('p','Редакционно одобренный кандидат. Историческая достоверность не подтверждена; запись не добавлена в корпус глобуса.','public-scope'));
  card.append(element('blockquote',response.claim.statement,'statement'));
  const epistemic=element('dl');field(epistemic,'Характер утверждения',labels.kind[response.claim.claim_kind]||response.claim.claim_kind);field(epistemic,'Статус проверки утверждения','Черновик');field(epistemic,'Подтверждение доказательствами','Отсутствует');field(epistemic,'Уверенность автора',labels.confidence[response.claim.confidence]||response.claim.confidence);field(epistemic,'Основание уверенности',response.claim.confidence_basis);field(epistemic,'Неопределённость',response.claim.uncertainty);field(epistemic,'Время и местоположение','Неизвестны; нормализация и геометрия отсутствуют');card.append(epistemic);
  card.append(element('h2','Источник'));const source=element('dl');field(source,'Название',response.source.title);field(source,'Автор или организация',response.source.author);field(source,'Тип',labels.source[response.source.source_type]||response.source.source_type);field(source,'Библиография',response.source.bibliographic_reference);field(source,'Права',response.source.rights);field(source,'Точное место в источнике',response.evidence.locator);field(source,'Связь с утверждением',labels.relation[response.evidence.relation_to_claim]);field(source,'Основание',labels.strength[response.evidence.evidence_strength]);field(source,'Статусы источника и доказательной связи','Черновик');card.append(source);if(response.source.url)card.append(safeLink(response.source.url,'Открыть источник'));
  card.append(element('h2','Проверка и версия'));const provenance=element('dl');field(provenance,'Режим редакционной проверки',labels.review[response.review_mode]||response.review_mode);field(provenance,'Опубликовано',date(response.published_at));field(provenance,'Версия',response.revision_id);field(provenance,'SHA-256 принятой версии',response.revision_digest);field(provenance,'SHA-256 исходного значения',response.source_value_digest);field(provenance,'SHA-256 пакета источника',response.source_packet_digest);card.append(provenance);
  card.append(element('p','Проверка другим аккаунтом не гарантирует независимость. Исходный фрагмент источника хранится приватно и не размещается в этой карточке.','muted'));
  const versions=element('ol');for(const version of publishedSnapshots){const li=element('li');const link=element('a',`${date(version.published_at)} · ${version.revision_id}`);link.href=`/editor/?snapshot=${encodeURIComponent(version.snapshot_id)}`;li.append(link);versions.append(li);}card.append(element('h2','История публикаций'),versions);
  const back=element('a','Вернуться в редактор');back.href='/editor/';card.append(back);
}
const params=new URLSearchParams(location.search);
if(params.has('object')||params.has('snapshot')){act(()=>showPublic({object:params.get('object'),snapshot:params.get('snapshot')}));}else{
  fill(defaults());renderPermissions();
  act(async()=>{try{await refresh();await session();}catch(error){if(error.status===401){clearError();return;}throw error;}});
}
