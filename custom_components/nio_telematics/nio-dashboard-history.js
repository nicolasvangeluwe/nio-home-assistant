// NIO-owned presentation over the existing ledger. Never patch the household card.
const baseVersion=new URL(import.meta.url).searchParams.get('base_version')||'';
const {CarLedgerCard}=await import(`/nio_telematics/car-dashboard.js?nio_owned=1&v=${encodeURIComponent(baseVersion)}`);
const HISTORY_ICONS={"left":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m15 18-6-6 6-6\" />\n</svg>\n","right":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m9 18 6-6-6-6\" />\n</svg>\n","calendar":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M8 2v3\" />\n  <path d=\"M16 2v3\" />\n  <rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\" />\n  <path d=\"M3 9h18\" />\n  <path d=\"M8 13h.01\" />\n  <path d=\"M12 13h.01\" />\n  <path d=\"M16 13h.01\" />\n  <path d=\"M8 17h.01\" />\n  <path d=\"M12 17h.01\" />\n  <path d=\"M16 17h.01\" />\n</svg>\n","refresh":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8\" />\n  <path d=\"M21 3v5h-5\" />\n  <path d=\"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16\" />\n  <path d=\"M8 16H3v5\" />\n</svg>\n","sliders":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M10 5H3\" />\n  <path d=\"M12 19H3\" />\n  <path d=\"M14 3v4\" />\n  <path d=\"M16 17v4\" />\n  <path d=\"M21 12h-9\" />\n  <path d=\"M21 19h-5\" />\n  <path d=\"M21 5h-7\" />\n  <path d=\"M8 10v4\" />\n  <path d=\"M8 12H3\" />\n</svg>\n","plus":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M5 12h14\" />\n  <path d=\"M12 5v14\" />\n</svg>\n","close":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M18 6 6 18\" />\n  <path d=\"m6 6 12 12\" />\n</svg>\n"};
const HISTORY_STYLE=":host{display:block;--car-accent:var(--accent);font-family:\"Segoe UI\",Arial,sans-serif}*{box-sizing:border-box}ha-card{background:transparent;border:0;box-shadow:none;padding:0}h2,h3{font-weight:400}.top{position:sticky;top:0;z-index:3;background:var(--base);padding:8px 0 12px;gap:6px}.main-tabs{display:flex;gap:4px;flex:1;border:0;padding:0;background:none}.main-tabs button{flex:1;min-height:44px;padding:6px 9px;font:400 13px \"Segoe UI\";border:1px solid var(--divider-color);border-radius:8px;background:transparent;color:var(--primary-text-color)}.main-tabs button.selected{background:var(--accent);border-color:var(--accent);color:#000f16;box-shadow:none}.refresh{width:44px;height:44px}.refresh svg{width:18px;height:18px}.calendar-row{display:flex;align-items:center;gap:5px;padding:0 0 14px;border-bottom:1px solid var(--divider-color);margin-bottom:14px}.calendar-row button{min-height:44px;border:1px solid var(--divider-color);border-radius:7px;padding:6px 9px;background:none;color:var(--primary-text-color);font:400 12px \"Segoe UI\"}.calendar-row svg{width:16px;height:16px}.calendar-row .date{display:flex;align-items:center;gap:6px}.calendar-row button:nth-last-child(2){margin-left:auto}.calendar-row .arrow{border:0;padding:4px;width:27px}.heading{margin:13px 0 7px}.heading h2{font-size:17px}.month{margin-top:0}.month h3{display:none}.month p{font-size:12px;color:var(--secondary-text-color);line-height:1.7;margin:0 0 14px}.session{display:block;border:1px solid var(--divider-color);border-radius:10px;background:var(--card-background-color);padding:14px 15px;margin-bottom:10px;color:var(--primary-text-color);width:100%}.session-head{font-size:12px;line-height:1.5}.metric>span{font-size:12px}.metric strong{font-size:21px;font-weight:300;line-height:1.5;white-space:nowrap}.metric strong small{display:inline;font-size:12px;font-weight:400;margin-left:4px}.metrics{gap:12px}.muted{font-size:12px;line-height:1.5}.panel{background:var(--card-background-color);border:1px solid var(--divider-color);border-radius:10px}.panel .hero .metric strong{font-size:27px;font-weight:300}.details{border:1px solid var(--divider-color);border-radius:9px;margin-bottom:12px}.details>summary{font-size:13px;padding:12px}.periods{gap:5px}.periods button{min-height:44px;font:400 12px \"Segoe UI\"}.periods button.selected{background:var(--soft);border-color:var(--accent)}.modal{background:var(--card-background-color);color:var(--primary-text-color);border:1px solid var(--divider-color);border-radius:14px;max-height:85vh}.modal .icon{min-width:44px;min-height:44px}.counter-links{display:flex;gap:6px}.counter-links button{min-height:44px;padding:5px 9px;border:1px solid var(--divider-color);border-radius:7px;background:none;color:inherit;font:400 12px \"Segoe UI\"}@media(max-width:440px){.main-tabs button{font-size:12px;padding:5px 6px}.metrics{gap:7px}.metric strong{font-size:19px}.metric strong small{font-size:10px}.session{padding:12px}.calendar-row{gap:1px}.calendar-row button{font-size:11px;padding:5px 7px}}\n :host{--ui-related:12px;--ui-section-gap:24px}\n .history-context{position:sticky;top:52px;z-index:8;background:var(--base);border-bottom:1px solid var(--divider-color);margin-bottom:24px;padding-bottom:8px}\n .history-context .top{position:static;margin:0;padding:0;display:block}\n .calendar-row{position:static;min-height:44px;margin:8px 0 0;padding:0;border:0;gap:4px}\n .calendar-row button{font-weight:400}.date-group,.date-tools{gap:4px}\n /* A 36px visible face sits inside each non-overlapping 44px target. */\n .main-tabs,.periods,.segmented.compact{position:relative;isolation:isolate;height:44px;min-height:44px;box-sizing:border-box;border:0;border-radius:0;overflow:visible;padding:0;background:transparent;gap:0}\n .main-tabs::after,.periods::after,.segmented.compact::after{content:\"\";position:absolute;inset:4px 0;border:1px solid var(--divider-color);border-radius:999px;pointer-events:none;z-index:2}\n .main-tabs button,.main-tabs button.selected,.periods button,.periods button.selected,.segmented.compact button,.segmented.compact button.selected{position:relative;isolation:isolate;box-sizing:border-box;height:44px;min-height:44px;margin:0;padding:0 4px;border:0;border-radius:0;box-shadow:none;background:transparent;font:400 13px/1.4 \"Segoe UI\",sans-serif;color:var(--secondary-text-color)}\n .main-tabs button::before,.periods button::before,.segmented.compact button::before{content:\"\";position:absolute;inset:4px 0;z-index:-1;border-right:1px solid var(--divider-color);pointer-events:none}\n .main-tabs button:first-child::before,.periods button:first-child::before,.segmented.compact button:first-child::before{border-radius:18px 0 0 18px}\n .main-tabs button:last-child::before,.periods button:last-child::before,.segmented.compact button:last-child::before{border:0;border-radius:0 18px 18px 0}\n .main-tabs button.selected,.periods button.selected,.segmented.compact button.selected{color:var(--primary-text-color)}\n .main-tabs button.selected::before,.periods button.selected::before,.segmented.compact button.selected::before{background:var(--soft)}\n .history-scopes{margin:0}.insight>.periods{margin:0 0 16px}\n .segmented.compact{display:flex;width:100px;flex:none}.segmented.compact button{flex:1}\n .content-title{font:400 17px/1.4 \"Segoe UI\",sans-serif;margin:0 0 12px}\n .heading{margin:0 0 12px;gap:12px;min-height:24px}.heading h2{font:400 17px/1.4 \"Segoe UI\",sans-serif;margin:0}\n .heading:has(button){min-height:44px}.heading .icon{width:44px;height:44px;padding:10px}\n .counter-links{gap:8px}.counter-links button{position:relative;font:400 12px/1.4 \"Segoe UI\",sans-serif;border:0;border-radius:0;min-height:44px}\n .counter-links button::before{content:\"\";position:absolute;inset:4px 0;border:1px solid var(--divider-color);border-radius:8px;pointer-events:none}\n .month,.parked-month{margin:0 3px 16px;padding:0;border:0}.month h3{display:none;font:400 14px/1.5 \"Segoe UI\",sans-serif;margin:20px 0 12px}\n .show-month-labels .month h3{display:block}.month:first-of-type h3{margin-top:0}\n .period-summary{margin:0;column-gap:12px;row-gap:6px}.period-summary.cols3{grid-template-columns:minmax(0,1fr) minmax(0,1.6fr) minmax(0,.55fr)}\n .period-summary small{font:400 12px/1.5 \"Segoe UI\",sans-serif}.period-summary strong{font:300 21px/1.4 \"Segoe UI\",sans-serif}\n .period-summary .unit,.metric strong small{display:inline;font:400 12px/1.4 \"Segoe UI\",sans-serif}\n .session{padding:16px;margin-bottom:12px;border-radius:12px}.session-head{font:400 12px/1.5 \"Segoe UI\",sans-serif;margin-bottom:16px;gap:12px}.place{font-size:12px}\n .metrics{gap:6px 12px}.metrics.three{grid-template-columns:minmax(0,1fr) minmax(0,1.5fr) minmax(0,.9fr)}\n .metric>span{font:400 12px/1.5 \"Segoe UI\",sans-serif}.metric strong{font-size:21px;line-height:1.4;font-weight:300!important;letter-spacing:normal}\n .session .muted{font:400 12px/1.5 \"Segoe UI\",sans-serif;margin-top:16px}\n .insight>.panel{padding:16px;margin:0 0 24px;border-radius:12px}.insight .panel>h3,.insight .panel>.row h3{font:400 17px/1.4 \"Segoe UI\",sans-serif;margin:0}\n .insight .panel>h3{margin-bottom:16px}.insight .panel .metrics{margin:0}.insight .panel .metrics.secondary{margin-top:24px}\n .insight .hero .metric strong{font-size:30px}.insight .metrics.two.hero .metric strong{font-size:30px}\n .insight .details{margin:0 0 24px;border-radius:12px}.details>summary{font:400 14px/1.5 \"Segoe UI\",sans-serif;min-height:44px;padding:12px 16px}\n .insight .details>.chart,.insight .details>.range{margin:16px}.insight .details>.panel{border:0;background:transparent;border-radius:0;padding:0 16px 16px;margin:24px 0 0}\n .insight .chart{margin-top:16px}.insight .range strong{font:300 21px/1.4 \"Segoe UI\",sans-serif}\n .insight .parked-summary{padding:16px 0;margin:0 0 24px;font-size:14px}.parked-summary strong{font-size:13px;font-weight:400}\n .empty{padding:24px 0;font:400 14px/1.6 \"Segoe UI\",sans-serif}\n .modal{box-sizing:border-box;width:min(calc(100vw - 32px),500px);max-height:calc(100dvh - 32px);padding:20px;border-radius:14px;font:400 14px/1.5 \"Segoe UI\",sans-serif}\n .modal h2{font:400 20px/1.4 \"Segoe UI\",sans-serif;margin:0}.modal>.row:has(h2){min-height:44px;align-items:flex-start;gap:12px;margin-bottom:16px}\n .modal>.row h2{padding-top:7px}.modal .icon{width:44px;height:44px;flex:0 0 44px;padding:10px}.modal .row>h2{flex:1;min-width:0}\n .modal .metrics{margin:16px 0}.modal label,.modal .muted{font-size:12px;line-height:1.6}.modal p{margin:16px 0;line-height:1.6}\n .modal input,.modal select{min-height:44px;font-size:14px}.modal .form-error{font-size:12px;line-height:1.5}.modal .save{min-height:44px;color:#000;font:400 14px/1.4 \"Segoe UI\",sans-serif}\n @media(max-width:800px){.history-context{top:0}.metric strong{font-size:19px}.session{padding:16px}.insight .panel.hero{padding:16px}}\n @media(max-width:350px){.main-tabs button,.main-tabs button.selected,.periods button,.periods button.selected{font-size:12px}.metrics.three{grid-template-columns:minmax(0,.9fr) minmax(0,1.8fr) minmax(0,.9fr)}.metric strong{font-size:18px}.insight .hero .metric strong,.insight .metrics.two.hero .metric strong{font-size:24px}.modal{padding:16px}}\n\n:host{--car-accent:var(--accent,#659e91);--base:var(--primary-background-color,#fafafa);--soft:color-mix(in srgb,var(--car-accent) 20%,transparent);font-family:\"Segoe UI\",sans-serif}\n.history-context{position:static}.main-tabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr))}.period-summary{display:grid;margin-bottom:16px}.period-summary.cols2{grid-template-columns:repeat(2,minmax(0,1fr))}.period-summary.cols4{grid-template-columns:repeat(4,minmax(0,1fr))}.period-summary small,.period-summary strong{display:block}.period-summary strong .unit{display:inline}\n.calendar-row{display:flex;flex-wrap:wrap;justify-content:space-between}.date-group,.date-tools{display:flex;align-items:center;min-width:0}.date-tools{margin-left:auto}.calendar-row button{border:0;background:none;min-width:44px;min-height:44px;padding:6px;color:var(--primary-text-color);font:400 12px/1.5 \"Segoe UI\",sans-serif}.calendar-row .date{display:flex;gap:6px;align-items:center;color:var(--car-accent);padding:6px 2px}.calendar-row .arrow{width:44px;height:44px;padding:12px}.calendar-row svg,.icon svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.7}.calendar-row .date svg{width:16px;height:16px}.calendar-row .refresh{margin:0}.calendar-row [aria-pressed=true]{color:var(--car-accent)}.history-context{padding-bottom:8px}.error{margin-bottom:12px}\n.metrics{align-items:start}.metric{min-width:0}.metric>span{min-height:36px;display:flex;align-items:flex-end}.metric strong small{margin-left:3px;white-space:nowrap}.period-summary small{min-height:36px;display:flex;align-items:flex-end}.modal .filter-check{display:flex;align-items:center;gap:12px}.modal .filter-check input{width:24px;height:24px;min-height:24px;margin:0;accent-color:var(--car-accent)}\n@media(max-width:440px){.calendar-row{gap:0}.date-group{width:100%;justify-content:space-between}.date-tools{margin-left:auto}.metrics.three .metric strong{font-size:19px}.period-summary.cols4{grid-template-columns:repeat(2,minmax(0,1fr))}.main-tabs button{padding:0 2px}.counter-links{gap:4px}.counter-links button{padding:4px;font-size:11px}.metric strong small{font-size:12px}}";
const UI_KEYS=['charging','trips','energy','parked','day','week','month','year','today','chooseDate','apply','filters','all','known','missing','priceMissing','loading','refresh','previous','next','date','close','counters'];
const UI_ROWS={
 en:['Charging','Trips','Energy','Parked','Day','Week','Month','Year','Today','Choose date','Apply','Filters','All records','Measured energy','Missing readings','Missing price','Loading history…','Refresh','Previous period','Next period','Date','Close','Trip counters'],
 nl:['Laden','Ritten','Energie','Stilstand','Dag','Week','Maand','Jaar','Vandaag','Datum kiezen','Toepassen','Filters','Alle records','Gemeten energie','Ontbrekende metingen','Prijs ontbreekt','Historiek laden…','Vernieuwen','Vorige periode','Volgende periode','Datum','Sluiten','Rittellers'],
 de:['Laden','Fahrten','Energie','Parken','Tag','Woche','Monat','Jahr','Heute','Datum wählen','Anwenden','Filter','Alle Einträge','Gemessene Energie','Fehlende Messungen','Preis fehlt','Verlauf wird geladen…','Aktualisieren','Vorheriger Zeitraum','Nächster Zeitraum','Datum','Schließen','Fahrtzähler'],
 fr:['Recharge','Trajets','Énergie','Stationnement','Jour','Semaine','Mois','Année','Aujourd’hui','Choisir la date','Appliquer','Filtres','Tous les relevés','Énergie mesurée','Relevés manquants','Prix manquant','Chargement de l’historique…','Actualiser','Période précédente','Période suivante','Date','Fermer','Compteurs de trajet'],
 nb:['Lading','Turer','Energi','Parkert','Dag','Uke','Måned','År','I dag','Velg dato','Bruk','Filtre','Alle poster','Målt energi','Manglende målinger','Pris mangler','Laster historikk…','Oppdater','Forrige periode','Neste periode','Dato','Lukk','Turtellere'],
 sv:['Laddning','Resor','Energi','Parkerad','Dag','Vecka','Månad','År','I dag','Välj datum','Tillämpa','Filter','Alla poster','Uppmätt energi','Saknade mätningar','Pris saknas','Läser historik…','Uppdatera','Föregående period','Nästa period','Datum','Stäng','Trippmätare'],
 da:['Opladning','Ture','Energi','Parkeret','Dag','Uge','Måned','År','I dag','Vælg dato','Anvend','Filtre','Alle poster','Målt energi','Manglende målinger','Pris mangler','Indlæser historik…','Opdater','Forrige periode','Næste periode','Dato','Luk','Triptællere'],
 cs:['Nabíjení','Jízdy','Energie','Stání','Den','Týden','Měsíc','Rok','Dnes','Vybrat datum','Použít','Filtry','Všechny záznamy','Změřená energie','Chybějící měření','Chybějící cena','Načítání historie…','Obnovit','Předchozí období','Další období','Datum','Zavřít','Počítadla jízd'],
 el:['Φόρτιση','Ταξίδια','Ενέργεια','Στάθμευση','Ημέρα','Εβδομάδα','Μήνας','Έτος','Σήμερα','Επιλογή ημερομηνίας','Εφαρμογή','Φίλτρα','Όλες οι εγγραφές','Μετρημένη ενέργεια','Ελλιπείς μετρήσεις','Λείπει η τιμή','Φόρτωση ιστορικού…','Ανανέωση','Προηγούμενη περίοδος','Επόμενη περίοδος','Ημερομηνία','Κλείσιμο','Μετρητές ταξιδιών'],
 hu:['Töltés','Utazások','Energia','Parkolás','Nap','Hét','Hónap','Év','Ma','Dátum választása','Alkalmaz','Szűrők','Minden bejegyzés','Mért energia','Hiányzó mérések','Hiányzó ár','Előzmények betöltése…','Frissítés','Előző időszak','Következő időszak','Dátum','Bezárás','Utazásszámlálók'],
 lb:['Oplueden','Faarten','Energie','Stillstand','Dag','Woch','Mount','Joer','Haut','Datum wielen','Uwenden','Filteren','All Opzeechnungen','Gemoossen Energie','Feelend Miessungen','Präis feelt','Historik gëtt gelueden…','Erfrëschen','Vireg Period','Nächst Period','Datum','Zoumaachen','Faartenzieler'],
 pl:['Ładowanie','Przejazdy','Energia','Postój','Dzień','Tydzień','Miesiąc','Rok','Dzisiaj','Wybierz datę','Zastosuj','Filtry','Wszystkie wpisy','Zmierzona energia','Brakujące odczyty','Brak ceny','Wczytywanie historii…','Odśwież','Poprzedni okres','Następny okres','Data','Zamknij','Liczniki przejazdów'],
 pt:['Carregamento','Viagens','Energia','Parado','Dia','Semana','Mês','Ano','Hoje','Escolher data','Aplicar','Filtros','Todos os registos','Energia medida','Leituras em falta','Preço em falta','A carregar histórico…','Atualizar','Período anterior','Período seguinte','Data','Fechar','Contadores de viagem'],
 ro:['Încărcare','Călătorii','Energie','Staționare','Zi','Săptămână','Lună','An','Astăzi','Alege data','Aplică','Filtre','Toate înregistrările','Energie măsurată','Citiri lipsă','Preț lipsă','Se încarcă istoricul…','Reîmprospătează','Perioada anterioară','Perioada următoare','Data','Închide','Contoare de călătorie'],
};

