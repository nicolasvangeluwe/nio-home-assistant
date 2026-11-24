const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const rawSource = fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/car_dashboard/car-ledger-card.js'), 'utf8');
const source = rawSource.replaceAll('import.meta.url', JSON.stringify('https://ha.test/nio_telematics/car-dashboard.js')).replace('export { CarLedgerCard };', '');
const sandbox = {
  URL,
  HTMLElement: class { constructor() { this.attributes = {}; } setAttribute(k, v) { this.attributes[k] = v; } addEventListener() {} attachShadow() {} },
  customElements: { get() { return undefined; }, define() {} },
  document: { addEventListener() {}, removeEventListener() {}, createTreeWalker(root) { let used = false; return { nextNode() { if (used) return null; used = true; return root.node; } }; }, hidden: false },
  NodeFilter: { SHOW_TEXT: 4 },
  window: { customCards: [] },
};
vm.runInNewContext(source + '\nglobalThis.__CarLedgerCard = CarLedgerCard; globalThis.__LEDGER_TRANSLATIONS = LEDGER_TRANSLATIONS; globalThis.__LEDGER_ENGLISH = LEDGER_ENGLISH; globalThis.__LEDGER_DYNAMIC = LEDGER_DYNAMIC;', sandbox);
const CarLedgerCard = sandbox.__CarLedgerCard;
const translations = sandbox.__LEDGER_TRANSLATIONS;
const dynamic = sandbox.__LEDGER_DYNAMIC;
test('owned history import cannot patch an existing household card', () => {
  class ExistingCard {}
  ExistingCard.styles = 'household styles';
  const original = Object.getOwnPropertyDescriptors(ExistingCard.prototype);
  const cards = [];
  let registered = false;
  vm.runInNewContext(rawSource.replaceAll('import.meta.url', JSON.stringify('https://ha.test/nio_telematics/car-dashboard.js?nio_owned=1')).replace('export { CarLedgerCard };', ''), {
    URL, HTMLElement: class {}, customElements: { get: () => ExistingCard, define: () => { registered = true; } }, window: { customCards: cards },
  });
  assert.deepEqual(Object.getOwnPropertyDescriptors(ExistingCard.prototype), original);
  assert.equal(ExistingCard.styles, 'household styles');
  assert.equal(registered, false);
  assert.equal(cards.length, 0);
});
const locales = ['en', 'nl', 'fr', 'de', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro'];
function card(language) { const instance = new CarLedgerCard(); instance.config = { language }; return instance; }

test('ledger host owns localization and opts out of the household DOM translator', () => {
  const instance = card('en');
  instance.connectedCallback();
  assert.equal(instance.attributes['data-i18n-ignore'], '');
  assert.equal(instance.attributes.translate, 'no');
});

for (const locale of locales) {
  test(locale + ' has localized ledger labels and keeps the selected language', () => {
    const instance = card(locale);
    const expected = locale === 'nl' ? 'Laden' : locale === 'en' ? 'Charging' : translations[locale].Laden;
    assert.equal(instance.translate('Laden'), expected);
    assert.equal(instance.translate('Meer tonen (5)'), locale === 'nl' ? 'Meer tonen (5)' : (translations[locale]?.['Meer tonen'] || 'Show more') + ' (5)');
    assert.equal(instance.translate('5 ritten'), locale === 'nl' ? '5 ritten' : '5 ' + (translations[locale]?.Ritten || 'Trips').toLocaleLowerCase(locale));
  });

  test(locale + ' translates every complete ledger source phrase without substring fallback', () => {
    const instance = card(locale);
    for (const sourcePhrase of Object.keys(sandbox.__LEDGER_ENGLISH)) {
      const expected = locale === 'nl' ? sourcePhrase : locale === 'en'
        ? sandbox.__LEDGER_ENGLISH[sourcePhrase]
        : translations[locale]?.[sourcePhrase];
      assert.equal(typeof expected, 'string', locale + ' missing exact source phrase: ' + sourcePhrase);
      assert.notEqual(expected, '', locale + ' has an empty translation for: ' + sourcePhrase);
      assert.equal(instance.translate(sourcePhrase), expected, locale + ' phrase: ' + sourcePhrase);
    }
    for (const dynamicText of ['Verbruiktin', 'This is not a trip', 'VerbruiktTrip A', 'EVCC-Home-12']) {
      assert.equal(instance.translate(dynamicText), dynamicText, locale + ' preserves unknown/user text: ' + dynamicText);
    }
    assert.equal(instance.translate('Home'), 'Home', locale + ' preserves user-supplied names');
    assert.equal(instance.translate('record-rit-123'), 'record-rit-123', locale + ' preserves identifiers');
    assert.equal(instance.translate('  Verbruikt 0.45 kWh  '), '  Verbruikt 0.45 kWh  ', locale + ' does not alter an unrecognized dynamic sentence');
  });
}

test('Dutch remains the source language and English retains its previous labels', () => {
  assert.equal(card('nl-BE').translate('Autohistoriek'), 'Autohistoriek');
  assert.equal(card('en-US').translate('Autohistoriek'), 'Vehicle history');
});

test('dynamic ledger explanations keep values and replace template placeholders', () => {
  const text = 'Verbruik: 72 kWh × verschil in berekende SoC. Rijkosten gebruiken de gemiddelde prijs van de energie in de batterij. Thuis telt de EVCC-waarde mee, inclusief misgelopen teruglevering. Laadverliezen zijn niet afzonderlijk gemeten.';
  for (const locale of ['en', 'fr', 'de', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro']) {
    const value = card(locale).translate(text);
    assert.match(value, /72/);
    assert.doesNotMatch(value, /\{capacity\}/);
    assert.notEqual(value, text);
  }
  const trip = 'Kilometerstand 101 → 125 km. Tijden volgen de ontvangen metingen. Verbruik is geschat uit batterijmetingen met 75 kWh bruikbare capaciteit. Afname zonder kilometerverandering telt afzonderlijk als stilstandsverlies. Energie ontbreekt door ontbrekende metingen of tussentijds laden.';
  const value = card('fr').translate(trip);
  assert.match(value, /101/);
  assert.match(value, /125/);
  assert.match(value, /75/);
  assert.doesNotMatch(value, /\{(?:start|end|capacity|unknown)\}/);
  assert.equal(dynamic.fr.battery.includes('{capacity}'), true);
});

test('backend errors resolve through the current locale and unknown errors use a localized fallback', () => {
  const knownEnglish = 'The first trip appears after the car reports new readings.';
  const french = card('fr');
  assert.equal(french.translate(french.localizeError(new Error(knownEnglish))), translations.fr['De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.']);
  const unknown = new Error('HTTP 502 upstream payload: secret diagnostic text');
  assert.equal(french.localizeError(unknown), 'La demande a échoué. Veuillez réessayer.');
  assert.notEqual(french.localizeError(unknown), unknown.message);
  assert.equal(card('en').localizeError(unknown), 'The request failed. Please try again.');
});

test('rendered dynamic captions and summaries use locale templates and retain user text', () => {
  for (const locale of locales) {
    const instance = card(locale);
    const charge = instance.translate('Vergoeding 12.50 € · 35% zon');
    const missing = instance.translate(instance.missingNoticeText({missing_prices:2,unconfirmed_charges:0,known_spend_eur:4.75}));
    const missingOne = instance.translate(instance.missingNoticeText({missing_prices:1,unconfirmed_charges:0,known_spend_eur:0}));
    const unconfirmedOnly = instance.translate(instance.missingNoticeText({missing_prices:0,unconfirmed_charges:1,known_spend_eur:0}));
    const both = instance.translate(instance.missingNoticeText({missing_prices:2,unconfirmed_charges:1,known_spend_eur:4.75}));
    const missingTrip = instance.translate('78% → 72% · Meting ontbreekt');
    const average = instance.translate('Gem. 24.5 kWh/100 km');
    if (locale === 'nl') {
      assert.equal(charge, 'Vergoeding 12.50 € · 35% zon');
      assert.equal(missing, 'Ontbrekende prijzen: 2 · Bekende kosten: 4,75 €');
      assert.equal(missingOne, 'Ontbrekende prijzen: 1 · Bekende kosten: 0,00 €');
      assert.equal(unconfirmedOnly, 'Niet-bevestigde sessies: 1 · Bekende kosten: 0,00 €');
      assert.equal(both, 'Ontbrekende prijzen: 2 · Niet-bevestigde sessies: 1 · Bekende kosten: 4,75 €');
      assert.equal(missingTrip, '78% → 72% · Meting ontbreekt');
      assert.equal(average, 'Gem. 24.5 kWh/100 km');
    } else for (const value of [charge, missing, missingOne, unconfirmedOnly, both, missingTrip, average]) assert.doesNotMatch(value, /\{(?:count|amount|missing|unconfirmed)\}|Vergoeding|Ontbrekende prijzen|Niet-bevestigde sessies|Bekende kosten|Meting ontbreekt|Gem\. 24/ , locale + ' leaves source text in ' + value);
    assert.match(charge, /12\.50/); assert.match(charge, /35%/);
    assert.match(missing, /2/); assert.match(missing, /4[.,]75/);
    assert.match(missingOne, /1/); assert.match(missingOne, /0[.,]00/);
    assert.match(unconfirmedOnly, /1/); assert.match(both, /2/); assert.match(both, /1/);
    assert.match(missingTrip, /78%/); assert.match(missingTrip, /72%/);
    assert.match(average, /24\.5 kWh\/100 km/);
    assert.match(instance.counterResetPrompt('Laden'), /data-user-content translate="no">Laden<\/span>/, locale + ' preserves a counter name that matches a translation source');
    assert.match(instance.chartDate('2026-11-23'), /23/, locale + ' formats chart dates');
    assert.ok(instance.translate('Berekende energie'), locale + ' estimated-energy label');
  }
});

test('actual rendered monthly history totals localize charging, home-charge and trip summaries', () => {
  const locales=['en','nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro'];
  const start=Date.parse('2026-11-22T12:00:00Z')/1000;
  for(const locale of locales){
    const instance=card(locale);instance.full=true;instance.pageSize=30;instance.chargeCard=()=>'<article></article>';instance.tripCard=()=>'<article></article>';
    instance.tab='charging';instance.snapshot={charges:[{start,category:'home',confirmed:true,kwh:12,cost_eur:4,reimbursement_eur:2,benefit_eur:1}]};
    const chargeHtml=instance.history(),chargeSource=chargeHtml.match(/<p>(.*?)<\/p>/)[1];
    const charge=instance.translate(chargeSource);
    assert.match(charge,/12(?:[.,]00)? kWh/);assert.match(charge,/4(?:[.,]00)? €/);assert.match(charge,/2(?:[.,]00)? €/);assert.match(charge,/1(?:[.,]00)? €/);
    if(locale!=='nl')assert.doesNotMatch(charge,/laadkosten|vergoeding|laadvoordeel/);
    instance.tab='trips';instance.snapshot={trips:[{end:start,distance_km:8,segments:[]}]};instance.drivingStats=()=>({consumption_kwh_100km:23.5});
    const tripHtml=instance.history(),tripSource=tripHtml.match(/<p>(.*?)<\/p>/)[1];
    const trip=instance.translate(tripSource);assert.match(trip,/8(?:[.,]0)? km/);assert.match(trip,/23[.,]5 kWh\/100 km/);assert.match(trip,/1/);
    if(locale!=='nl')assert.doesNotMatch(trip,/ritten/);
  }
});

test('actual ongoing home-charge history row localizes its live label and solar-only suffix', () => {
  const locales=['en','nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro'];
  const start=Date.parse('2026-11-24T13:08:00Z')/1000;
  for(const locale of locales){
    const instance=card(locale);instance.full=false;instance.pageSize=30;instance.tab='charging';
    instance.snapshot={charges:[{id:'live-charge',start,ongoing:true,category:'home',kwh:8.4,cost_eur:null,confirmed:false,benefit_eur:null,reimbursement_eur:null,solar_pct:97}]};
    const html=instance.history();
    const timeSource=html.match(/class="row session-head"><span>(.*?)<\/span>/)[1];
    const solarSource=html.match(/class="muted">(.*?)<\/div>/)[1];
    assert.match(timeSource,/Lopende sessie$/,locale+' history renderer includes live state');
    assert.match(solarSource,/· 97% zon$/,locale+' home row has solar without reimbursement');
    const time=instance.translate(timeSource),solar=instance.translate(solarSource);
    assert.match(time,new RegExp(instance.translate('Lopende sessie')+'$'),locale+' live state translated');
    assert.match(solar,/97%/);
    if(locale!=='nl'){assert.doesNotMatch(time,/Lopende sessie/);assert.doesNotMatch(solar,/zon/);assert.notEqual(solar,solarSource,locale+' solar label translated');}
  }
});

test('localize skips user-supplied names but still translates surrounding static labels', () => {
  const instance = card('en');
  const marked = { textContent: 'Laden', parentElement: { closest: selector => selector.includes('data-user-content') ? {} : null } };
  const ordinary = { textContent: 'Laden', parentElement: { closest: () => null } };
  instance.localize({ node: marked, querySelectorAll: () => [] });
  assert.equal(marked.textContent, 'Laden');
  instance.localize({ node: ordinary, querySelectorAll: () => [] });
  assert.equal(ordinary.textContent, 'Charging');
});

test('rendered ledger source extraction finds static labels outside the translation catalogue', () => {
  const phrases = new Set();
  for (const match of rawSource.matchAll(/this\.(?:value|dialog|translate)\(\s*['"]([^'"\n]+)['"]/g)) phrases.add(match[1]);
  for (const match of rawSource.matchAll(/<(?:h[1-6]|p|summary|button|label|span|strong|small|option|title)\b[^>]*>([^<$]*)<\/(?:h[1-6]|p|summary|button|label|span|strong|small|option|title)>/g)) {
    const phrase = match[1].replace(/<[^>]*>/g, '').trim();
    if (/[A-Za-zÀ-ÿ]/.test(phrase) && !/[{}]/.test(phrase)) phrases.add(phrase);
  }
  const missing = [...phrases].filter(phrase => !/^(?:[\d.,]+\s*km|kWh|×)$/.test(phrase) && !Object.hasOwn(sandbox.__LEDGER_ENGLISH, phrase));
  assert.deepEqual(missing, [], 'visible static source phrases need explicit translations');
});


test('HA locale JSON files match English keys and placeholders', () => {
  const directory = path.join(__dirname, '../custom_components/nio_telematics/translations');
  const english = JSON.parse(fs.readFileSync(path.join(directory, 'en.json'), 'utf8'));
  function flatten(value, prefix = '', result = {}) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      for (const [key, child] of Object.entries(value)) flatten(child, prefix ? prefix + '.' + key : key, result);
    } else result[prefix] = value;
    return result;
  }
  const baseline = flatten(english);
  const placeholders = value => typeof value === 'string' ? (value.match(/\{[^{}]+\}/g) || []).sort().join('|') : '';
  for (const locale of locales) {
    const translated = flatten(JSON.parse(fs.readFileSync(path.join(directory, locale + '.json'), 'utf8')));
    assert.deepEqual(Object.keys(translated).sort(), Object.keys(baseline).sort(), locale + ' leaf keys');
    for (const key of Object.keys(baseline)) assert.equal(placeholders(translated[key]), placeholders(baseline[key]), locale + ' placeholders at ' + key);
  }
  for (const locale of locales.filter(locale => locale !== 'en')) {
    const translated = JSON.parse(fs.readFileSync(path.join(directory, locale + '.json'), 'utf8'));
    assert.notEqual(translated.config.step.user.title, english.config.step.user.title, locale + ' sample is translated');
    assert.notEqual(translated.options.step.init.data.paint, english.options.step.init.data.paint, locale + ' paint sample is translated');
  }
});
