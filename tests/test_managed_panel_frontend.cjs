const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(
  require('node:path').join(__dirname, '../custom_components/nio_telematics/nio-vehicle-panel.js'),
  'utf8',
);

class FakeNode {
  constructor(tag = 'div') {
    this.tagName = tag;
    this.children = [];
    this.attributes = {};
    this.listeners = {};
    this.hidden = false;
    this.value = '';
    this.textContent = '';
    this.className = '';
    this.isConnected = true;
  }
  append(node) { this.children.push(node); }
  replaceChildren(...nodes) { this.children = nodes; }
  remove() { this.removed = true; }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener(name, handler) { this.listeners[name] = handler; }
  emit(name) { this.listeners[name]?.({ target: this }); }
  querySelector(selector) {
    if (selector === 'label') return this.label;
    if (selector === 'select') return this.select;
    return null;
  }
}

class FakeCard extends FakeNode {
  constructor() { super('nio-vehicle-dashboard'); }
  setConfig(config) { this.config = config; }
}

function setup({
  vehicles = [],
  importFails = false,
  entryIds = ['car-1', 'car-2'],
  pending = false,
  cardFails = false,
} = {}) {
  const elements = new Map([['nio-vehicle-dashboard', FakeCard]]);
  const imported = [];
  const menu = new FakeNode('ha-menu-button');
  const label = new FakeNode('label');
  const select = new FakeNode('select');
  const selector = new FakeNode('div');
  selector.label = label;
  selector.select = select;
  const status = new FakeNode('div');
  const cardHost = new FakeNode('div');
  const nodes = new Map([
    ['ha-menu-button', menu],
    ['.selector', selector],
    ['.status', status],
    ['.card-host', cardHost],
    ['select', select],
  ]);
  class FakeHTMLElement {
    constructor() {
      this.isConnected = true;
      this.shadowRoot = {
        innerHTML: '',
        querySelector: (key) => nodes.get(key) || null,
      };
    }
    attachShadow() { return this.shadowRoot; }
  }
  const customElements = {
    get: (name) => elements.get(name),
    define: (name, component) => elements.set(name, component),
  };
  const document = {
    createElement: (tag) => {
      if (tag !== 'nio-vehicle-dashboard') return new FakeNode(tag);
      const card = new FakeCard();
      if (cardFails) card.setConfig = () => { throw new Error('invalid card configuration'); };
      return card;
    },
  };
  const context = {
    HTMLElement: FakeHTMLElement,
    customElements,
    document,
    Set,
    Promise,
    __dynamicImport: async (specifier) => {
      imported.push(specifier);
      if (importFails) throw new Error('module unavailable');
    },
  };
  vm.runInNewContext(
    source.replace('import(moduleUrl)', 'globalThis.__dynamicImport(moduleUrl)'),
    context,
  );
  const Panel = elements.get('nio-vehicle-panel');
  const panel = new Panel();
  const config = {
    owner: 'nio_telematics',
    schema_version: 1,
    entry_ids: entryIds,
    vehicle_card_url: '/nio_telematics/nio-vehicle-card.js?v=card-hash',
    history_url: '/nio_telematics/nio-dashboard-history.js?v=history-hash&base_version=base-hash',
    history_base_url: '/nio_telematics/car-dashboard.js?nio_owned=1&v=base-hash',
  };
  let wsCalls = 0;
  let resolveVehicles;
  const hass = {
    language: 'en',
    callWS: async () => {
      wsCalls += 1;
      if (pending) return new Promise((resolve) => { resolveVehicles = resolve; });
      return { vehicles };
    },
  };
  panel.panel = { config };
  panel.narrow = true;
  panel.route = { path: '/nio' };
  panel.hass = hass;
  return {
    panel, config, hass, nodes, menu, selector, select, status, cardHost, imported,
    get wsCalls() { return wsCalls; },
    resolveVehicles,
  };
}

const tick = () => new Promise((resolve) => setTimeout(resolve, 0));

test('repeated HA panel assignment does not reintroduce a loading notice', async () => {
  const state = setup({ vehicles: [{ entry_id: 'car-1', name: 'NIO' }] });
  await tick();
  assert.equal(state.status.hidden, true);
  state.panel.panel = { config: { ...state.config } };
  await tick();
  assert.equal(state.status.hidden, true);
  assert.equal(state.wsCalls, 1);
});

