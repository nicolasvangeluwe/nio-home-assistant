const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/nio-vehicle-card.js'), 'utf8');
const context = {
  HTMLElement: class { attachShadow() { this.shadowRoot = { querySelector() { return null; }, querySelectorAll() { return []; } }; } },
  customElements: { get() { return undefined; }, define() {} },
  window: { customCards: [] },
  fetch: async () => ({ ok: true, json: async () => ({ schema_version: 1, selection: 'model_and_paint', models: [] }) }),
};
vm.runInNewContext(source + '\nglobalThis.__test = { NIO_SOURCE_HINT, NIO_EVCC_PROMPT, NIO_COST_INPUTS, NIO_FIELD_HELP, NIO_BACKUP_WORDS, NIO_EXTRA, NIO_WORDS, NioVehicleCard, NioVehicleDashboard };', context);
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
