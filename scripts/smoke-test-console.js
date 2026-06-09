/* === ConciliaIA · smoke test de API (cole no console, na página do app logado) ===
   Utilitário MANUAL de QA — não é importado pelo app nem pelo build/CI.
   - Reaproveita o token do app (localStorage); se não houver, faz login com o CONFIG.
   - Testa só leituras por padrão. Ponha RUN_WRITES:true p/ também rodar a reconciliação.
   - A linha de notificações usa /api/v1/notifications (SEM barra final): é o caminho
     canônico após o fix do trailing-slash. Se ela vier 404, é sinal de que esse fix
     ainda não foi deployado nesse ambiente. */
(async () => {
  const CONFIG = {
    BASE: location.origin,                 // troque se a API estiver em outro host
    EMAIL: 'test@example.com',             // usado só se não houver sessão ativa
    PASSWORD: 'SecurePassword123!',
    RUN_WRITES: false,                     // true = também executa POST /reconciliation/execute
    DATE_FROM: new Date(Date.now() - 90*864e5).toISOString().slice(0,10),
    DATE_TO:   new Date().toISOString().slice(0,10),
  };
  const TAG=['%c[ConciliaIA]','color:#6c5ce7;font-weight:bold'], log=(...a)=>console.log(...TAG,...a);
  const qs=o=>o&&Object.keys(o).length?'?'+new URLSearchParams(o):'';
  const pickArray=d=>Array.isArray(d)?d:Object.values(d||{}).find(v=>Array.isArray(v))||[];
  const sample=d=>{try{const s=typeof d==='string'?d:JSON.stringify(d);return s.length>90?s.slice(0,90)+'…':s;}catch{return'';}};

  let token,refresh;
  try{const s=JSON.parse(localStorage.getItem('auth-storage')||'{}');token=s?.state?.accessToken;refresh=s?.state?.refreshToken;}catch{}

  async function api(method,path,{params,body,bearer=true,binary=false}={}){
    const t0=performance.now(),headers={};
    if(body)headers['Content-Type']='application/json';
    if(bearer&&token)headers['Authorization']='Bearer '+token;
    let res,data,err;
    try{
      res=await fetch(CONFIG.BASE+path+qs(params),{method,headers,body:body?JSON.stringify(body):undefined});
      if(binary&&res.ok)data=`[${res.headers.get('content-type')||''} ${res.headers.get('content-length')||'?'}b]`;
      else{const t=await res.text();try{data=JSON.parse(t);}catch{data=t;}}
    }catch(e){err=e;}
    return{status:res?.status??0,ok:res?.ok??false,ms:Math.round(performance.now()-t0),data,err};
  }

  if(token)log('Token do app encontrado — usando a sessão atual.');
  else{
    log('Sem sessão — login:',CONFIG.EMAIL);
    const r=await api('POST','/api/v1/auth/login',{body:{email:CONFIG.EMAIL,password:CONFIG.PASSWORD},bearer:false});
    if(!r.ok){console.error('❌ Login falhou',r.status,r.data);return;}
    token=r.data.access_token;refresh=r.data.refresh_token;log('✅ Login OK.');
  }
  try{const p=JSON.parse(atob(token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));log('Autenticado como →',{email:p.email,roles:p.roles,tenant_id:p.tenant_id});}catch{}

  const D={start_date:CONFIG.DATE_FROM,end_date:CONFIG.DATE_TO};
  const checks=[
    ['Infra','Health','GET','/api/v1/health',{bearer:false}],
    ['Auth','Perfil (/me)','GET','/api/v1/auth/me'],
    ['Cadastro','Adquirentes','GET','/api/v1/acquirers'],
    ['Regras','Regras de reconciliação','GET','/api/v1/reconciliation-rules'],
    ['Dados','Vendas','GET','/api/v1/sales',{params:{page:1,page_size:5}}],
    ['Dados','Transações','GET','/api/v1/transactions',{params:{page:1,page_size:5}}],
    ['Dados','Divergências','GET','/api/v1/divergences',{params:{page:1,page_size:5}}],
    ['Dados','Matches','GET','/api/v1/matches',{params:{limit:10}}],
    ['Jobs','Jobs de reconciliação','GET','/api/v1/reconciliation-jobs',{params:{limit:20}}],
    ['Jobs','Métricas de processo','GET','/api/v1/reconciliation-jobs/metrics'],
    ['Dashboard','Stats / dashboard','GET','/api/v1/stats/dashboard'],
    ['Dashboard','KPIs','GET','/api/v1/stats/kpis'],
    ['Fluxo','Cash flow / forecast','GET','/api/v1/cash-flow/forecast'],
    ['Alertas','Alertas proativos','GET','/api/v1/alerts/proactive'],
    ['Notif','Notificações','GET','/api/v1/notifications',{params:{unread_only:true}}],
    ['Notif','Não lidas (count)','GET','/api/v1/notifications/unread-count'],
    ['Import','Agendamentos auto-import','GET','/api/v1/auto-import/schedule'],
    ['Export','Vendas → CSV','GET','/api/v1/sales/export/csv',{binary:true}],
    ['Export','Transações → CSV','GET','/api/v1/transactions/export/csv',{binary:true}],
    // ↓ exigem papel analyst/admin/manager (testam o RBAC)
    ['Relatórios','Accuracy','GET','/api/v1/reports/accuracy',{params:D}],
    ['Relatórios','Divergence analysis','GET','/api/v1/reports/divergence-analysis',{params:D}],
    ['Relatórios','Acquirer performance','GET','/api/v1/reports/acquirer-performance',{params:D}],
    ['Relatórios','Settlement analysis','GET','/api/v1/reports/settlement-analysis',{params:D}],
    ['Relatórios','MDR variance','GET','/api/v1/reports/mdr-variance',{params:D}],
    ['Relatórios','Cashflow overview','GET','/api/v1/reports/cashflow-overview',{params:D}],
    ['Export','Vendas → Excel','GET','/api/v1/export/sales/excel',{binary:true}],
    ['Export','Accuracy → Excel','GET','/api/v1/export/reports/accuracy/excel',{params:D,binary:true}],
    ['Export','Divergências → Excel','GET','/api/v1/export/reports/divergences/excel',{params:D,binary:true}],
  ];
  const verdict=r=>r.err?'🚫 rede/CORS':r.ok?'✅ OK':({401:'🔒 401 sem auth',403:'⛔ 403 papel/tenant',404:'❓ 404',405:'🚫 405',422:'⚠️ 422 validação',429:'⏳ 429 rate-limit',500:'💥 500 erro',502:'💥 502',503:'🔌 503 desativado'}[r.status]||('❌ '+r.status));

  const rows=[],ids={};
  for(const [g,n,m,path,opts] of checks){
    const r=await api(m,path,opts);
    rows.push({Grupo:g,Endpoint:n,M:m,HTTP:r.status,Resultado:verdict(r),ms:r.ms,Amostra:sample(r.data)});
    if(r.ok&&path==='/api/v1/sales')ids.sale=pickArray(r.data)[0]?.id;
    if(r.ok&&path==='/api/v1/divergences')ids.div=pickArray(r.data)[0]?.id;
    if(r.ok&&path==='/api/v1/reconciliation-jobs')ids.job=pickArray(r.data)[0]?.id;
  }
  for(const [c,g,n,path] of [[ids.sale,'Dados','Venda por id',`/api/v1/sales/${ids.sale}`],[ids.div,'Dados','Divergência por id',`/api/v1/divergences/${ids.div}`],[ids.job,'Jobs','Status de job',`/api/v1/reconciliation-jobs/${ids.job}/status`]]){
    if(!c)continue;const r=await api('GET',path);rows.push({Grupo:g,Endpoint:n,M:'GET',HTTP:r.status,Resultado:verdict(r),ms:r.ms,Amostra:sample(r.data)});
  }
  if(refresh){const r=await api('POST','/api/v1/auth/refresh',{body:{refresh_token:refresh},bearer:false});rows.push({Grupo:'Auth',Endpoint:'Refresh token',M:'POST',HTTP:r.status,Resultado:verdict(r),ms:r.ms,Amostra:sample(r.data)});}
  if(CONFIG.RUN_WRITES){const r=await api('POST','/api/v1/reconciliation/execute',{body:D});rows.push({Grupo:'Reconciliação',Endpoint:'Executar (WRITE)',M:'POST',HTTP:r.status,Resultado:verdict(r),ms:r.ms,Amostra:sample(r.data)});}
  {const r=await api('POST','/api/v1/auth/logout');rows.push({Grupo:'Auth',Endpoint:'Logout',M:'POST',HTTP:r.status,Resultado:verdict(r),ms:r.ms,Amostra:sample(r.data)});}

  console.table(rows);
  const ok=rows.filter(r=>r.Resultado==='✅ OK').length,f403=rows.filter(r=>r.HTTP===403).length,srv=rows.filter(r=>r.HTTP>=500||r.HTTP===0).length;
  log(`Resumo: ${ok}/${rows.length} OK · ${f403}×403 (papel/tenant) · ${srv} erro de servidor/rede`);
  log('⛔403 em Relatórios/Export ⇒ usuário sem papel analyst/admin/manager · 🔌503 ⇒ recurso (ex.: Cielo) não configurado · 🚫rede/CORS ⇒ rode na MESMA origem do app');
  window.__conciliaTest=rows; // resultados ficam em window.__conciliaTest
})();