const EMPTY_PERIOD={en:'No records in this period.',nl:'Geen registraties in deze periode.',de:'Keine Aufzeichnungen in diesem Zeitraum.',fr:'Aucun relevé pour cette période.',nb:'Ingen registreringer i denne perioden.',sv:'Inga registreringar under denna period.',da:'Ingen registreringer i denne periode.',cs:'V tomto období nejsou žádné záznamy.',el:'Δεν υπάρχουν εγγραφές για αυτή την περίοδο.',hu:'Ebben az időszakban nincs bejegyzés.',lb:'Keng Opzeechnungen an dëser Period.',pl:'Brak zapisów w tym okresie.',pt:'Sem registos neste período.',ro:'Nu există înregistrări în această perioadă.'};
const EMPTY_FILTERS={en:'No records match these filters in this period.',nl:'Geen registraties voldoen aan deze filters in deze periode.',de:'Keine Aufzeichnungen entsprechen diesen Filtern in diesem Zeitraum.',fr:'Aucun relevé ne correspond à ces filtres pour cette période.',nb:'Ingen registreringer samsvarer med disse filtrene i denne perioden.',sv:'Inga registreringar matchar dessa filter under denna period.',da:'Ingen registreringer matcher disse filtre i denne periode.',cs:'Žádné záznamy v tomto období neodpovídají těmto filtrům.',el:'Δεν υπάρχουν εγγραφές που να ταιριάζουν με αυτά τα φίλτρα σε αυτή την περίοδο.',hu:'Ebben az időszakban egyetlen bejegyzés sem felel meg ezeknek a szűrőknek.',lb:'Keng Opzeechnungen entspriechen dëse Filteren an dëser Period.',pl:'Żadne zapisy w tym okresie nie pasują do tych filtrów.',pt:'Nenhum registo corresponde a estes filtros neste período.',ro:'Nicio înregistrare din această perioadă nu corespunde acestor filtre.'};

