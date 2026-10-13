const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const elements = new Map();
const source = fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/nio-vehicle-card.js'), 'utf8');
vm.runInNewContext(source, {
  HTMLElement: class {},
  customElements: { get: name => elements.get(name), define: (name, cls) => elements.set(name, cls) },
  window: { customCards: [] },
});
const Dashboard = elements.get('nio-vehicle-dashboard');
const ledgerElements = new Map();
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/car_dashboard/car-ledger-card.js'), 'utf8'), {
  HTMLElement: class {},
  customElements: { get: name => ledgerElements.get(name), define: (name, cls) => ledgerElements.set(name, cls) },
  window: { customCards: [] },
});
const Ledger = ledgerElements.get('car-ledger-card');

function display(chargingState, connection, power) {
  const nodes = new Map();
  const root = {
    querySelector(selector) {
      if (selector === 'car-ledger-card') return null;
      if (!nodes.has(selector)) nodes.set(selector, { textContent: '', style: {}, setAttribute(name, value) { this[name] = value; } });
      return nodes.get(selector);
    },
  };
  const states = {
    soc: { state: '75' }, range: { state: '416' }, odo: { state: '6266' }, limit: { state: '90' },
    charging: { state: chargingState }, connected: { state: connection }, power: { state: power },
  };
  const card = {
    vehicle: { entities: { battery_state_of_charge: 'soc', remaining_range: 'range', odometer: 'odo', maximum_soc: 'limit', charging_state: 'charging' }, preferences: { evcc_connected: 'connected', evcc_power: 'power' } },
    shadowRoot: { querySelector: selector => selector === '.dashboard[data-entry-id]' ? root : null },
    words: { charging: 'Laden', connectedStatus: 'Verbonden', idle: 'Laadt niet', unavailable: 'Niet beschikbaar', power: 'Vermogen', limit: 'Laadlimiet' },
    state: id => states[id],
    number(id, digits = 0) { const value = Number(states[id]?.state); return Number.isFinite(value) ? value.toFixed(digits) : null; },
    stamp: () => '',
    _hass: {},
  };
  Dashboard.prototype.updateDisplay.call(card);
  return nodes;
}

test('a connected but idle EVCC car is not labelled charging', () => {
  const nodes = display('unknown', 'on', '0');
  assert.equal(nodes.get('[data-value="status"]').textContent, 'Laadt niet · Verbonden');
  assert.equal(nodes.get('[data-value="soc"]').textContent, '75%');
  assert.equal(nodes.get('[data-value="range"]').textContent, '416 km');
});

test('positive power means charging even when native state is sparse', () => {
  assert.equal(display('unknown', 'on', '4.2').get('[data-value="status"]').textContent, 'Laden · Verbonden');
});

test('no configured EVCC source falls back to native charge limit', () => {
  const nodes = display('not_charging', undefined, undefined);
  assert.equal(nodes.get('[data-value="status"]').textContent, 'Laadt niet');
  assert.equal(nodes.get('[data-label="third"]').textContent, 'Laadlimiet');
  assert.equal(nodes.get('[data-value="third"]').textContent, '90%');
});

test('history uses English outside Dutch HA and keeps Dutch for the owner', () => {
  const english = {config: {language: 'en'}, displayLocale: 'en'};
  const dutch = {config: {language: 'nl'}, displayLocale: 'nl'};
  assert.equal(Ledger.prototype.translate.call(english, 'Ritten'), 'Trips');
  assert.equal(Ledger.prototype.translate.call(english, 'Laden'), 'Charging');
  assert.equal(Ledger.prototype.translate.call(dutch, 'Ritten'), 'Ritten');
});

test('other NIO models use the approved NIO front icon, not a fabricated model image', () => {
  const html = Dashboard.prototype.carImage.call({esc: value => value}, 'EL6');
  assert.match(html, /class="car-placeholder"/);
  assert.doesNotMatch(html, /et5-touring-hero/);
});

test('automatic model detection prefers ET5 Touring over the shorter ET5 name', () => {
  const model = Dashboard.prototype.modelFor.call({config: {}}, {name: 'My ET5 Touring', preferences: {model: 'auto'}});
  assert.equal(model, 'ET5 Touring');
  const unknown = Dashboard.prototype.modelFor.call({config: {}}, {name: 'My car', preferences: {model: 'auto'}});
  assert.equal(unknown, 'NIO');
});
