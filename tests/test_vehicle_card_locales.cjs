const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/nio-vehicle-card.js'), 'utf8');
const context = {
  HTMLElement: class { attachShadow() { this.attributes = {}; this.shadowRoot = { querySelector() { return null; }, querySelectorAll() { return []; } }; } setAttribute(key, value) { this.attributes[key] = value; } },
  customElements: { get() { return undefined; }, define() {} },
  window: { customCards: [] },
  fetch: async () => ({ ok: true, json: async () => ({ schema_version: 1, selection: 'model_and_paint', models: [] }) }),
};
vm.runInNewContext(source + '\nglobalThis.__test = { NIO_SOURCE_HINT, NIO_INPUT_LABELS, NIO_EVCC_PROMPT, NIO_COST_INPUTS, NIO_FIELD_HELP, NIO_BACKUP_WORDS, NIO_BACKUP_TRANSPORT_ERROR, NIO_EXTRA, NIO_WORDS, NIO_DASHBOARD_UI, NIO_DASHBOARD_SOLAR, NIO_DASHBOARD_SETTINGS_INTRO, NIO_DASHBOARD_HISTORY_INTRO, NIO_DASHBOARD_RETAINED, NIO_DASHBOARD_RETRY, NIO_HELP_ARIA, NIO_ERROR_FALLBACK, NIO_LANGUAGE_NAMES, NIO_OTHER_MODEL, NIO_CHARGING_UNKNOWN, NIO_CONNECTED_STATUS, NioVehicleCard, NioVehicleDashboard, NioVehicleCardEditor };', context);
const maps = context.__test;
const locales = ['en', 'nl', 'de', 'fr', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro'];
const placeholders = value => (value.match(/\{[^{}]+\}/g) || []).sort().join('|');

test('all five setup and backup maps cover all 14 languages without English fallbacks', () => {
  const keys = Object.keys(maps.NIO_FIELD_HELP.en).sort();
  for (const name of ['NIO_SOURCE_HINT', 'NIO_EVCC_PROMPT', 'NIO_COST_INPUTS', 'NIO_FIELD_HELP', 'NIO_BACKUP_WORDS']) {
    assert.deepEqual(Object.keys(maps[name]).sort(), [...locales].sort(), name + ' locales');
  }
  for (const locale of locales) {
    assert.equal(maps.NIO_COST_INPUTS[locale].length, 6, locale + ' cost labels');
    assert.deepEqual(Object.keys(maps.NIO_FIELD_HELP[locale]).sort(), keys, locale + ' help keys');
    assert.equal(maps.NIO_BACKUP_WORDS[locale].length, 11, locale + ' backup labels');
    assert.deepEqual(maps.NIO_BACKUP_WORDS[locale].map(placeholders), maps.NIO_BACKUP_WORDS.en.map(placeholders), locale + ' backup placeholders');
    assert.equal(maps.NIO_EXTRA[locale].length, 4, locale + ' extra words');
    if (locale !== 'en') {
      assert.notEqual(maps.NIO_SOURCE_HINT[locale], maps.NIO_SOURCE_HINT.en, locale + ' source hint');
      assert.notEqual(maps.NIO_EVCC_PROMPT[locale], maps.NIO_EVCC_PROMPT.en, locale + ' EVCC prompt');
      for (let i = 0; i < 6; i++) assert.notEqual(maps.NIO_COST_INPUTS[locale][i], maps.NIO_COST_INPUTS.en[i], locale + ' cost label ' + i);
      for (const key of keys) assert.notEqual(maps.NIO_FIELD_HELP[locale][key], maps.NIO_FIELD_HELP.en[key], locale + ' help ' + key);
      for (let i = 0; i < 11; i++) assert.notEqual(maps.NIO_BACKUP_WORDS[locale][i], maps.NIO_BACKUP_WORDS.en[i], locale + ' backup label ' + i);
    }
  }
});

test('exact-text backup transport restart guidance covers every supported language', () => {
  assert.deepEqual(Object.keys(maps.NIO_BACKUP_TRANSPORT_ERROR).sort(), [...locales].sort());
  for (const locale of locales) assert.ok(maps.NIO_BACKUP_TRANSPORT_ERROR[locale].length > 30, locale);
});

test('every card locale map has complete per-language coverage and the right row shape', () => {
  const keyedMaps = ['NIO_SOURCE_HINT', 'NIO_INPUT_LABELS', 'NIO_EVCC_PROMPT', 'NIO_DASHBOARD_UI', 'NIO_DASHBOARD_SOLAR', 'NIO_DASHBOARD_SETTINGS_INTRO', 'NIO_DASHBOARD_HISTORY_INTRO', 'NIO_DASHBOARD_RETAINED', 'NIO_DASHBOARD_RETRY', 'NIO_HELP_ARIA', 'NIO_ERROR_FALLBACK', 'NIO_LANGUAGE_NAMES', 'NIO_OTHER_MODEL', 'NIO_CHARGING_UNKNOWN', 'NIO_CONNECTED_STATUS'];
  for (const name of keyedMaps) assert.deepEqual(Object.keys(maps[name]).sort(), [...locales].sort(), name + ' locale coverage');
  for (const name of ['NIO_WORDS', 'NIO_EXTRA', 'NIO_COST_INPUTS', 'NIO_DASHBOARD_UI']) {
    for (const locale of locales) assert.equal(maps[name][locale].length, maps[name].en.length, `${name}.${locale} row length`);
  }
  for (const locale of locales) {
    assert.equal(maps.NIO_INPUT_LABELS[locale].length, 3, locale + ' input labels');
    assert.equal(maps.NIO_FIELD_HELP[locale] && Object.keys(maps.NIO_FIELD_HELP[locale]).length, Object.keys(maps.NIO_FIELD_HELP.en).length, locale + ' help map');
    assert.ok(maps.NIO_DASHBOARD_HISTORY_INTRO[locale], locale + ' history intro');
    assert.ok(maps.NIO_ERROR_FALLBACK[locale], locale + ' localized error fallback');
  }
});

test('card settings words resolve localized source hints and native defaults', () => {
  for (const locale of locales) {
    const card = new maps.NioVehicleCard();
    card.config = { entry_id: 'entry' };
    card.vehicles = [{ entry_id: 'entry', preferences: { language: locale } }];
    const words = card.words;
    assert.equal(words.sourceHint, maps.NIO_SOURCE_HINT[locale]);
    assert.equal(words.nativeDefault, maps.NIO_EXTRA[locale][3]);
  }
});

test('dashboard copy, accessible help labels, and retry actions cover every supported locale', () => {
  for (const locale of locales) {
    assert.equal(maps.NIO_DASHBOARD_UI[locale].length, maps.NIO_DASHBOARD_UI.en.length, locale + ' dashboard labels');
    assert.ok(maps.NIO_DASHBOARD_RETRY[locale], locale + ' retry label');
    assert.ok(maps.NIO_HELP_ARIA[locale], locale + ' accessible help label');
    const dashboard = new maps.NioVehicleDashboard();
    dashboard.config = { language: locale };
    assert.equal(dashboard.words.retry, maps.NIO_DASHBOARD_RETRY[locale], locale + ' dashboard retry');
    assert.equal(dashboard.words.errorFallback, maps.NIO_ERROR_FALLBACK[locale], locale + ' error fallback');
    assert.equal(JSON.stringify(dashboard.words.dashboardUI), JSON.stringify(maps.NIO_DASHBOARD_UI[locale]), locale + ' dashboard language');
    const card = new maps.NioVehicleCard();
    card.vehicles = [{ preferences: { language: locale } }];
    assert.match(card.fieldHelp('vehicle', locale), new RegExp(`aria-label="${maps.NIO_HELP_ARIA[locale]}"`), locale + ' help aria');
  }
});

test('regional HA language tags resolve translated copy while preserving a valid Intl locale', () => {
  const card = new maps.NioVehicleCard();
  card._hass = { language: 'nl_BE' };
  card.vehicles = [{ preferences: { language: 'auto' } }];
  assert.equal(card.locale(), 'nl-BE');
  assert.equal(card.words.range, maps.NIO_WORDS.nl[1]);
  assert.doesNotThrow(() => new Intl.NumberFormat(card.locale()).format(1234.5));
  card.markLocalizationRoot();
  assert.equal(card.attributes['data-i18n-ignore'], '');
  assert.equal(card.attributes.translate, 'no');
  assert.equal(card.attributes.lang, 'nl-BE');
  const dashboard = new maps.NioVehicleDashboard();
  dashboard.config = { language: 'pt_PT' };
  assert.equal(dashboard.locale(), 'pt-PT');
  assert.equal(dashboard.words.range, maps.NIO_WORDS.pt[1]);
  assert.doesNotThrow(() => new Intl.DateTimeFormat(dashboard.locale()).format(new Date('2026-11-24T12:00:00Z')));
  card._hass.language = 'no_NO';
  assert.equal(card.locale(), 'nb-NO');
  assert.equal(card.words.range, maps.NIO_WORDS.nb[1]);
  card._hass.language = 'es-ES';
  assert.equal(card.locale(), 'en');
  assert.equal(card.words.range, maps.NIO_WORDS.en[1]);
  assert.doesNotThrow(() => new Intl.NumberFormat(card.locale()).format(1234.5));
});

test('language picker uses native language names and translates Other model', () => {
  assert.deepEqual(Object.values(maps.NIO_LANGUAGE_NAMES).sort(), ['Čeština','Dansk','Deutsch','English','Français','Ελληνικά','Lëtzebuergesch','Magyar','Nederlands','Norsk bokmål','Polski','Português','Română','Svenska'].sort());
  for (const locale of locales) assert.ok(maps.NIO_OTHER_MODEL[locale], locale + ' other model');
  assert.match(source, /NIO_LANGUAGE_NAMES\[m\]\|\|m/);
  assert.match(source, /NIO_OTHER_MODEL\[inputLanguage\]/);
});

test('vehicle load failures show a localized summary instead of the raw backend error', async () => {
  const card = new maps.NioVehicleCard();
  card._hass = { language: 'nl_BE', callWS: async () => { throw new Error('English backend traceback'); } };
  card.render = () => {};
  card.refreshArtwork = () => {};
  await card.load();
  assert.equal(card.error, maps.NIO_ERROR_FALLBACK.nl);
  assert.doesNotMatch(card.error, /English backend traceback/);
  for (const locale of locales) {
    card.vehicles = [{ preferences: { language: locale } }];
    assert.equal(card.serviceErrorSummary(new Error('Unsupported preview request: nio_telematics/vehicle_dashboard/save')), maps.NIO_ERROR_FALLBACK[locale], locale + ' unknown service error');
    assert.equal(card.serviceErrorSummary(new Error('Confirm the restore after reviewing its preview'), locale, { 'Confirm the restore after reviewing its preview': maps.NIO_BACKUP_WORDS[locale][8] }), maps.NIO_BACKUP_WORDS[locale][8], locale + ' known translated service error');
  }
});

test('known broken localized backup terms describe trips and charging sessions', () => {
  assert.match(maps.NIO_BACKUP_WORDS.cs[4], /jízd/);
  assert.match(maps.NIO_BACKUP_WORDS.cs[4], /nabíjecích relací/);
  assert.match(maps.NIO_BACKUP_WORDS.hu[4], /utazást/);
  assert.match(maps.NIO_BACKUP_WORDS.hu[4], /töltési alkalmat/);
  assert.match(maps.NIO_BACKUP_WORDS.pl[4], /przejazdów/);
  assert.match(maps.NIO_BACKUP_WORDS.pl[4], /sesji ładowania/);
  assert.doesNotMatch(maps.NIO_BACKUP_WORDS.nb[4], /\bBackup\b|\bkostnader\b/);
});

test('artwork catalogue is retained while detached and rendered when the loaded card attaches', async () => {
  const card = new maps.NioVehicleCard();
  const catalogue = { schema_version: 1, selection: 'model_and_paint', models: [] };
  card.loaded = true;
  card.isConnected = false;
  card.refreshArtwork();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.equal(card.artworkCatalogue.schema_version, 1);
  let renders = 0;
  card.render = () => { renders++; };
  card.isConnected = true;
  card.connectedCallback();
  assert.equal(renders, 1);
  card.shadowRoot.querySelector = selector => selector === 'dialog[open]' ? {} : null;
  card.connectedCallback();
  assert.equal(renders, 1, 'open dialogs are left in place');
  assert.ok(catalogue);
});


test('HA translation catalogues include every paint selector option with localized automatic', () => {
  const root = path.join(__dirname, '../custom_components/nio_telematics');
  const source = JSON.parse(fs.readFileSync(path.join(root, 'strings.json'), 'utf8'));
  const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'artwork/catalogue.json'), 'utf8'));
  const paintNames = new Map();
  for (const model of catalogue.models) for (const paint of model.paints) paintNames.set(paint.id, paint.label);
  const expectedKeys = ['auto', ...paintNames.keys()].sort();
  assert.deepEqual(Object.keys(source.selector.paint.options).sort(), expectedKeys);
  const flatten = (value, prefix = '', result = {}) => {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      for (const [key, child] of Object.entries(value)) flatten(child, prefix ? prefix + '.' + key : key, result);
    } else result[prefix] = value;
    return result;
  };
  const base = flatten(source);
  const slots = value => typeof value === 'string' ? (value.match(/\{[^{}]+\}/g) || []).sort().join('|') : '';
  for (const locale of locales) {
    const translated = JSON.parse(fs.readFileSync(path.join(root, 'translations', locale + '.json'), 'utf8'));
    const leaves = flatten(translated);
    assert.deepEqual(Object.keys(leaves).sort(), Object.keys(base).sort(), locale + ' translation leaf parity');
    for (const key of Object.keys(base)) assert.equal(slots(leaves[key]), slots(base[key]), locale + ' placeholder parity: ' + key);
    const options = translated.selector.paint.options;
    assert.deepEqual(Object.keys(options).sort(), expectedKeys, locale + ' paint option keys');
    if (locale !== 'en') assert.notEqual(options.auto, source.selector.paint.options.auto, locale + ' automatic label');
    for (const [id, label] of paintNames) assert.equal(options[id], label, locale + ' official colour name ' + id);
  }
});

