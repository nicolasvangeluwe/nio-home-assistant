const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/car_dashboard/car-ledger-card.js'), 'utf8');
const sandbox = {
  HTMLElement: class { attachShadow() {} },
  customElements: { get() { return undefined; }, define() {} },
  window: { customCards: [] },
};
vm.runInNewContext(source + '\nglobalThis.__CarLedgerCard = CarLedgerCard; globalThis.__LEDGER_TRANSLATIONS = LEDGER_TRANSLATIONS; globalThis.__LEDGER_DYNAMIC = LEDGER_DYNAMIC;', sandbox);
const CarLedgerCard = sandbox.__CarLedgerCard;
const translations = sandbox.__LEDGER_TRANSLATIONS;
const dynamic = sandbox.__LEDGER_DYNAMIC;
const locales = ['en', 'nl', 'fr', 'de', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro'];
function card(language) { const instance = new CarLedgerCard(); instance.config = { language }; return instance; }

for (const locale of locales) {
  test(locale + ' has localized ledger labels and keeps the selected language', () => {
    const instance = card(locale);
    const expected = locale === 'nl' ? 'Laden' : locale === 'en' ? 'Charging' : translations[locale].Laden;
    assert.equal(instance.translate('Laden'), expected);
    assert.equal(instance.translate('Meer tonen (5)'), locale === 'nl' ? 'Meer tonen (5)' : (translations[locale]?.['Meer tonen'] || 'Show more') + ' (5)');
    assert.equal(instance.translate('5 ritten'), locale === 'nl' ? '5 ritten' : '5 ' + (translations[locale]?.Ritten || 'Trips').toLocaleLowerCase(locale));
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
