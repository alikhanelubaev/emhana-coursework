(()=>{
  const root=document.getElementById('emhana-ui');
  const icon=n=>`<i data-lucide="${n}" aria-hidden="true"></i>`;
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }
  [c]));
  const patients=[
  [1,'Айдос Нұрланов','2004-03-12','Ер','87001234567','Астана'],[2,'Аружан Серікқызы','2003-07-25','Әйел','87007654321','Астана'],[3,'Данияр Қасымов','2005-11-08','Ер','87005556677','Астана'],[4,'Мадина Ермекова','2004-01-19','Әйел','87008889900','Астана'],[5,'Нұрбек Әлиев','2002-09-30','Ер','87001112233','Астана, Сарыарқа ауданы'],[6,'Әсел Бекова','1985-05-14','Әйел','87009990011','Астана'],[7,'Ерасыл Жақсылықов','2018-02-03','Ер','87004443322','Астана'],[8,'Гүлмира Тоқтарова','1962-12-01','Әйел','87006667788','Астана']].map(a=>Object.fromEntries(['id','full_name','birth_date','gender','phone','address'].map((k,i)=>[k,a[i]])));
  const doctors=[[1,'Ерлан Сейітов','Терапевт','87001112244',101],[2,'Айгүл Мұратова','Кардиолог','87002223355',102],[3,'Данияр Әбілов','Невропатолог','87003334466',103],[4,'Гүлнар Қасымова','Педиатр','87004445577',104],[5,'Марат Омаров','Хирург','87005556688',105],[6,'Лаура Нұрмағамбетова','Офтальмолог','87006667799',106]].map(a=>Object.fromEntries(['id','full_name','specialization','phone','cabinet'].map((k,i)=>[k,a[i]])));
  const appointments=[[1,1,1,'2026-09-10','09:00','Жалпы тексеру'],[2,2,2,'2026-09-10','10:30','Жүрек тексеруі'],[3,3,3,'2026-09-11','11:00','Бас ауруы'],[4,4,4,'2026-09-11','12:00','Тексеру'],[5,5,5,'2026-09-13','15:30','Жоспарлы тексеру'],[6,6,1,'2026-09-14','09:30','Қан қысымын өлшеу'],[7,7,4,'2026-09-14','10:00','Вакцинация'],[8,8,2,'2026-09-15','11:30','Жүрек тұсындағы ауырсыну'],[9,1,1,'2026-09-17','09:00','Қайта қарау'],[10,2,2,'2026-09-18','10:00','Қайта қарау'],[11,6,1,'2026-09-18','15:00','Қайта қарау'],[12,3,3,'2026-09-19','11:30','Бас ауруын қайта тексеру']].map(a=>Object.fromEntries(['id','patient_id','doctor_id','appointment_date','appointment_time','reason'].map((k,i)=>[k,a[i]])));
  const records=[[1,1,'2026-09-10','ЖРВИ','Дене қызуы','Демалу және сұйықтық ішу'],[2,2,'2026-09-10','Гипертония','Қан қысымы','Дәрігер бақылауы'],[3,3,'2026-09-11','Мигрень','Бас ауруы','Тексеруден өту'],[4,4,'2026-09-11','ЖРВИ','Жөтел','Ем қабылдау'],[5,5,'2026-09-12','Дені сау','Шағым жоқ','Жоспарлы бақылау'],[6,6,'2026-09-14','Гипертония','Қан қысымының көтерілуі','Дәрігер бақылауы'],[7,7,'2026-09-14','Дені сау','Шағым жоқ','Жоспарлы бақылау'],[8,8,'2026-09-15','Гипертония','Жүрек тұсындағы ауырсыну','Кардиологқа қайта келу'],[9,1,'2026-09-17','ЖРВИ','Жөтел','Ем қабылдау'],[10,3,'2026-09-19','Мигрень','Бас ауруы','Невропатологтың бақылауы']].map(a=>Object.fromEntries(['id','patient_id','record_date','diagnosis','complaint','recommendation'].map((k,i)=>[k,a[i]])));
  const data={
    patients,doctors,appointments,records
  };
  function saveData(){
    try{
      localStorage.setItem('emhana.records.v1',JSON.stringify({
        version:1,...data
      }));
      return true
    }
    catch(error){
      const el=root.querySelector('#em-notice');
      if(el)el.textContent='Телефонда сақтау орны жеткіліксіз.';
      return false
    }
  }
  try{
    const stored=JSON.parse(localStorage.getItem('emhana.records.v1'));
    if(stored&&stored.version===1&&Object.keys(data).every(k=>Array.isArray(stored[k])&&stored[k].every(r=>r&&Number.isInteger(r.id)&&r.id>0))){
      const pids=new Set(stored.patients.map(r=>r.id)),dids=new Set(stored.doctors.map(r=>r.id));
      if(stored.appointments.every(r=>pids.has(r.patient_id)&&dids.has(r.doctor_id))&&stored.records.every(r=>pids.has(r.patient_id))){
        for(const key of Object.keys(data))data[key].splice(0,data[key].length,...stored[key]);
      }
    }
  }
  catch(error){
  }
  const defs={
    patients:{
      title:'Пациенттер',sub:'Емханаға тіркелген пациенттердің картотекасы',add:'Пациент қосу',fields:[['full_name','Аты-жөні'],['birth_date','Туған күні','date'],['gender','Жынысы','gender'],['phone','Телефон','tel'],['address','Мекенжайы']]
    },doctors:{
      title:'Дәрігерлер',sub:'Мамандар, байланыс деректері және кабинеттер',add:'Дәрігер қосу',fields:[['full_name','Аты-жөні'],['specialization','Мамандығы'],['phone','Телефон','tel'],['cabinet','Кабинет','number']]
    },appointments:{
      title:'Қабылдаулар',sub:'Пациенттерді дәрігердің қабылдауына тіркеу',add:'Қабылдауға жазу',fields:[['patient_id','Пациент','patient'],['doctor_id','Дәрігер','doctor'],['appointment_date','Қабылдау күні','date'],['appointment_time','Уақыты','time'],['reason','Келу себебі']]
    },records:{
      title:'Медициналық жазбалар',sub:'Пациенттердің шағымдары, диагноздары және ұсыныстар',add:'Жазба қосу',fields:[['patient_id','Пациент','patient'],['record_date','Жазба күні','date'],['diagnosis','Диагноз'],['complaint','Шағымы'],['recommendation','Ұсынысы','textarea']]
    }
  };
  const nav=[['home','layout-dashboard','Басты бет'],['patients','users','Пациенттер'],['doctors','stethoscope','Дәрігерлер'],['appointments','calendar-days','Қабылдаулар'],['records','clipboard-list','Медициналық жазбалар'],['card','contact-round','Пациент картасы'],['reports','chart-no-axes-combined','Есептер']];
  let saved={
  };
  let state={
    screen:saved.screen==='app'?'app':'login',page:nav.some(x=>x[0]===saved.page)?saved.page:'home',selected:patients.some(p=>p.id===saved.selected)?saved.selected:1,query:'',filter:'',sort:'default',report:'workload'
  };
  const design={
    layout:'side',radius:16
  };
  const persist=()=>{
  };
  const pname=id=>patients.find(p=>p.id===Number(id))?.full_name||'—',dname=id=>doctors.find(p=>p.id===Number(id))?.full_name||'—';
  const date=v=>v?String(v).split('-').reverse().join('.'):'—';
  const initials=s=>s.split(' ').map(x=>x[0]).slice(0,2).join('');
  const person=p=>`<div class="em-person"><span class="em-avatar">${esc(initials(p.full_name))}</span><span class="em-name">${esc(p.full_name)}</span></div>`;
  const brand=()=>'<div class="em-brand"><span class="em-logo">+</span>emhana<span class="em-small em-muted">/</span></div>';
  const table=(heads,rows)=>`<div class="em-table-wrap"><table><thead><tr>${heads.map(h=>`<th scope="col">${h}</th>`).join('')}</tr></thead><tbody>${rows.length?rows.map(r=>'<tr>'+r.map((c,i)=>`<td data-label="${esc(heads[i])}">${c}</td>`).join('')+'</tr>').join(''):`<tr><td colspan="${heads.length}">Жазбалар табылмады</td></tr>`}</tbody></table></div>`;
  function icons(){
    if(globalThis.lucide)lucide.createIcons({
      root,attrs:{
        width:18,height:18
      }
    })
  }
  function login(){
    root.innerHTML=`<div class="em-login"><section class="em-story">${brand()}<div><span class="em-pill">Қалалық емхана картотекасы</span><h1>Әр пациенттің<br>тарихы —<br>бір жүйеде.</h1><p>Пациенттер, қабылдаулар және медициналық жазбалармен жұмыс істеуге арналған орта.</p><div class="em-story-card"><div class="em-rowtitle"><h3>Пациент картасы</h3><span class="em-pill">№ 001</span></div>${person(patients[0])}<div class="em-story-row">${icon('calendar-check')}<div><div>Соңғы қабылдау</div><span class="em-small em-muted">17.09.2026 · Ерлан Сейітов</span></div></div><div class="em-story-row">${icon('folder-heart')}<div>2 қабылдау · 2 медициналық жазба</div></div></div></div><p class="em-small">Emhana · пациенттер картотекасы</p></section><section class="em-login-right"><span class="em-pill" style="align-self:flex-start;margin-bottom:22px">Қызметкер кабинеті</span><h1>Жүйеге кіру</h1><p class="em-muted" style="margin-top:10px">Картотекамен жұмысты бастау үшін кіріңіз.</p><form id="em-login-form"><label>Логин<input name="login" autocomplete="off" placeholder="Логинді енгізіңіз" required></label><label>Құпиясөз<span class="em-password"><input name="password" type="password" autocomplete="off" placeholder="Құпиясөзді енгізіңіз" required><button type="button" data-action="password" aria-label="Құпиясөзді көрсету">${icon('eye')}</button></span></label><p id="em-login-error" class="em-error" role="alert"></p><button class="em-primary" type="submit">Жүйеге кіру ${icon('arrow-right')}</button></form><div class="em-demo"><span>Үлгілік логин: <strong>admin</strong><br>Құпиясөз: <strong>Clinic2026</strong></span><button type="button" data-action="fill">Толтыру</button></div><p class="em-small em-muted" style="margin-top:20px">Интерфейстің үлгісі · құжаттағы тестілік деректер</p></section></div>`;
    icons();
  }
  function shell(){
    root.innerHTML=`<div class="em-shell"><aside class="em-sidebar">${brand()}<nav class="em-nav" aria-label="Негізгі бөлімдер">${nav.map(([id,i,t])=>`<button data-page="${id}" aria-current="${id===state.page?'page':'false'}">${icon(i)}${t}</button>`).join('')}</nav><div class="em-sidefoot"><span class="em-pill">Оқу үлгісі</span><p class="em-small em-muted">Курстық жұмыстың<br>тестілік деректері</p><button data-action="logout">${icon('log-out')} Шығу</button></div></aside><div class="em-main"><header class="em-topbar"><div><span class="em-small em-muted">Қалалық емхана</span><div>Пациенттер картотекасы</div></div><div class="em-account"><span class="em-avatar">А</span><span class="em-accountname">Әкімші<br><span class="em-small em-muted">admin · үлгі</span></span><button data-action="logout" aria-label="Кіру бетіне оралу">${icon('log-out')}</button></div></header><main class="em-workspace" id="em-content"></main></div></div><div id="em-modal"></div>`;
    content();
  }
  function heading(title,sub,action=''){
    return `<div class="em-heading"><div><h1>${title}</h1><p>${sub}</p></div>${action}</div>`
  }
  function home(){
    const recent=[...appointments].sort((a,b)=>(b.appointment_date+b.appointment_time).localeCompare(a.appointment_date+a.appointment_time)).slice(0,4);
    return heading('Картотекаға шолу','Құжаттағы үлгілік деректердің жалпы көрінісі',`<button class="em-primary" data-new="appointments">${icon('plus')} Қабылдауға жазу</button>`)+`<div class="em-stats">${[['Пациент',patients.length],['Дәрігер',doctors.length],['Қабылдау',appointments.length],['Мед. жазба',records.length]].map(([t,n])=>`<div class="em-stat"><span>${t}</span><strong>${n}</strong><span>Картотекада тіркелген</span></div>`).join('')}</div><div class="em-two"><section class="em-panel"><div class="em-rowtitle"><h3>Соңғы қабылдаулар</h3><button data-page="appointments" class="em-small">Барлығы ${icon('arrow-up-right')}</button></div>${recent.map(a=>`<div class="em-listrow"><div class="em-time">${a.appointment_time}<small>${date(a.appointment_date)}</small></div><div class="em-grow"><div class="em-name">${esc(pname(a.patient_id))}</div><div class="em-small em-muted">${esc(dname(a.doctor_id))}</div></div><button data-card="${a.patient_id}" aria-label="${esc(pname(a.patient_id))} картасын ашу">${icon('arrow-up-right')}</button></div>`).join('')}</section><section class="em-panel"><h3>Жылдам әрекеттер</h3><div class="em-quick"><button data-new="patients"><span>${icon('user-plus')} Пациентті тіркеу</span>${icon('arrow-right')}</button><button data-new="records"><span>${icon('file-plus-2')} Медициналық жазба</span>${icon('arrow-right')}</button><button data-page="card"><span>${icon('contact-round')} Пациент картасын ашу</span>${icon('arrow-right')}</button></div></section></div><section class="em-panel"><div class="em-rowtitle"><h3>Пациенттер</h3><button data-page="patients">Картотеканы ашу ${icon('arrow-right')}</button></div>${table(['№','Аты-жөні','Туған күні','Телефон','Картасы'],patients.slice(0,3).map(p=>[String(p.id).padStart(3,'0'),person(p),date(p.birth_date),esc(p.phone),`<button data-card="${p.id}">Ашу ${icon('arrow-up-right')}</button>`]))}</section>`
  }
  function controls(key){
    const opts=key==='patients'?['Ер','Әйел']:key==='doctors'?[...new Set(doctors.map(d=>d.specialization))]:key==='appointments'?doctors.map(d=>d.full_name):[...new Set(records.map(d=>d.diagnosis))];
    const label=key==='patients'?'Барлық пациенттер':key==='doctors'?'Барлық мамандықтар':key==='appointments'?'Барлық дәрігерлер':'Барлық диагноздар';
    return `<div class="em-toolbar"><div class="em-search">${icon('search')}<input id="em-search" aria-label="Іздеу" placeholder="${key==='patients'?'Аты-жөні немесе телефон...':'Жазбаларды іздеу...'}" value="${esc(state.query)}"></div><select id="em-filter" aria-label="Сүзгі"><option value="">${label}</option>${opts.map(x=>`<option ${state.filter===x?'selected':''}>${esc(x)}</option>`).join('')}</select><select id="em-sort" aria-label="Сұрыптау">${[['default','№ бойынша'],['asc','Өсу ретімен'],['desc','Кему ретімен']].map(([v,t])=>`<option value="${v}" ${state.sort===v?'selected':''}>${t}</option>`).join('')}</select></div>`
  }
  function rowsFor(key){
    let rows=data[key].filter(r=>{
      const vals=[...Object.values(r),r.patient_id?pname(r.patient_id):'',r.doctor_id?dname(r.doctor_id):''].join(' ').toLocaleLowerCase('kk');
      return vals.includes(state.query.toLocaleLowerCase('kk'))&&(!state.filter||(key==='patients'?r.gender:key==='doctors'?r.specialization:key==='appointments'?dname(r.doctor_id):r.diagnosis)===state.filter)
    });
    if(state.sort!=='default'){
      const field=key==='patients'||key==='doctors'?'full_name':key==='appointments'?'appointment_date':'record_date';
      rows.sort((a,b)=>String(a[field]).localeCompare(String(b[field]),'kk')*(state.sort==='desc'?-1:1))
    }
    return rows
  }
  function tableContent(key){
    const rows=rowsFor(key),action=r=>`<div class="em-actions"><button data-edit="${key}:${r.id}" aria-label="№ ${r.id} жазбаны өзгерту">${icon('pencil')}</button><button data-delete="${key}:${r.id}" aria-label="№ ${r.id} жазбаны жою">${icon('trash-2')}</button></div>`;
    let heads,values;
    if(key==='patients'){
      heads=['№','Аты-жөні','Туған күні','Жынысы','Телефон','Мекенжайы','Әрекет'];
      values=rows.map(p=>[p.id,`<button data-card="${p.id}" style="border:0;padding:0;background:transparent;text-align:left">${person(p)}</button>`,date(p.birth_date),esc(p.gender),esc(p.phone),esc(p.address),action(p)])
    }
    if(key==='doctors'){
      heads=['№','Аты-жөні','Мамандығы','Телефон','Кабинет','Әрекет'];
      values=rows.map(d=>[d.id,person(d),`<span class="em-pill">${esc(d.specialization)}</span>`,esc(d.phone),esc(d.cabinet),action(d)])
    }
    if(key==='appointments'){
      heads=['№','Пациент','Дәрігер','Күні','Уақыты','Келу себебі','Әрекет'];
      values=rows.map(a=>[a.id,`<button data-card="${a.patient_id}">${esc(pname(a.patient_id))}</button>`,esc(dname(a.doctor_id)),date(a.appointment_date),`<span class="em-time">${esc(a.appointment_time)}</span>`,esc(a.reason),action(a)])
    }
    if(key==='records'){
      heads=['№','Пациент','Күні','Диагноз','Шағымы','Ұсынысы','Әрекет'];
      values=rows.map(r=>[r.id,`<button data-card="${r.patient_id}">${esc(pname(r.patient_id))}</button>`,date(r.record_date),`<span class="em-pill">${esc(r.diagnosis)}</span>`,esc(r.complaint),esc(r.recommendation),action(r)])
    }
    return table(heads,values)+`<div class="em-foot"><span>${rows.length} / ${data[key].length} жазба</span><span>Барлық өрістер көрсетілген</span></div>`
  }
  function listing(key){
    const d=defs[key];
    return heading(d.title,d.sub,`<button class="em-primary" data-new="${key}">${icon('plus')} ${d.add}</button>`)+`<section class="em-panel">${controls(key)}<div id="em-table">${tableContent(key)}</div><div id="em-notice" class="em-notice" role="status"></div></section>`
  }
  function card(){
    const p=patients.find(x=>x.id===state.selected)||patients[0];
    if(!p)return heading('Пациент картасы','Алдымен пациентті тіркеңіз');
    state.selected=p.id;
    const apps=appointments.filter(x=>x.patient_id===p.id).sort((a,b)=>a.appointment_date.localeCompare(b.appointment_date)), recs=records.filter(x=>x.patient_id===p.id).sort((a,b)=>a.record_date.localeCompare(b.record_date));
    return heading('Пациенттің толық картасы','Жеке мәліметтер, қабылдау тарихы және медициналық жазбалар')+`<label>Пациентті таңдаңыз<select id="em-patient-select">${patients.map(x=>`<option value="${x.id}" ${x.id===p.id?'selected':''}>№ ${String(x.id).padStart(3,'0')} · ${esc(x.full_name)}</option>`).join('')}</select></label><section class="em-panel"><div class="em-rowtitle">${person(p)}<button data-edit="patients:${p.id}">${icon('pencil')} Өзгерту</button></div><div class="em-details">${[['Карта нөмірі','№ '+String(p.id).padStart(3,'0')],['Туған күні',date(p.birth_date)],['Жынысы',p.gender],['Телефон',p.phone],['Мекенжайы',p.address],['Тарихы',`${apps.length} қабылдау · ${recs.length} жазба`]].map(([k,v])=>`<div class="em-detail"><span>${k}</span>${esc(v)}</div>`).join('')}</div></section><div class="em-two"><section class="em-panel"><div class="em-rowtitle"><h3>Қабылдау тарихы</h3><button data-new="appointments">${icon('plus')} Жазу</button></div>${apps.length?apps.map(a=>`<div class="em-entry"><span class="em-pill">${date(a.appointment_date)} · ${esc(a.appointment_time)}</span><h3 style="margin-top:10px">${esc(dname(a.doctor_id))}</h3><p>Себебі: ${esc(a.reason)}</p></div>`).join(''):'Қабылдаулар тіркелмеген'}</section><section class="em-panel"><div class="em-rowtitle"><h3>Медициналық жазбалар</h3><button data-new="records">${icon('plus')} Қосу</button></div>${recs.length?recs.map(r=>`<div class="em-entry"><div class="em-rowtitle"><span class="em-pill">${esc(r.diagnosis)}</span><span class="em-small em-muted">${date(r.record_date)}</span></div><p>Шағымы: ${esc(r.complaint)}</p><p>Ұсынысы: ${esc(r.recommendation)}</p></div>`).join(''):'Медициналық жазбалар тіркелмеген'}</section></div>`
  }
  function reportContent(){
    if(state.report==='workload'){
      const w=doctors.map(d=>({
        ...d,count:appointments.filter(a=>a.doctor_id===d.id).length
      })).sort((a,b)=>b.count-a.count);
      return `<h3>Дәрігерлердің қабылдау саны</h3>${w.map(d=>`<div class="em-bar-row"><span>${esc(d.full_name)}<br><span class="em-muted">${esc(d.specialization)}</span></span><div class="em-bar"><span style="width:${d.count/Math.max(1,...w.map(x=>x.count))*100}%"></span></div><strong>${d.count}</strong></div>`).join('')}`
    }
    if(state.report==='diagnoses'){
      const counts={
      }; records.forEach(r=>counts[r.diagnosis]=(counts[r.diagnosis]||0)+1);
      return table(['Диагноз','Жазба саны'],Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([k,v])=>[esc(k),v]))
    }
    if(state.report==='gender')return table(['Жынысы','Пациент саны'],['Ер','Әйел'].map(g=>[g,patients.filter(p=>p.gender===g).length]));
    const rows=patients.map(p=>({
      ...p,count:appointments.filter(a=>a.patient_id===p.id).length
    })).filter(p=>p.count>1).sort((a,b)=>b.count-a.count);
    return table(['Пациент','Қабылдау саны','Картасы'],rows.map(p=>[person(p),p.count,`<button data-card="${p.id}">Ашу ${icon('arrow-up-right')}</button>`]))
  }
  function reports(){
    return heading('Есептер','Қабылдаулар мен медициналық жазбалар бойынша жиынтық ақпарат')+`<div class="em-tabs" aria-label="Есеп түрі">${[['workload','Дәрігер жүктемесі'],['diagnoses','Диагноздар'],['gender','Жынысы бойынша'],['frequent','Қайта келгендер']].map(([id,t])=>`<button data-report="${id}" aria-pressed="${id===state.report}">${t}</button>`).join('')}</div><section class="em-panel" aria-live="polite">${reportContent()}</section>`
  }
  function content(){
    const el=root.querySelector('#em-content');
    el.innerHTML=state.page==='home'?home():defs[state.page]?listing(state.page):state.page==='card'?card():reports();
    root.querySelectorAll('[data-page]').forEach(b=>b.setAttribute('aria-current',b.dataset.page===state.page?'page':'false'));
    icons();
  }
  function render(){
    root.dataset.layout=design.layout;
    root.style.setProperty('--em-radius',design.radius+'px');
    state.screen==='login'?login():shell()
  }
  function formField([k,label,type],r){
    let input;
    if(type==='patient'||type==='doctor'){
      const list=type==='patient'?patients:doctors;
      input=`<select name="${k}" required><option value="">Таңдаңыз</option>${list.map(x=>`<option value="${x.id}" ${Number(r[k])===x.id?'selected':''}>${esc(x.full_name)}${type==='doctor'?' · '+esc(x.specialization):''}</option>`).join('')}</select>`
    }
    else if(type==='gender'){
      input=`<select name="${k}" required>${['Ер','Әйел'].map(x=>`<option ${r[k]===x?'selected':''}>${x}</option>`).join('')}</select>`
    }
    else if(type==='textarea')input=`<textarea name="${k}" rows="3" required>${esc(r[k]||'')}</textarea>`;
    else input=`<input name="${k}" type="${type||'text'}" value="${esc(r[k]||'')}" ${type==='number'?'min="1" step="1"':''} ${type==='tel'?'pattern="[0-9+ ()-]{7,20}"':''} required>`;
    return `<label class="${['full_name','address','reason','complaint','recommendation'].includes(k)?'em-full':''}">${label}${input}</label>`
  }
  function modal(key,id){
    const row=id?data[key].find(x=>x.id===Number(id)):{
      patient_id:state.page==='card'?state.selected:'',gender:'Ер'
    }; const d=defs[key];
    root.querySelector('#em-modal').innerHTML=`<div class="em-overlay"><section class="em-dialog" role="dialog" aria-modal="true" aria-labelledby="em-dialog-title"><div class="em-rowtitle"><h2 id="em-dialog-title">${id?'Жазбаны өзгерту':d.add}</h2><button data-action="close" aria-label="Жабу">${icon('x')}</button></div><form id="em-record-form" data-key="${key}" data-id="${id||''}"><div class="em-form-grid">${d.fields.map(f=>formField(f,row)).join('')}</div><p class="em-error" id="em-form-error" role="alert"></p><div class="em-dialog-footer"><button type="button" data-action="close">Болдырмау</button><button class="em-primary" type="submit">${icon('check')} Сақтау</button></div></form></section></div>`;
    icons();
    root.querySelector('#em-record-form input, #em-record-form select')?.focus()
  }
  function close(){
    root.querySelector('#em-modal').innerHTML=''
  }
  root.addEventListener('click',e=>{
    const b=e.target.closest('button'); if(!b)return;
    if(b.type==='submit'&&b.closest('form')){
      e.preventDefault(); const form=b.closest('form');
      if(form.reportValidity())submitForm(form);
      return
    }
    if(b.dataset.page){
      state.page=b.dataset.page; state.query=''; state.filter='';
      state.sort='default'; content();
      persist()
    }
    if(b.dataset.card){
      state.selected=Number(b.dataset.card); state.page='card'; content();
      persist()
    }
    if(b.dataset.new)modal(b.dataset.new);
    if(b.dataset.edit){
      const [key,id]=b.dataset.edit.split(':');
      modal(key,id)
    }
    if(b.dataset.delete){
      const [key,id]=b.dataset.delete.split(':'); const n=Number(id);
      if((key==='patients'&&(appointments.some(a=>a.patient_id===n)||records.some(r=>r.patient_id===n)))||(key==='doctors'&&appointments.some(a=>a.doctor_id===n))){
        root.querySelector('#em-notice').textContent='Байланысты жазбалар бар. Бұл жазбаны жою мүмкін емес.';
        return
      }
      root.querySelector('#em-modal').innerHTML=`<div class="em-overlay"><section class="em-dialog" role="dialog" aria-modal="true" aria-label="Жазбаны жою"><h2>№ ${n} жазбаны жою керек пе?</h2><p class="em-muted" style="margin-top:10px">Өзгеріс тек осы интерфейс үлгісіне қолданылады.</p><div class="em-dialog-footer"><button data-action="close">Болдырмау</button><button class="em-primary" data-confirm="${key}:${n}">Жою</button></div></section></div>`
    }
    if(b.dataset.confirm){
      const [key,id]=b.dataset.confirm.split(':');
      data[key].splice(data[key].findIndex(r=>r.id===Number(id)),1); saveData();
      close(); content();
      root.querySelector('#em-notice').textContent='Жазба жойылды.'
    }
    if(b.dataset.report){
      state.report=b.dataset.report;
      content()
    }
    if(b.dataset.action==='logout'){
      state.screen='login'; render();
      persist()
    }
    if(b.dataset.action==='fill'){
      root.querySelector('[name=login]').value='admin';
      root.querySelector('[name=password]').value='Clinic2026'
    }
    if(b.dataset.action==='password'){
      const el=root.querySelector('[name=password]');
      el.type=el.type==='password'?'text':'password';
      b.setAttribute('aria-label',el.type==='text'?'Құпиясөзді жасыру':'Құпиясөзді көрсету')
    }
    if(b.dataset.action==='close')close()
  });
  function submitForm(form){
    if(form.id==='em-login-form'){
      const fd=new FormData(form);
      if(fd.get('login')==='admin'&&fd.get('password')==='Clinic2026'){
        state.screen='app'; render();
        persist()
      }
      else root.querySelector('#em-login-error').textContent='Логин немесе құпиясөз қате. Үлгілік деректерді қолданыңыз.'
    }
    if(form.id==='em-record-form'){
      const key=form.dataset.key; const fd=new FormData(form);
      const row={
      };
      for(const [k,v]of fd.entries())row[k]=['patient_id','doctor_id','cabinet'].includes(k)?Number(v):String(v).trim();
      const id=Number(form.dataset.id);
      const error=root.querySelector('#em-form-error');
      if(Object.values(row).some(v=>v==='')){
        error.textContent='Барлық өрістерді толтырыңыз.';
        return
      }
      if(row.phone&&data[key].some(r=>r.phone===row.phone&&r.id!==id)){
        error.textContent='Бұл телефон нөмірі бұрын тіркелген.';
        return
      }
      if(key==='appointments'&&appointments.some(a=>a.id!==id&&a.doctor_id===row.doctor_id&&a.appointment_date===row.appointment_date&&a.appointment_time===row.appointment_time)){
        error.textContent='Бұл дәрігердің таңдалған уақыты бос емес.';
        return
      }
      if(id)Object.assign(data[key].find(r=>r.id===id),row);
      else data[key].push({
        ...row,id:Math.max(0,...data[key].map(r=>r.id))+1
      }); saveData(); close(); content();
      const notice=root.querySelector('#em-notice');
      if(notice)notice.textContent='Жазба сақталды.'
    }
  }
  root.addEventListener('submit',e=>{
    e.preventDefault();
    submitForm(e.target)
  });
  root.addEventListener('input',e=>{
    if(e.target.id==='em-search'){
      state.query=e.target.value;
      root.querySelector('#em-table').innerHTML=tableContent(state.page);
      icons()
    }
  });
  root.addEventListener('change',e=>{
    if(e.target.id==='em-filter'||e.target.id==='em-sort'){
      state[e.target.id==='em-filter'?'filter':'sort']=e.target.value;
      root.querySelector('#em-table').innerHTML=tableContent(state.page);
      icons()
    }
    if(e.target.id==='em-patient-select'){
      state.selected=Number(e.target.value); content();
      persist()
    }
  });
  root.addEventListener('keydown',e=>{
    if(e.key==='Enter'&&e.target.tagName==='INPUT'&&e.target.closest('form')){
      e.preventDefault(); const form=e.target.closest('form');
      if(form.reportValidity())submitForm(form);
      return
    }
    if(e.key==='Escape'&&root.querySelector('.em-overlay'))close();
    if(e.key==='Tab'){
      const dialog=root.querySelector('.em-dialog'); if(!dialog)return;
      const items=[...dialog.querySelectorAll('button,input,select,textarea')];
      if(e.shiftKey&&document.activeElement===items[0]){
        e.preventDefault();
        items.at(-1).focus()
      }
      if(!e.shiftKey&&document.activeElement===items.at(-1)){
        e.preventDefault();
        items[0].focus()
      }
    }
  });
  window.emhanaGoBack=()=>{
    if(root.querySelector('.em-overlay')){
      close();
      return true
    }
    if(state.screen==='app'&&state.page!=='home'){
      state.page='home'; content(); window.scrollTo(0,0);
      return true
    }
    return false;
  }; render();
})();