test('native setup copy preserves product names and uses the correct range and charging terms', () => {
  const root = path.join(__dirname, '../custom_components/nio_telematics/translations');
  const expectations = {
    cs: ['Dojezd', /dojezdu/],
    hu: ['Hátralévő hatótáv', /hatótáv/i],
    pl: ['Pozostały zasięg', /zasięgu/],
    pt: ['Autonomia restante', /autonomia/],
    ro: ['Autonomie rămasă', /autonomiei/],
  };
  for (const [locale, [rangeLabel, rangeTerm]] of Object.entries(expectations)) {
    const translated = JSON.parse(fs.readFileSync(path.join(root, locale + '.json'), 'utf8'));
    assert.match(translated.config.step.user.description, /Direct NIO/ , locale + ' Direct NIO brand');
    assert.match(translated.config.step.user.description, /Home Assistant/, locale + ' Home Assistant brand');
    assert.match(translated.config.step.user.description, /Companion/, locale + ' Companion brand');
    assert.match(translated.config.step.user.menu_options.companion, /Companion/, locale + ' Companion selector');
    assert.match(translated.options.step.init.data.language, /Home Assistant/, locale + ' language setting');
    assert.equal(translated.entity.sensor.remaining_range.name, rangeLabel, locale + ' sensor range');
    assert.match(translated.options.step.init.data.range_entity, rangeTerm, locale + ' range setting');
    assert.ok(!/\b(artwork|műalkotás|tartomány|zakres|faixa|interval)\b/i.test(translated.options.step.init.data.range_entity), locale + ' no mistranslated range');
  }
});


