/* Car Ledger: snapshot UI. Source updates never replace the visible session list. */
class CarLedgerCard extends HTMLElement {
  constructor() {
    super(); this.attachShadow({mode:'open'}); this.tab='charging'; this.period='month'; this.full=false;
    this.pageSize=36; this.graphUnit='kwh'; this.snapshot=null; this.loading=false; this.error='';
    this._visibility=()=>{if(!document.hidden&&this.isConnected)this.refresh();};
    this._touchStart=e=>{this.touchY=e.touches[0]?.clientY;};
    this._touchEnd=e=>{if(this.touchY!=null&&e.changedTouches[0]?.clientY-this.touchY>110&&window.scrollY<30)this.refresh();this.touchY=null;};
  }
  setConfig(config){this.config=config;this.render();}
  getCardSize(){return 8;}
  getGridOptions(){return {columns:12,rows:'auto'};}
  set hass(hass){this._hass=hass;if(!this.snapshot&&!this.loading&&this.isConnected)this.refresh();}
  connectedCallback(){document.addEventListener('visibilitychange',this._visibility);this.addEventListener('touchstart',this._touchStart,{passive:true});this.addEventListener('touchend',this._touchEnd,{passive:true});if(this._hass)this.refresh();}
  disconnectedCallback(){document.removeEventListener('visibilitychange',this._visibility);this.removeEventListener('touchstart',this._touchStart);this.removeEventListener('touchend',this._touchEnd);}
  async refresh(){
    if(!this._hass||this.loading)return;this.loading=true;this.refreshState();
    try{this.snapshot=this.prepareSnapshot(await this._hass.callWS({type:'nio_telematics/car_dashboard/get',entry_id:this.config.entry_id}));this.error='';this.render();}
    catch(e){this.error=e.message||'Rittenregistratie nog niet beschikbaar';if(!this.snapshot)this.render();else this.refreshState();}
    finally{this.loading=false;this.refreshState();}
  }
  refreshState(){const b=this.shadowRoot.querySelector('[data-action="refresh"]');if(b){b.disabled=this.loading;b.setAttribute('aria-busy',String(this.loading));}const err=this.shadowRoot.querySelector('.error');if(err)err.textContent=this.error;}
  esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  n(v,d=1){return v==null||!Number.isFinite(Number(v))?'—':Number(v).toLocaleString('nl-BE',{minimumFractionDigits:d,maximumFractionDigits:d});}
  date(t,opts){return new Date(t*1000).toLocaleString('nl-BE',opts||{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});}
  value(label,v,unit='',d=1){return `<div class="metric"><span>${label}</span><strong>${this.n(v,d)}${unit?`<small>${unit}</small>`:''}</strong></div>`;}
  category(c){return {home:'Thuis',work:'Werk',supercharger:'Snellader',other:'Onderweg'}[c]||'Onderweg';}
  tripEnergy(t){return t.segments.every(s=>s.kwh!=null)?t.segments.reduce((sum,s)=>sum+s.kwh,0):null;}
  prepareSnapshot(raw){
    const data=JSON.parse(JSON.stringify(raw)),cap=data.settings.capacity_kwh;
    const rangeStat=Object.values(raw.statistics).find(s=>s.projected_range_km!=null&&s.consumption_kwh_100km>0);
    const remainingEnergy=rangeStat?rangeStat.projected_range_km*rangeStat.consumption_kwh_100km/100:null;
    const chargedBetween=(a,b)=>data.charges.some(c=>c.kind!=='dismissed'&&c.start<b&&c.end>a);
    const trips=data.trips.sort((a,b)=>a.start-b.start);
    for(const trip of trips){
      for(const segment of trip.segments){
        const delta=segment.start_energy-segment.end_energy;
        if(segment.kwh==null&&segment.km>0&&Number.isFinite(delta)&&delta>=0&&!chargedBetween(segment.start,segment.end)){
          segment.kwh=delta;segment.estimated=true;
        }
      }
      trip.estimated=trip.segments.some(s=>s.estimated);
      trip.source_ids=[trip.id];
    }
    const estimates=new Map(trips.flatMap(t=>t.segments.map(s=>[`${s.start}/${s.end}`,s])));
    const costs=new Map(Object.values(data.statistics).flatMap(s=>s.segments||[]).map(s=>[`${s.start}/${s.end}`,s]));
    const recalculate=stat=>{
      for(const s of stat.segments){const source=estimates.get(`${s.start}/${s.end}`);if(s.kwh==null&&source?.kwh!=null){s.kwh=source.kwh*(s.km/source.km);s.estimated=true;}}
      const km=stat.segments.reduce((sum,s)=>sum+s.km,0),known=stat.segments.length&&stat.segments.every(s=>s.kwh!=null);
      stat.distance_km=km;stat.used_kwh=known?stat.segments.reduce((sum,s)=>sum+s.kwh,0):null;
      stat.soc_used_pct=stat.used_kwh==null?null:stat.used_kwh/cap*100;
      stat.consumption_kwh_100km=stat.used_kwh!=null&&km?stat.used_kwh/km*100:null;
      stat.estimated=stat.segments.some(s=>s.estimated);
      stat.projected_range_km=remainingEnergy!=null&&stat.consumption_kwh_100km>0?remainingEnergy/stat.consumption_kwh_100km*100:null;
      const petrol=data.preferences.petrol_l_100km,price=data.preferences.petrol_eur_l;
      stat.petrol_comparison_eur=petrol!=null&&price!=null?km/100*petrol*price:null;
      stat.petrol_saving_eur=stat.petrol_comparison_eur!=null&&stat.driving_cost_eur!=null?stat.petrol_comparison_eur-stat.driving_cost_eur:null;
      return stat;
    };
    for(const stat of Object.values(data.statistics))recalculate(stat);
    for(const counter of data.counters)recalculate(counter.statistics);
    const groups=[];let pending=null;
    for(const trip of trips){
      if(pending&&pending.distance_km<5&&!chargedBetween(pending.end,trip.start)&&pending.end_odo===trip.start_odo){
        pending.end=trip.end;pending.end_odo=trip.end_odo;pending.end_energy=trip.end_energy;
        pending.distance_km+=trip.distance_km;pending.segments.push(...trip.segments);
        pending.source_ids.push(trip.id);pending.complete&&=trip.complete;pending.estimated||=trip.estimated;
      }else{pending=trip;groups.push(pending);}
    }
    const active=groups.find(t=>t.source_ids.includes(data.active_trip_id));
    if(active)data.active_trip_id=active.id;
    const last=[...groups].reverse().find(t=>t.id!==data.active_trip_id&&(t.distance_km>=5||chargedBetween(t.end,Date.now()/1000)));
    const tripStat=t=>{
      const stat=JSON.parse(JSON.stringify(raw.statistics.last_trip));
      stat.segments=t.segments.map(s=>({...s,cost_eur:costs.get(`${s.start}/${s.end}`)?.cost_eur??null}));
      stat.driving_cost_eur=stat.segments.every(s=>s.cost_eur!=null)?stat.segments.reduce((sum,s)=>sum+s.cost_eur,0):null;
      stat.cost_eur_100km=stat.driving_cost_eur==null?null:stat.driving_cost_eur/t.distance_km*100;
      return recalculate(stat);
    };
    if(last)data.statistics.last_trip=tripStat(last);
    else{data.statistics.last_trip.segments=[];recalculate(data.statistics.last_trip);data.statistics.last_trip.driving_cost_eur=null;data.statistics.last_trip.cost_eur_100km=null;}
    if(active)data.statistics.current_trip=tripStat(active);
    data.trips=groups.reverse();
    return data;
  }
  endDate(c){return this.localISO(new Date(c.start*1000))===this.localISO(new Date(c.end*1000))?this.date(c.end,{hour:'2-digit',minute:'2-digit'}):this.date(c.end);}
  monthKey(t){const d=new Date(t*1000);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;}
  chargeCard(c){
    const needs=c.cost_eur==null||!c.confirmed;
    return `<button class="session" data-charge="${this.esc(c.id)}"><div class="row session-head"><span>${this.date(c.start)} → ${this.endDate(c)}</span><span class="place">${c.kind==='candidate'?'Lading controleren':this.category(c.category)}${needs?' <span class="receipt" aria-label="Prijs aanvullen">＋€</span>':''}</span></div><div class="metrics three">${this.value('Geladen',c.kwh,'kWh',2)}${this.value('Laadkosten',c.cost_eur,'€',2)}${this.value(c.category==='home'?'Laadvoordeel':'Tarief',c.category==='home'?c.benefit_eur:(c.cost_eur!=null&&c.kwh?c.cost_eur/c.kwh:null),c.category==='home'?'€':'€/kWh',2)}</div><div class="muted">${c.category==='home'?`${c.reimbursement_eur==null?'':`Vergoeding ${this.n(c.reimbursement_eur,2)} €`}${c.solar_pct==null?'':` · ${this.n(c.solar_pct,0)}% zon`}`:c.energy_basis==='range_estimate'?'Berekende energie':''}</div></button>`;
  }
  tripCard(t){
    const energy=this.tripEnergy(t);
    const cap=this.snapshot.settings.capacity_kwh;
    return `<button class="session ${this.snapshot.active_trip_id===t.id?'active':''}" data-trip="${this.esc(t.id)}"><div class="row session-head"><span>${this.date(t.start)} → ${this.date(t.end,{hour:'2-digit',minute:'2-digit'})}</span>${this.snapshot.active_trip_id===t.id?'<span class="place">Rit bezig</span>':''}</div><div class="metrics three">${this.value('Afstand',t.distance_km,'km')}${this.value('Gem. verbruik',energy!=null&&t.distance_km?energy/t.distance_km*100:null,'kWh/100 km')}${this.value('Batterij gebruikt',energy!=null?energy/cap*100:null,'%')}</div><div class="muted">${this.n(t.start_energy/cap*100,0)}% → ${this.n(t.end_energy/cap*100,0)}%${energy==null?' · Meting ontbreekt':` · ${this.n(energy,2)} kWh`}</div></button>`;
  }
  history(){
    const charging=this.tab==='charging', all=charging?this.snapshot.charges:this.snapshot.trips;
    const rows=all.slice(0,this.full?this.pageSize:3);
    let html=`<div class="row heading"><h2>${this.full?(charging?'Alle laadsessies':'Alle ritten'):(charging?'Laatste laadsessies':'Laatste ritten')}</h2>${charging?'<button class="icon" data-action="add" title="Lading toevoegen" aria-label="Lading toevoegen">＋</button>':''}</div>`;
    if(!rows.length)html+=`<div class="empty">${charging?'Nog geen laadsessies':'De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.'}</div>`;
    let month='';
    for(const item of rows){
      const key=this.monthKey(charging?item.start:item.end);
      if(this.full&&month!==key){month=key;const group=all.filter(r=>this.monthKey(charging?r.start:r.end)===key);
        const label=this.date(charging?item.start:item.end,{month:'long',year:'numeric'});
        let totals='';
        if(charging){const sum=k=>group.every(c=>c[k]!=null&&c.confirmed)?group.reduce((s,c)=>s+c[k],0):null;
          totals=`${this.n(group.filter(c=>c.confirmed).reduce((s,c)=>s+c.kwh,0),2)} kWh · ${this.n(sum('cost_eur'),2)} € laadkosten${group.some(c=>c.category==='home')?` · ${this.n(group.filter(c=>c.category==='home').every(c=>c.reimbursement_eur!=null)?group.filter(c=>c.category==='home').reduce((s,c)=>s+c.reimbursement_eur,0):null,2)} € vergoeding · ${this.n(group.filter(c=>c.category==='home').every(c=>c.benefit_eur!=null)?group.filter(c=>c.category==='home').reduce((s,c)=>s+c.benefit_eur,0):null,2)} € laadvoordeel`:''}`;
        }else{const km=group.reduce((s,t)=>s+t.distance_km,0);const energy=group.every(t=>this.tripEnergy(t)!=null)?group.reduce((s,t)=>s+this.tripEnergy(t),0):null;totals=`${this.n(km)} km · ${this.n(energy!=null&&km?energy/km*100:null)} kWh/100 km · ${group.length} ritten`;}
        html+=`<div class="month"><h3>${label}</h3><p>${totals}</p></div>`;
      }
      html+=charging?this.chargeCard(item):this.tripCard(item);
    }
    if(this.full&&all.length>this.pageSize)html+=`<button class="more" data-action="more">Meer tonen (${all.length-this.pageSize})</button>`;
    html+=`<button class="more" data-action="full">${this.full?'Terug naar de laatste drie':charging?'Alle laadsessies':'Alle ritten'} <span>›</span></button>`;
    return html;
  }
  graph(segments,mean){
    if(!segments.length)return '';
    const good=segments.filter(s=>s.kwh!=null&&s.km>0);if(!good.length)return '';
    const max=Math.max(mean||0,...good.map(s=>s.kwh/s.km*100))*1.2;
    const distance=segments.reduce((s,r)=>s+r.km,0);let x=0;
    const bars=segments.map(r=>{const width=r.km/distance*300;const left=x;x+=width;if(r.kwh==null)return '';const value=r.kwh/r.km*100;return `<rect x="${left}" y="${100-value/max*85}" width="${Math.max(.5,width-1)}" height="${value/max*85}" rx="2"><title>${this.n(r.km)} km · ${this.n(value)} kWh/100 km</title></rect>`;}).join('');
    return `<div class="chart"><svg viewBox="0 0 300 110" role="img" aria-label="Verbruik per gemeten rijsegment"><g fill="var(--car-accent)">${bars}</g>${mean!=null?`<path d="M0 ${100-mean/max*85} H300" class="mean"/>`:''}</svg><div class="row muted"><span>0 km</span><span>Gem. ${this.n(mean)} kWh/100 km</span><span>${this.n(distance,0)} km</span></div></div>`;
  }
  chargingGraph(){
    let rows=this.snapshot.charging_daily;
    const now=new Date();rows=rows.filter(r=>this.period==='day'?r.date===this.localISO(now):this.period==='year'?r.date.startsWith(String(now.getFullYear())):r.date.startsWith(this.localISO(now).slice(0,7)));
    if(!rows.length)return '';
    const cost=this.graphUnit==='eur',max=Math.max(1,...rows.map(r=>cost?r.known_cost_eur:r.kwh));
    const bars=rows.map((r,i)=>{const w=300/rows.length;const v=cost?r.known_cost_eur:r.kwh;return `<rect x="${i*w}" y="${95-v/max*80}" width="${Math.max(1,w-3)}" height="${v/max*80}" rx="2" opacity="${cost&&r.missing?.4:.9}"><title>${r.date}: ${this.n(v,2)} ${cost?'€':'kWh'}${r.missing?' · prijs ontbreekt':''}</title></rect>`;}).join('');
    return `<div class="panel"><div class="row"><h3>Laden</h3><div class="segmented compact"><button data-unit="kwh" class="${cost?'':'selected'}">kWh</button><button data-unit="eur" class="${cost?'selected':''}">€</button></div></div><div class="chart"><svg viewBox="0 0 300 100" role="img" aria-label="Laadenergie per dag"><g fill="var(--car-accent)">${bars}</g></svg><div class="row muted"><span>${rows[0].date.slice(5)}</span><span>${rows.at(-1).date.slice(5)}</span></div></div></div>`;
  }
  insight(){
    if(this.period==='current_trip'&&!this.snapshot.active_trip_id)this.period='last_trip';
    const stat=this.snapshot.statistics[this.period];if(!stat)return '';
    const groups=[[
      ['last_trip','Laatste rit','Laatste rit',''],
      ...(this.snapshot.active_trip_id?[['current_trip','Huidige rit','Huidige rit','']]:[]),
      ['since_charge','Sinds laadbeurt','Sinds laatste laadbeurt',''],
      ['last_100km','Laatste 100 km','Laatste 100 km','']
    ],[['day','Vandaag','Vandaag',''],['month','Maand','Maand',''],['year','Jaar','Jaar','']]];
    let html=groups.map(group=>`<div class="periods" style="--period-count:${group.length}">${group.map(([key,name,title,icon])=>`<button data-period="${key}" title="${title}" aria-label="${title}" aria-pressed="${this.period===key}" class="${this.period===key?'selected':''}">${icon?`<ha-icon icon="${icon}" aria-hidden="true"></ha-icon>`:''}<span>${name}</span></button>`).join('')}</div>`).join('');
    html+=`<div class="panel"><div class="metrics ${stat.cost_eur_100km!=null?'two':''} hero">${this.value('Gemiddeld verbruik',stat.consumption_kwh_100km,'kWh/100 km')}${stat.cost_eur_100km!=null?this.value('Rijkosten',stat.cost_eur_100km,'€/100 km',2):''}</div><div class="metrics three secondary">${this.value('Afstand',stat.distance_km,'km')}${this.value('Gebruikt',stat.used_kwh,'kWh')}${this.value('Batterij',stat.soc_used_pct,'%')}</div>${!stat.distance_km?'<p class="muted">Verbruik wordt zichtbaar na de eerste gemeten rit.</p>':''}</div>`;
    if(!['last_100km','last_trip','current_trip'].includes(this.period))html+=`<button class="parked-summary row" data-tab="parked"><span>Stilstand</span><strong>${this.n(stat.parked_loss_estimate_kwh,2)} kWh · ${this.n(stat.parked_loss_estimate_kwh/this.snapshot.settings.capacity_kwh*100)}%</strong><span aria-hidden="true">›</span></button>`;
    html+=`<div class="panel"><h3>Laadkosten</h3><div class="metrics three">${this.value('Totaal',stat.spend_eur,'€',2)}${this.value('Geladen',stat.charged_kwh,'kWh')}${this.value('Gem. tarief',stat.price_eur_kwh,'€/kWh',2)}</div><div class="metrics two secondary">${this.value('Gem. verbruik',stat.consumption_kwh_100km,'kWh/100 km')}${this.value('Rijkosten',stat.cost_eur_100km,'€/100 km',2)}</div>${stat.missing_prices||stat.unconfirmed_charges?`<button class="notice" data-action="missing">${stat.missing_prices} prijs${stat.missing_prices===1?'':'en'} aanvullen · Bekend: ${this.n(stat.known_spend_eur,2)} € <span>›</span></button>`:''}<div class="categories">${Object.entries(stat.categories).map(([k,r])=>`<div class="row"><span>${this.category(k)}</span><span>${this.n(r.kwh)} kWh · ${this.n(r.cost_eur,2)} €</span></div>`).join('')}</div></div>`;
    if(stat.segments.length||['day','month','year'].includes(this.period))html+=`<details class="details"><summary>Grafieken & bereik</summary>${this.graph(stat.segments,stat.consumption_kwh_100km)}${stat.projected_range_km!=null?`<div class="row range"><span>Bereik bij dit verbruik</span><strong>${this.n(stat.projected_range_km,0)} km</strong></div>`:''}${['day','month','year'].includes(this.period)?this.chargingGraph():''}</details>`;
    const rated=this.snapshot.preferences.rated_kwh_100km;
    if(rated>0&&stat.consumption_kwh_100km!=null)html+=`<div class="panel row"><span>Verbruik t.o.v. referentie<br><small>${this.n(rated)} kWh/100 km</small></span><strong>${this.n((stat.consumption_kwh_100km/rated-1)*100,0)}%</strong></div>`;
    if(stat.petrol_comparison_eur!=null)html+=`<div class="panel"><h3>Vergelijking benzine</h3><div class="metrics two">${this.value('Benzine voor deze afstand',stat.petrol_comparison_eur,'€',2)}${this.value('Besparing',stat.petrol_saving_eur,'€',2)}</div></div>`;
    html+=`<details class="details"><summary>Rittellers & instellingen</summary>${this.snapshot.counters.map(c=>`<div class="counter"><div class="row"><strong>${this.esc(c.name)}</strong><button class="text" data-reset="${c.id}">Reset</button></div><div class="metrics three">${this.value('Afstand',c.statistics.distance_km,'km')}${this.value('Verbruik',c.statistics.consumption_kwh_100km,'kWh/100 km')}${this.value('Kosten',c.statistics.cost_eur_100km,'€/100 km',2)}</div></div>`).join('')}<button class="more" data-action="counter">＋ Ritteller</button><button class="more" data-action="settings">Rekeninstellingen ›</button><p class="muted">Verbruik: ${this.snapshot.settings.capacity_kwh} kWh × verschil in berekende SoC. Rijkosten gebruiken de gemiddelde prijs van de energie in de batterij. Thuis telt de EVCC-waarde mee, inclusief misgelopen teruglevering. Laadverliezen zijn niet afzonderlijk gemeten.</p>${this.snapshot.source_status!=='fresh'?'<p class="muted">Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.</p>':''}</details>`;
    return `<div class="insight">${html}</div>`;
  }
  parkedHistory(){
    const all=this.snapshot.parked_periods||[],rows=all.slice(0,this.full?this.pageSize:3);
    let html=`<div class="row heading"><h2>${this.full?'Alle stilstandperiodes':'Laatste stilstandperiodes'}</h2></div>`;
    if(!rows.length)html+='<div class="empty">Nog geen geregistreerde bereikafname bij stilstand.</div>';
    const total=group=>{const energy=group.reduce((sum,p)=>sum+p.kwh,0);return `${this.n(energy,2)} kWh · ${this.n(energy/this.snapshot.settings.capacity_kwh*100)}%`;};
    let month='';
    for(const p of rows){
      const key=this.monthKey(p.end);
      if(this.full&&month!==key){month=key;html+=`<div class="month parked-month"><h3>${this.date(p.end,{month:'long',year:'numeric'})}</h3><p>${total(all.filter(r=>this.monthKey(r.end)===key))}</p></div>`;}
      html+=`<button class="session" data-parked="${this.esc(p.id)}"><div class="row session-head"><span>${this.date(p.start)} → ${this.date(p.end)}</span></div><div class="metrics three">${this.value('Duur',(p.end-p.start)/60,'min',0)}${this.value('Verbruikt',p.kwh,'kWh',2)}${this.value('Batterij',p.soc_used_pct,'%')}</div><div class="muted">Geschat uit bereikafname</div></button>`;
    }
    if(this.full&&all.length>this.pageSize)html+=`<button class="more" data-action="more">Meer tonen (${all.length-this.pageSize})</button>`;
    html+=`<button class="more" data-action="full">${this.full?'Terug naar de laatste drie':'Alle stilstandperiodes'} <span>›</span></button>`;
    if(!this.full&&all.length){const key=this.monthKey(all[0].end);html+=`<div class="month parked-month"><h3>${this.date(all[0].end,{month:'long',year:'numeric'})}</h3><p>${total(all.filter(p=>this.monthKey(p.end)===key))}</p></div>`;}
    return html;
  }
  render(){
    if(!this.config)return;
    this.shadowRoot.innerHTML=`<style>${CarLedgerCard.styles}</style><ha-card><div class="row top"><nav class="segmented main-tabs" aria-label="Autohistoriek">${[['charging','Laden'],['trips','Ritten'],['insight','Verbruik'],['parked','Stilstand']].map(([key,label])=>`<button data-tab="${key}" aria-pressed="${this.tab===key}" class="${this.tab===key?'selected':''}">${label}</button>`).join('')}</nav><button class="icon refresh" data-action="refresh" title="Vernieuwen" aria-label="Vernieuwen"><svg viewBox="0 0 24 24"><path d="M20 7v5h-5M20 12a8 8 0 1 0-2.4 5.7"/></svg></button></div><div class="error" role="status">${this.esc(this.error)}</div>${this.snapshot?(this.tab==='insight'?this.insight():this.tab==='parked'?this.parkedHistory():this.history()):'<div class="empty">Ritten en laadkosten laden…</div>'}</ha-card>`;
    this.shadowRoot.addEventListener('click',this._clickHandler ||= e=>this.click(e));
    this.refreshState();
  }
  async click(e){
    const b=e.target.closest('button');if(!b)return;
    if(b.dataset.tab){this.tab=b.dataset.tab;this.full=false;this.pageSize=36;this.render();await this.refresh();return;}
    if(b.dataset.period){this.period=b.dataset.period;this.render();return;}
    if(b.dataset.unit){this.graphUnit=b.dataset.unit;this.render();return;}
    if(b.dataset.charge){this.chargeDialog(this.snapshot.charges.find(c=>c.id===b.dataset.charge));return;}
    if(b.dataset.trip){this.tripDialog(this.snapshot.trips.find(t=>t.id===b.dataset.trip));return;}
    if(b.dataset.parked){const p=this.snapshot.parked_periods.find(r=>r.id===b.dataset.parked);this.dialog('Stilstand',`<p>${this.date(p.start)} → ${this.date(p.end)}</p><div class="metrics three">${this.value('Duur',(p.end-p.start)/60,'min',0)}${this.value('Verbruikt',p.kwh,'kWh',2)}${this.value('Batterij',p.soc_used_pct,'%')}</div><p class="muted">Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.</p>`);return;}
    if(b.dataset.reset){const c=this.snapshot.counters.find(c=>c.id===b.dataset.reset);this.dialog('Ritteller opnieuw starten',`<p>${this.esc(c.name)} vanaf nu opnieuw tellen?</p>`,async()=>this.update('counter',{ident:c.id,name:c.name}));return;}
    switch(b.dataset.action){
      case'refresh':await this.refresh();break;
      case'full':this.full=!this.full;this.render();break;
      case'more':this.pageSize+=36;this.render();break;
      case'missing':this.tab='charging';this.full=true;this.render();break;
      case'add':this.chargeDialog();break;
      case'counter':this.dialog('Nieuwe ritteller','<label>Naam<input name="name" maxlength="60" required placeholder="Trip A"></label>',async f=>this.update('counter',{name:f.get('name')}));break;
      case'settings':this.settingsDialog();break;
    }
  }
  localISO(d){const local=new Date(d.getTime()-d.getTimezoneOffset()*60000);return local.toISOString().slice(0,10);}
  inputDate(t){const d=new Date(t*1000);return new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,16);}
  chargeDialog(c){
    const now=Date.now()/1000;const isNew=!c;
    const form=`${c?`<p class="muted">${this.date(c.start)} · ${this.n(c.kwh,2)} kWh${c.energy_basis==='range_estimate'?' berekend':''}</p>`:`<div class="form-two"><label>Start<input type="datetime-local" name="start" required value="${this.inputDate(now-1800)}"></label><label>Einde<input type="datetime-local" name="end" required value="${this.inputDate(now)}"></label></div>`}<label>Prijs per kWh<input type="number" name="price" step="0.001" min="0" inputmode="decimal" placeholder="€/kWh" value="${c?.price_eur_kwh??''}"></label><label>Locatie<select name="category">${(c?.kind==='home'?['home']:['other','supercharger','work']).map(k=>`<option value="${k}" ${(c?.category||'other')===k?'selected':''}>${this.category(k)}</option>`).join('')}</select></label><details ${isNew?'open':''}><summary>Bon & energie</summary><label>Geladen kWh<input type="number" name="kwh" step="0.01" min="0.01" inputmode="decimal" ${isNew?'required':''} value="${c?.kwh??''}"></label><label>Totaal op bon (optioneel)<input type="number" name="receipt" step="0.01" min="0" inputmode="decimal" placeholder="€"></label></details>${c?.kind==='candidate'?'<p class="muted">De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.</p><button type="button" class="more" data-dismiss="true">Dit was geen lading</button>':''}`;
    this.dialog(isNew?'Lading toevoegen':c.kind==='candidate'?'Lading bevestigen':'Laadprijs',form,async f=>{
      const values={category:f.get('category')};for(const key of ['price','receipt','kwh'])if(f.get(key)!==''&&f.get(key)!=null&&(key!=='kwh'||isNew||Number(f.get(key))!==c.kwh||f.get('receipt')!==''))values[key]=Number(f.get(key));
      if(values.price==null&&values.receipt==null&&!c?.confirmed)throw new Error('Vul de prijs per kWh of het bedrag op de bon in.');
      if(isNew){values.start=new Date(f.get('start')).getTime()/1000;values.end=new Date(f.get('end')).getTime()/1000;await this.update('add_charge',values);}
      else await this.update('edit_charge',{ident:c.id,...values});
    },c);
  }
  tripDialog(t){
    const cap=this.snapshot.settings.capacity_kwh;const energy=this.tripEnergy(t);
    this.dialog('Ritdetails',`<p>${this.date(t.start)} → ${this.date(t.end)}</p><div class="metrics two">${this.value('Afstand',t.distance_km,'km')}${this.value('Energie gebruikt',energy,'kWh',2)}${this.value('Batterij bij vertrek',t.start_energy/cap*100,'%')}${this.value('Batterij bij aankomst',t.end_energy/cap*100,'%')}</div><p class="muted">Kilometerstand ${this.n(t.start_odo,0)} → ${this.n(t.end_odo,0)} km. Tijden volgen de ontvangen metingen. Verbruik is berekend uit bereik met ${cap} kWh beschikbare batterij. Afname zonder kilometerverandering telt afzonderlijk als stilstandsverlies.${energy==null?' Energie ontbreekt door ontbrekende metingen of tussentijds laden.':''}</p>`,null);
  }
  settingsDialog(){
    const p=this.snapshot.preferences;
    const fields=[['opening_price_eur_kwh','Prijs energie bij start van registratie (€/kWh)'],['rated_kwh_100km','Referentieverbruik (kWh/100 km)'],['petrol_l_100km','Vorige auto (l/100 km)'],['petrol_eur_l','Benzineprijs (€/l)']];
    this.dialog('Rekeninstellingen',`<p class="muted">De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.</p>${fields.map(([key,label])=>`<label>${label}<input type="number" name="${key}" min="0" step="0.001" value="${p[key]??''}" inputmode="decimal"></label>`).join('')}`,async f=>{const values={};for(const [key]of fields)values[key]=f.get(key)===''?null:Number(f.get(key));await this.update('preferences',values);});
  }
  dialog(title,content,save,c){
    const el=document.createElement('dialog');el.className='modal';el.innerHTML=`<form><div class="row"><h2>${this.esc(title)}</h2><button type="button" class="icon" data-close aria-label="Sluiten">×</button></div>${content}<p class="form-error" role="alert"></p>${save?'<button class="save" type="submit">Opslaan</button>':''}</form>`;
    this.shadowRoot.append(el);el.addEventListener('close',()=>el.remove());el.querySelector('[data-close]').onclick=()=>el.close();
    el.addEventListener('click',async e=>{if(e.target===el)el.close();if(e.target.closest('[data-dismiss]')){try{await this.update('dismiss_candidate',{ident:c.id});el.close();}catch(err){el.querySelector('.form-error').textContent=err.message;}}});
    el.querySelector('form').onsubmit=async e=>{e.preventDefault();if(!save){el.close();return;}const button=el.querySelector('.save');button.disabled=true;try{await save(new FormData(e.target));el.close();}catch(err){el.querySelector('.form-error').textContent=err.message;button.disabled=false;}};el.showModal();
  }
  async update(action,values){this.snapshot=this.prepareSnapshot(await this._hass.callWS({type:'nio_telematics/car_dashboard/update',entry_id:this.config.entry_id,action,values}));this.render();}
  static styles=`
    :host{--car-accent:#47776e;--car-surface:var(--card-background-color,#fff);--car-text:var(--primary-text-color,#18211f);--car-muted:var(--secondary-text-color,#777e7b);display:block;color:var(--car-text);font-family:var(--paper-font-body1_-_font-family,Arial,sans-serif)}
    *{box-sizing:border-box}ha-card{background:transparent;border:0;box-shadow:none;padding:4px 0 16px}button,input,select{font:inherit;color:inherit}button{cursor:pointer}button:focus-visible,summary:focus-visible{outline:2px solid var(--car-accent);outline-offset:3px}button:disabled{opacity:.45;cursor:wait}h2,h3,p{margin:0}h2{font-size:16px;font-weight:600}h3{font-size:14px;font-weight:600}.row{display:flex;align-items:center;justify-content:space-between;gap:12px}.top{gap:10px;margin-bottom:18px}.segmented{display:flex;background:rgba(128,128,128,.075);border-radius:13px;padding:4px;gap:3px;flex:1}.segmented button{flex:1;border:0;background:transparent;padding:10px 7px;border-radius:10px;font-size:14px;color:var(--car-muted)}.segmented button.selected{background:var(--car-surface);color:var(--car-text);box-shadow:0 1px 4px #0000000a;font-weight:600}.icon{background:transparent;border:0;width:34px;height:34px;padding:7px;font-size:22px;border-radius:50%;display:grid;place-items:center}.refresh svg{width:21px;height:21px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}.heading{margin:0 3px 11px}.session,.panel{width:100%;text-align:left;background:var(--car-surface);border:1px solid rgba(128,128,128,.18);border-radius:20px;padding:18px;margin:0 0 9px}.session-head{font-size:11px;margin-bottom:17px;color:var(--car-muted)}.place{white-space:nowrap;font-size:10px}.receipt{color:var(--car-accent);font-size:13px;margin-left:4px}.metrics{display:grid;gap:12px}.three{grid-template-columns:repeat(3,minmax(0,1fr))}.two{grid-template-columns:repeat(2,minmax(0,1fr))}.metric span{display:block;color:var(--car-muted);font-size:10px;margin-bottom:6px}.metric strong{font-size:21px;line-height:1.15;font-weight:500;letter-spacing:-.6px;white-space:nowrap}.metric small{font-size:11px;margin-left:4px;letter-spacing:0;font-weight:400}.muted{font-size:11px;color:var(--car-muted);line-height:1.5}.session>.muted{margin-top:14px;min-height:0}.session.active{background:color-mix(in srgb,var(--car-accent) 5%,var(--car-surface))}.more,.text{background:none;border:0;padding:13px 3px;font-size:12px}.more{width:100%;display:flex;justify-content:space-between;align-items:center}.month{margin:23px 3px 12px}.month h3{font-size:13px;text-transform:capitalize}.month p{font-size:10px;color:var(--car-muted);margin-top:6px;line-height:1.5}.periods{display:grid;grid-template-columns:repeat(var(--period-count,3),minmax(0,1fr));gap:3px;margin:0 0 7px;padding:0;background:transparent;border-bottom:1px solid #8882}.periods+ .panel{margin-top:16px}.periods button{display:flex;align-items:center;justify-content:center;gap:6px;min-width:0;min-height:40px;white-space:nowrap;border:0;background:transparent;border-radius:0;padding:12px 0;font-size:12px;color:var(--car-muted);border-bottom:2px solid transparent}.periods .selected{background:transparent;border-bottom-color:var(--car-text);color:var(--car-text);font-weight:600}.periods:has([data-period="current_trip"]) button{font-size:10px}.panel>h3{margin-bottom:18px}.hero .metric strong{font-size:30px}.hero .metric small{display:block;margin:7px 0 0;font-size:11px}.secondary{margin-top:23px}.secondary .metric strong{font-size:18px}.chart{margin-top:24px}.chart svg{display:block;width:100%;height:auto;max-height:150px}.chart .muted{font-size:9px}.mean{stroke:var(--car-text);stroke-width:1;stroke-dasharray:3 3;fill:none;opacity:.6}.range{font-size:12px;border-top:1px solid #8882;margin-top:18px;padding-top:14px}.range strong{font-size:18px;font-weight:500}.notice{background:rgba(128,128,128,.05);border:0;padding:10px;border-radius:9px;font-size:11px;width:100%;text-align:left;margin-top:18px;display:flex;justify-content:space-between}.categories .row{font-size:11px;margin-top:14px;color:var(--car-muted)}.compact{flex:none;width:85px;padding:2px}.compact button{padding:5px;font-size:11px}.details{margin:17px 3px;font-size:12px}.details summary{cursor:pointer;padding:10px 0}.details p{margin:13px 0}.counter{padding:15px 0;border-bottom:1px solid #8882}.counter .metrics{margin-top:10px}.counter strong{font-size:13px}.counter .metric strong{font-size:16px}.empty{padding:30px 12px;font-size:13px;color:var(--car-muted);line-height:1.6}.error:empty{display:none}.error{font-size:12px;padding:8px;color:var(--error-color,#ac594d)}.modal{background:var(--car-surface);color:var(--car-text);border:1px solid #8882;border-radius:22px;padding:24px;width:min(92vw,440px);max-height:90dvh;box-shadow:0 12px 60px #0003}.modal::backdrop{background:#0006;backdrop-filter:blur(3px)}.modal h2{font-size:19px}.modal p{margin:15px 0}.modal label{display:block;font-size:11px;color:var(--car-muted);margin:18px 0}.modal input,.modal select{display:block;width:100%;margin-top:7px;padding:12px;border-radius:10px;border:1px solid #8883;background:transparent;color:var(--car-text);font-size:16px}.modal summary{font-size:12px;cursor:pointer;padding-top:14px}.save{border:0;background:var(--car-accent);color:white;border-radius:12px;width:100%;padding:13px;margin-top:12px}.form-two{display:grid;grid-template-columns:1fr 1fr;gap:10px}.form-error{color:var(--error-color,#a44);font-size:12px}@media(max-width:380px){.session,.panel{padding:15px}.metric strong{font-size:18px}.metric small{font-size:9px}.hero .metric strong{font-size:27px}.session-head{font-size:10px}.metrics{gap:8px}.form-two{grid-template-columns:1fr}}
    .modal input,.modal select{min-width:0;max-width:100%}.form-two{grid-template-columns:repeat(2,minmax(0,1fr))}@media(max-width:440px){.form-two{grid-template-columns:1fr;gap:0}}
    .main-tabs{background:transparent;border-radius:0;padding:0;gap:0;border-bottom:1px solid #8882}.main-tabs button{min-width:0;border-radius:0;padding:13px 2px;font-size:13px;border-bottom:2px solid transparent;white-space:nowrap}.main-tabs button.selected{background:transparent;box-shadow:none;border-bottom-color:var(--car-accent);color:var(--car-text)}.top{gap:6px;margin-bottom:19px}.refresh{flex:none;width:30px;height:30px;padding:5px}.insight .panel{background:transparent;border:0;border-bottom:1px solid #8882;border-radius:0;padding:20px 3px;margin:0}.insight .hero .metric strong{font-size:38px}.insight .hero .metric small{display:inline;margin-left:6px;font-size:12px}.insight .metrics.two.hero .metric strong{font-size:30px}.parked-summary{width:100%;background:transparent;border:0;border-bottom:1px solid #8882;padding:18px 3px;font-size:13px;text-align:left}.parked-summary strong{font-size:13px;font-weight:500}.parked-month{border-top:1px solid #8882;padding-top:16px;margin:14px 3px}.parked-month p{font-size:15px;color:var(--car-text)}
  `;
}
// HA also preloads this module: let the versioned resource refresh an already registered class.
const registeredCarLedger=customElements.get('car-ledger-card');
if(registeredCarLedger){
  for(const key of Object.getOwnPropertyNames(CarLedgerCard.prototype)){
    if(key!=='constructor')Object.defineProperty(registeredCarLedger.prototype,key,Object.getOwnPropertyDescriptor(CarLedgerCard.prototype,key));
  }
  registeredCarLedger.styles=CarLedgerCard.styles;
}else customElements.define('car-ledger-card',CarLedgerCard);
window.customCards=window.customCards||[];window.customCards.push({type:'car-ledger-card',name:'Car Ledger',description:'Charging, trips and consumption in one snapshot dashboard'});