export function periodLabel(meta,locale='en'){
 if(!meta)return '';
 const date=s=>new Date(`${s}T12:00:00Z`),format=(s,options)=>date(s).toLocaleDateString(locale,{...options,timeZone:'UTC'});
 if(meta.scope==='day')return format(meta.start_date,{day:'numeric',month:'long',year:'numeric'});
 if(meta.scope==='year')return meta.start_date.slice(0,4);
 if(meta.scope==='week'){
  const end=date(meta.end_date);end.setUTCDate(end.getUTCDate()-1);
  return format(meta.start_date,{day:'numeric',month:'short'})+' – '+end.toLocaleDateString(locale,{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'});
 }
 return format(meta.start_date,{month:'long',year:'numeric'});
}

export class NioDashboardHistory extends CarLedgerCard{
 constructor(){super();this.scope='month';this.anchor=null;this.full=true;this.pageSize=36;this._requestId=0;this._contextId=0;this._mutationId=0;this._notifiedMutationId=0;this._pendingWrites=0;this._savedRefreshPending=false;this.filters={location:'all',basis:'all',price:false};}
 get displayLocale(){return this.config?.language||this._hass?.language||'en';}
 translate(value){
  const text=String(value),used=text.match(/^(\s*)Verbruikt ([\d.,\s−-]+) (kWh)(\s*)$/);
  if(used)return `${used[1]}${super.translate('Verbruikt')} ${used[2]} ${used[3]}${used[4]}`;
  return super.translate(text);
 }
 date(ts,options={day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}){return ts?new Date(ts*1000).toLocaleString(this.displayLocale,{hour12:false,...options,timeZone:this._hass?.config?.time_zone||'UTC'}):'—';}
 monthKey(ts){return new Intl.DateTimeFormat('en-CA',{year:'numeric',month:'2-digit',timeZone:this._hass?.config?.time_zone||'UTC'}).format(new Date(ts*1000));}
 get ui(){const code=this.displayLocale.toLowerCase().split(/[-_]/)[0];return Object.fromEntries(UI_KEYS.map((key,i)=>[key,(UI_ROWS[code]||UI_ROWS.en)[i]]));}
 get emptyPeriodLabel(){const filtered=this.tab==='charging'&&(this.filters.location!=='all'||this.filters.price)||this.tab==='trips'&&this.filters.basis!=='all';const labels=filtered?EMPTY_FILTERS:EMPTY_PERIOD;return labels[this.displayLocale.toLowerCase().split(/[-_]/)[0]]||labels.en;}
 setConfig(config){
  const changed=this.config?.entry_id!==config.entry_id;this.config={...config};
  this.setAttribute?.('lang',this.displayLocale);
  if(changed){this._requestId++;this._contextId++;this._savedRefreshPending=false;this.snapshot=null;this.fullSnapshot=null;this.anchor=null;this.scope='month';this.filters={location:'all',basis:'all',price:false};}
  this.render();if(this._hass&&this.isConnected)this.refresh();
 }
 set hass(hass){
  this._hass=hass;
  if(this.isConnected&&!this.loading&&!this._pendingWrites&&(!this.fullSnapshot||Date.now()-(this._lastRefresh||0)>30000))this.refresh();
 }
 disconnectedCallback(){super.disconnectedCallback();this._requestId++;this._contextId++;this._savedRefreshPending=false;this.loading=false;}
 async refresh(afterSave=false){
  if(!this._hass||!this.config?.entry_id){if(afterSave||this._savedRefreshPending){this.error=this.savedRefreshCopy();this.refreshState();return 'failed';}return 'skipped';}
  const request=++this._requestId;this.loading=true;this.refreshState();
  try{
   const query={type:'nio_telematics/car_dashboard/get',entry_id:this.config.entry_id,period:this.scope};if(this.anchor)query.date=this.anchor;
   const raw=await this._hass.callWS(query);if(request!==this._requestId)return 'superseded';
   if(!raw.selected_period||!raw.statistics?.selected)throw new Error(this.translate('Rittenregistratie nog niet beschikbaar'));
   this.fullSnapshot=this.prepareSnapshot(raw);this.anchor=raw.selected_period.date;this._calendar=raw.selected_period;this._lastRefresh=Date.now();this.error='';this._savedRefreshPending=false;
   this.applyView();
   this.dispatchEvent(new CustomEvent('nio-history-updated',{bubbles:true,composed:true,detail:{entry_id:this.config.entry_id,snapshot:this.fullSnapshot}}));
   if(this.shadowRoot.querySelector('dialog[open]')){this._deferredRender=true;this.refreshState();}else this.render();
   return 'updated';
  }catch(error){if(request!==this._requestId)return 'superseded';this.error=afterSave||this._savedRefreshPending?this.savedRefreshCopy():this.localizeError(error,this.ui.loading);if(!this.snapshot)this.render();else this.refreshState();return 'failed';}
  finally{if(request===this._requestId){this.loading=false;this.refreshState();}}
 }
 async update(action,values){
  const entryId=this.config.entry_id,context=this._contextId,mutation=++this._mutationId;
  // A read started before this write must not replace the newly saved state.
  this._requestId++;this.loading=false;this.refreshState();
  this._pendingWrites++;
  try{
   const raw=await this._hass.callWS({type:'nio_telematics/car_dashboard/update',entry_id:entryId,action,values});
   if(context!==this._contextId||entryId!==this.config?.entry_id)return {saved:true,refreshed:false};
   this._savedRefreshPending=true;
   // UPDATE returns an ordinary snapshot. Car can consume it immediately, but
   // History needs a selected-period GET before applying its calendar filters.
   if(mutation>this._notifiedMutationId){this._notifiedMutationId=mutation;if(raw?.statistics)this.dispatchEvent(new CustomEvent('nio-history-updated',{bubbles:true,composed:true,detail:{entry_id:entryId,snapshot:raw}}));}
   const status=await this.refresh(true);
   return {saved:true,refreshed:status==='updated'};
  }finally{this._pendingWrites--;}
 }
 applyView(){
  if(!this.fullSnapshot)return;
  const data=JSON.parse(JSON.stringify(this.fullSnapshot)),p=data.selected_period;
  const inside=r=>Number.isFinite(r.end)&&r.end>=p.start&&r.end<p.end&&r.end<=p.effective_end;
  data.charges=data.charges.filter(inside);data.trips=data.trips.filter(inside);data.parked_periods=data.parked_periods.filter(inside);data.unaccounted_intervals=(data.unaccounted_intervals||[]).filter(inside);
  data.charging_daily=data.charging_daily.filter(r=>r.date>=p.start_date&&r.date<p.end_date);
  if(this.filters.location!=='all')data.charges=data.charges.filter(r=>r.category===this.filters.location);
  if(this.filters.price)data.charges=data.charges.filter(r=>r.cost_eur==null||!r.confirmed);
  if(this.filters.basis!=='all')data.trips=data.trips.filter(t=>(this.tripEnergy(t)!=null)===(this.filters.basis==='known'));
  for(const key of ['day','month','year'])data.statistics[key]=data.statistics.selected;
  this.snapshot=data;
 }
 render(){
  if(!this.config)return;
  if(!this.snapshot){
   const u=this.ui;
   this.shadowRoot.innerHTML=`<style>${CarLedgerCard.styles}${HISTORY_STYLE}</style><ha-card><div class="history-context"><div class="top"><nav class="main-tabs" aria-label="${this.esc(this.translate('Autohistoriek'))}">${[['charging',u.charging],['trips',u.trips],['insight',u.energy],['parked',u.parked]].map(([key,label])=>`<button type="button" data-tab="${key}" class="${this.tab===key?'selected':''}" aria-pressed="${this.tab===key}">${this.esc(label)}</button>`).join('')}</nav></div><nav class="history-scopes periods" style="--period-count:4" aria-label="${this.esc(this.ui.date)}">${['day','week','month','year'].map(key=>`<button type="button" data-scope="${key}" class="${this.scope===key?'selected':''}" aria-pressed="${this.scope===key}">${this.esc(u[key])}</button>`).join('')}</nav></div><p class="empty" role="status">${this.esc(this.translate(this.error||u.loading))}</p><button type="button" data-action="refresh" class="text">${this.esc(u.refresh)}</button></ha-card>`;
   this.shadowRoot.addEventListener('click',this._clickHandler ||= e=>this.click(e));this.refreshState();return;
  }
  this.applyView();this.full=true;super.render();
  const r=this.shadowRoot,u=this.ui;
  r.append(Object.assign(document.createElement('style'),{textContent:HISTORY_STYLE}));
  for(const b of r.querySelectorAll('.main-tabs button')){b.textContent=({charging:u.charging,trips:u.trips,insight:u.energy,parked:u.parked})[b.dataset.tab];}
  for(const b of r.querySelectorAll('[data-action=full]'))b.remove();
  for(const p of r.querySelectorAll('.periods'))if(p.querySelector('[data-period=day]'))p.remove();
  const top=r.querySelector('.top'),context=document.createElement('div');context.className='history-context';top.before(context);context.append(top);
  const scope=document.createElement('nav');scope.className='history-scopes periods';scope.style.setProperty('--period-count','4');scope.setAttribute('aria-label',this.ui.date);
  scope.innerHTML=['day','week','month','year'].map(key=>`<button type="button" data-scope="${key}" class="${this.scope===key?'selected':''}" aria-pressed="${this.scope===key}">${this.esc(u[key])}</button>`).join('');context.append(scope);
  const calendar=document.createElement('div');calendar.className='calendar-row';
  calendar.innerHTML=`<div class="date-group"><button class="arrow" data-shift="-1" aria-label="${this.esc(u.previous)}">${HISTORY_ICONS.left}</button><button class="date" data-calendar>${HISTORY_ICONS.calendar}<span>${this.esc(periodLabel(this._calendar,this.displayLocale))}</span></button><button class="arrow" data-shift="1" aria-label="${this.esc(u.next)}">${HISTORY_ICONS.right}</button></div><div class="date-tools"><button data-today>${this.esc(u.today)}</button>${['charging','trips'].includes(this.tab)?`<button class="arrow" data-filter aria-label="${this.esc(u.filters)}" aria-pressed="${this.filters.location!=='all'||this.filters.price||this.filters.basis!=='all'}">${HISTORY_ICONS.sliders}</button>`:''}</div>`;
  const refresh=r.querySelector('.refresh');refresh.innerHTML=HISTORY_ICONS.refresh;refresh.setAttribute('aria-label',u.refresh);calendar.querySelector('.date-tools').append(refresh);context.append(calendar);
  const heading=r.querySelector('.heading h2');if(heading)heading.textContent=({charging:u.charging,trips:u.trips,parked:u.parked})[this.tab]||heading.textContent;
  const add=r.querySelector('[data-action=add]');if(add)add.innerHTML=HISTORY_ICONS.plus;
  if(this.tab==='trips'){
   const counters=document.createElement('div');counters.className='counter-links';
   for(const c of this.snapshot.counters.slice(0,2)){const b=document.createElement('button');b.type='button';b.dataset.showCounter=c.id;b.textContent=`${c.name} · ${this.n(c.statistics.distance_km,0)} km`;counters.append(b);}r.querySelector('.heading').append(counters);
  }
  if(this.tab==='insight'){const title=document.createElement('h2');title.className='content-title';title.textContent=u.energy;r.querySelector('.insight').before(title);}
  const empty=r.querySelector('.empty');if(empty&&this.tab!=='insight')empty.textContent=this.emptyPeriodLabel;
  this.summaryGrids();
  for(const details of r.querySelectorAll('.details'))if(details.querySelector('.chart'))details.open=true;
  for(const label of r.querySelectorAll('.metric>span,.period-summary small')){
   if(this.displayLocale.startsWith('en')&&label.textContent==='Average consumption'){label.textContent='Avg. consumption';label.setAttribute('aria-label','Average consumption');}
  }
  r.querySelector('ha-card').classList.toggle('show-month-labels',this.scope==='year'||r.querySelectorAll('.month h3').length>1);
  this.refreshState();
 }
 summaryGrids(){
  const labels={charging:['Geladen','Laadkosten','Vergoeding','Laadvoordeel'],trips:['Afstand','Gem. verbruik','Ritten'],parked:['Verbruikt','Batterij']}[this.tab];if(!labels)return;
  const units={charging:['kWh',this.moneyUnit(this.currencyCode(this.snapshot.currency||'EUR')),this.moneyUnit(this.currencyCode(this.snapshot.currency||'EUR')),this.moneyUnit(this.currencyCode(this.snapshot.currency||'EUR'))],trips:['km','kWh/100 km',''],parked:['kWh','%']}[this.tab];
  for(const p of this.shadowRoot.querySelectorAll('.month p')){
   if(p.classList?.contains('currency-notice'))continue;
   const values=p.textContent.split(' · ');if(values.length>labels.length)continue;
   const grid=document.createElement('div');grid.className=`period-summary cols${values.length}`;
   for(let i=0;i<values.length;i++){
    const item=document.createElement('div'),label=document.createElement('small'),value=document.createElement('strong');label.textContent=this.translate(labels[i]);
    const text=values[i].trim(),match=text.match(/^([\d.,\s−—-]+)\s*(.*)$/),currency=text.match(/(?:€|\b[A-Z]{3}\b)/)?.[0];value.textContent=match?match[1].trim():text;
    if(match&&units[i]){const unit=document.createElement('span');unit.className='unit';unit.textContent=' '+(i>0&&i<4&&currency?currency:units[i]);value.append(unit);}
    item.append(label,value);grid.append(item);
   }p.replaceWith(grid);
  }
 }
 chargingGraph(){
  // Base graph already has the established known/unknown cost semantics. Its date
  // filter must see the selected calendar, not the browser's current month.
  const rows=this.snapshot.charging_daily;if(!rows.length)return '';
  const cost=this.graphUnit==='eur',mismatch=Number(this.snapshot.statistics?.selected?.currency_mismatch_count)>0,currency=this.currencyCode(this.snapshot.currency||'EUR'),max=Math.max(1,...rows.map(r=>cost?r.known_cost_eur:r.kwh));
  const bars=rows.map((r,i)=>{const w=300/rows.length,v=cost?(mismatch||Number(r.currency_mismatch_count)>0?null:r.known_cost_eur):r.kwh;return `<rect x="${i*w}" y="${95-(v||0)/max*80}" width="${Math.max(1,w-3)}" height="${(v||0)/max*80}" rx="2" opacity="${cost&&r.missing?.4:.9}"><title>${this.esc(r.date)}: ${cost?this.money(v,currency):`${this.n(v,2)} kWh`}</title></rect>`;}).join('');
  return `<div class="panel"><div class="row"><h3>${this.esc(this.ui.charging)}</h3><div class="segmented compact"><button data-unit="kwh" class="${cost?'':'selected'}">kWh</button><button data-unit="eur" class="${cost?'selected':''}">${this.esc(this.moneyUnit(currency))}</button></div></div>${cost&&mismatch?`<p class="muted">${this.currencyNotice('mixed')}</p>`:''}<div class="chart"><svg viewBox="0 0 300 100" role="img" aria-label="${this.esc(this.ui.charging)}"><g fill="var(--car-accent)">${bars}</g></svg><div class="row muted"><span>${this.esc(rows[0].date)}</span><span>${this.esc(rows.at(-1).date)}</span></div></div></div>`;
 }
 tripCard(t){const cap=this.snapshot.settings.capacity_kwh;return super.tripCard(t).replace(`${this.n(t.start_energy/cap*100,0)}% → ${this.n(t.end_energy/cap*100,0)}%`,`${this.n(t.start_energy/cap*100,1)}% → ${this.n(t.end_energy/cap*100,1)}%`);}
 dialog(...args){
  super.dialog(...args);const d=this.shadowRoot.querySelector('dialog');const close=d?.querySelector('[data-close]');if(close)close.innerHTML=HISTORY_ICONS.close;
  d?.addEventListener('close',()=>{if(this._deferredRender){this._deferredRender=false;this.render();}},{once:true});
 }
 async click(e){
  const b=e.target.closest('button');if(!b)return;
  if(b.dataset.tab){this.tab=b.dataset.tab;this.pageSize=36;this.period=['last_trip','current_trip','since_charge','last_100km'].includes(this.period)?this.period:this.scope==='week'?'month':this.scope;this.render();return;}
  if(b.dataset.scope){this.scope=b.dataset.scope;this.pageSize=36;this.period=this.scope==='week'?'month':this.scope;await this.refresh();return;}
  if(b.hasAttribute('data-shift')){this.pageSize=36;this.shift(Number(b.dataset.shift));await this.refresh();return;}
  if(b.hasAttribute('data-today')){this.pageSize=36;this.anchor=null;await this.refresh();return;}
  if(b.hasAttribute('data-calendar')){this.dateDialog();return;}
  if(b.hasAttribute('data-filter')){this.filterDialog();return;}
  if(b.dataset.showCounter){const c=this.snapshot.counters.find(c=>c.id===b.dataset.showCounter),stat=c?.statistics,currency=this.currencyCode(stat?.currency||this.snapshot.currency||'EUR');if(c)this.dialog(c.name,`<div class="metrics three">${this.value('Afstand',stat.distance_km,'km')}${this.value('Gem. verbruik',stat.consumption_kwh_100km,'kWh/100 km')}${this.value('Rijkosten',Number(stat.currency_mismatch_count)>0?null:stat.cost_eur_100km,`${this.moneyUnit(currency)}/100 km`,2)}</div>${Number(stat.currency_mismatch_count)>0?`<p class="muted">${this.currencyNotice('mixed')}</p>`:''}<button class="text" data-reset="${this.esc(c.id)}">${this.esc(this.translate('Reset'))}</button>`);return;}
  return super.click(e);
 }
 shift(step){
  const d=new Date(`${this._calendar.start_date}T12:00:00Z`);
  if(this.scope==='day'||this.scope==='week')d.setUTCDate(d.getUTCDate()+step*(this.scope==='week'?7:1));
  if(this.scope==='month')d.setUTCMonth(d.getUTCMonth()+step);
  if(this.scope==='year')d.setUTCFullYear(d.getUTCFullYear()+step);
  this.anchor=d.toISOString().slice(0,10);
 }
 dateDialog(){
  this.dialog(this.ui.chooseDate,`<label>${this.esc(this.ui.date)}<input name="date" type="date" value="${this.esc(this.anchor)}" required></label>`,async form=>{this.pageSize=36;this.anchor=form.get('date');await this.refresh();});
  const save=this.shadowRoot.querySelector('dialog .save');if(save)save.textContent=this.ui.apply;
 }
 filterDialog(){
  const u=this.ui;
  const field=this.tab==='charging'?`<label>${this.esc(this.translate('Locatie'))}<select name="location">${[['all',u.all],...['home','work','supercharger','other'].map(k=>[k,this.translate(this.category(k))])].map(([k,v])=>`<option value="${k}" ${this.filters.location===k?'selected':''}>${this.esc(v)}</option>`).join('')}</select></label><label class="filter-check"><input name="price" type="checkbox" ${this.filters.price?'checked':''}>${this.esc(u.priceMissing)}</label>`:`<label>${this.esc(u.trips)}<select name="basis">${[['all',u.all],['known',u.known],['missing',u.missing]].map(([k,v])=>`<option value="${k}" ${this.filters.basis===k?'selected':''}>${this.esc(v)}</option>`).join('')}</select></label>`;
  this.dialog(u.filters,field,async form=>{if(this.tab==='charging'){this.filters.location=form.get('location');this.filters.price=form.get('price')==='on';}else this.filters.basis=form.get('basis');this.applyView();this._deferredRender=true;});
  const save=this.shadowRoot.querySelector('dialog .save');if(save)save.textContent=u.apply;
 }
}
if(!customElements.get('nio-dashboard-history'))customElements.define('nio-dashboard-history',NioDashboardHistory);