test('the actual compact editor renders safely and updates its localized UI', async () => {
  const editor=new maps.NioVehicleCardEditor();
  assert.deepEqual(editor.attributes,{},'custom-element construction must not gain host attributes');
  assert.doesNotThrow(()=>editor.setConfig({entry_id:'example'}));
  editor._hass={language:'nl_BE',callWS:async()=>({vehicles:[{entry_id:'example',name:'Home & Range <Auto>'}]})};
  await editor.load();
  assert.equal(editor.attributes.lang,'nl-BE');
  assert.ok(editor.shadowRoot.innerHTML.includes('Home &amp; Range &lt;Auto&gt;'));
  editor.hass={...editor._hass,language:'fr'};
  assert.equal(editor.attributes.lang,'fr');
  assert.ok(editor.shadowRoot.innerHTML.includes(maps.NIO_WORDS.fr[21]));
  editor.loaded=false;editor._hass={language:'nl',callWS:async()=>{throw Error('Server exploded in English');}};
  await editor.load();
  assert.ok(editor.shadowRoot.innerHTML.includes('role="alert"'));
  assert.ok(editor.shadowRoot.innerHTML.includes(maps.NIO_ERROR_FALLBACK.nl));
  assert.ok(!editor.shadowRoot.innerHTML.includes('Server exploded'));
});