test('a card configuration failure remains visible after module loading finishes', async () => {
  const state = setup({ vehicles: [{ entry_id: 'car-1', name: 'NIO' }], cardFails: true });
  await tick();
  assert.equal(state.status.hidden, false);
  assert.equal(state.status.attributes.role, 'alert');
  assert.equal(state.status.children.at(-1).textContent, 'Try again');
});

test('explicit retry uses a fresh module URL after an import failure', async () => {
  const state = setup({ importFails: true });
  await tick();
  state.status.children.at(-1).emit('click');
  await tick();
  assert.notEqual(state.imported[0], state.imported[1]);
  assert.match(state.imported[1], /nio_retry=1/);
});

test('ordinary HA state updates preserve the vehicle selector options', async () => {
  const state = setup({ vehicles: [{ entry_id: 'car-1', name: 'NIO' }] });
  await tick();
  const option = state.select.children[0];
  state.panel.hass = { ...state.hass, states: { updated: true } };
  assert.equal(state.select.children[0], option);
  state.panel.hass = { ...state.hass, language: 'nl' };
  assert.equal(state.select.attributes['aria-label'], 'Auto');
});

test('loads only opted-in vehicles and forwards HA context and history URLs', async () => {
  const state = setup({ vehicles: [
    { entry_id: 'other', name: 'Not opted in' },
    { entry_id: 'car-1', name: 'EL7' },
    { entry_id: 'car-2', name: 'ET5 Touring' },
  ] });
  await tick();

  assert.equal(state.imported[0], state.config.vehicle_card_url);
  assert.equal(state.menu.hass, state.hass);
  assert.equal(state.menu.narrow, true);
  assert.equal(state.selector.hidden, false);
  assert.deepEqual(state.select.children.map((option) => option.textContent), ['EL7', 'ET5 Touring']);
  assert.equal(state.cardHost.children[0].config.entry_id, 'car-1');
  assert.equal(state.cardHost.children[0].config.history_url, state.config.history_url);
  assert.equal(state.cardHost.children[0].config.history_base_url, state.config.history_base_url);
  assert.equal(state.cardHost.children[0].hass, state.hass);
  assert.deepEqual(state.cardHost.children[0].route, { path: '/nio' });

  state.select.value = 'car-2';
  state.select.emit('change');
  assert.equal(state.cardHost.children[0].config.entry_id, 'car-2');
});

test('single vehicle has no redundant selector and uses a safe fallback name', async () => {
  const state = setup({
    vehicles: [{ entry_id: 'car-1', name: '' }],
    entryIds: ['car-1'],
  });
  await tick();

  assert.equal(state.selector.hidden, true);
  assert.equal(state.select.children[0].textContent, 'NIO vehicle 1');
  assert.equal(state.cardHost.children[0].config.entry_id, 'car-1');
});

test('failed module load is visible and offers an explicit retry', async () => {
  const state = setup({ importFails: true, vehicles: [{ entry_id: 'car-1', name: 'NIO' }] });
  await tick();

  assert.equal(state.status.hidden, false);
  assert.equal(state.status.attributes.role, 'alert');
  assert.ok(state.status.children.some((child) => child.textContent === 'The NIO dashboard could not load.'));
  const retry = state.status.children.find((child) => child.className === 'retry');
  assert.ok(retry);
  retry.emit('click');
  await tick();
  assert.equal(state.imported.length, 2);
});

test('a hass update during a pending load forwards the latest connection context', async () => {
  const state = setup({ pending: true });
  await tick();
  const latestHass = { language: 'nl', callWS: async () => ({ vehicles: [] }) };
  state.panel.hass = latestHass;
  state.resolveVehicles({ vehicles: [{ entry_id: 'car-1', name: 'ET7' }] });
  await tick();

  assert.equal(state.wsCalls, 1);
  assert.equal(state.cardHost.children[0].hass, latestHass);
  assert.equal(state.menu.hass, latestHass);
});

test('detaching the panel invalidates an in-flight response', async () => {
  const state = setup({ pending: true });
  await tick();
  state.panel.disconnectedCallback();
  state.resolveVehicles({ vehicles: [{ entry_id: 'car-1', name: 'ET7' }] });
  await tick();

  assert.equal(state.cardHost.children.length, 0);
});
