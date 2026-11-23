/* Thin Home Assistant panel host for the shared NIO vehicle dashboard. */
class NioVehiclePanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._narrow = false;
    this._route = null;
    this._vehicles = [];
    this._selectedEntryId = null;
    this._card = null;
    this._running = false;
    this._pending = false;
    this._request = 0;
    this._retryAttempt = 0;
    this._loadKey = null;
    this._configKey = null;
    this._shellReady = false;
  }

  setConfig(config) {
    this.config = config || {};
    const key = this._configurationKey();
    if (key !== this._configKey) {
      this._configKey = key;
      this._loadKey = null;
      this._request += 1;
    }
    this._renderShell();
    this._scheduleLoad();
  }

  set panel(value) {
    this._panel = value;
    this.setConfig(value?.config || {});
  }

  get panel() {
    return this._panel;
  }

  set hass(value) {
    const firstHass = !this._hass && Boolean(value);
    const languageChanged = value?.language !== this._hass?.language;
    this._hass = value;
    const menu = this.shadowRoot?.querySelector("ha-menu-button");
    if (menu) {
      menu.hass = value;
      menu.setAttribute("aria-label", this._words().openMenu);
    }
    if (languageChanged && this._vehicles.length) this._renderSelector();
    if (this._card) this._forwardContext();
    if (firstHass) this._scheduleLoad();
  }

  get hass() {
    return this._hass;
  }

  set narrow(value) {
    this._narrow = Boolean(value);
    const menu = this.shadowRoot?.querySelector("ha-menu-button");
    if (menu) menu.narrow = this._narrow;
    this._forwardContext();
  }

  get narrow() {
    return this._narrow;
  }

  set route(value) {
    this._route = value;
    this._forwardContext();
  }

  get route() {
    return this._route;
  }

  connectedCallback() {
    this._renderShell();
    this._scheduleLoad();
  }

  disconnectedCallback() {
    this._request += 1;
    this._loadKey = null;
    this._pending = false;
  }

  _words() {
    const code = (this._hass?.language || "en").replace("_", "-").split("-")[0].toLowerCase();
    const keys = ["loading", "selector", "unavailable", "failed", "retry", "openMenu", "invalid"];
    const rows = {
      en: ["Loading NIO vehicles…", "Vehicle", "No opted-in NIO vehicle is currently available.", "The NIO dashboard could not load.", "Try again", "Open navigation menu", "The NIO dashboard configuration is incomplete."],
      nl: ["NIO-auto’s laden…", "Auto", "Er is momenteel geen ingeschakelde NIO-auto beschikbaar.", "Het NIO-dashboard kon niet worden geladen.", "Opnieuw proberen", "Navigatiemenu openen", "De configuratie van het NIO-dashboard is onvolledig."],
      fr: ["Chargement des véhicules NIO…", "Véhicule", "Aucun véhicule NIO activé n’est disponible.", "Le tableau de bord NIO n’a pas pu être chargé.", "Réessayer", "Ouvrir le menu de navigation", "La configuration du tableau de bord NIO est incomplète."],
      de: ["NIO-Fahrzeuge werden geladen…", "Fahrzeug", "Kein aktiviertes NIO-Fahrzeug ist verfügbar.", "Das NIO-Dashboard konnte nicht geladen werden.", "Erneut versuchen", "Navigationsmenü öffnen", "Die NIO-Dashboard-Konfiguration ist unvollständig."],
      nb: ["Laster NIO-kjøretøy…", "Kjøretøy", "Ingen aktivert NIO-bil er tilgjengelig.", "NIO-dashbordet kunne ikke lastes.", "Prøv igjen", "Åpne navigasjonsmenyen", "NIO-dashbordkonfigurasjonen er ufullstendig."],
      sv: ["Läser in NIO-fordon…", "Fordon", "Inget aktiverat NIO-fordon är tillgängligt.", "NIO-instrumentpanelen kunde inte läsas in.", "Försök igen", "Öppna navigeringsmenyn", "Konfigurationen för NIO-instrumentpanelen är ofullständig."],
      da: ["Indlæser NIO-køretøjer…", "Køretøj", "Intet aktiveret NIO-køretøj er tilgængeligt.", "NIO-dashboardet kunne ikke indlæses.", "Prøv igen", "Åbn navigationsmenuen", "NIO-dashboardkonfigurationen er ufuldstændig."],
      cs: ["Načítání vozidel NIO…", "Vozidlo", "Není dostupné žádné povolené vozidlo NIO.", "Panel NIO se nepodařilo načíst.", "Zkusit znovu", "Otevřít navigační nabídku", "Konfigurace panelu NIO není úplná."],
      el: ["Φόρτωση οχημάτων NIO…", "Όχημα", "Δεν υπάρχει διαθέσιμο ενεργοποιημένο όχημα NIO.", "Δεν ήταν δυνατή η φόρτωση του πίνακα NIO.", "Δοκιμή ξανά", "Άνοιγμα μενού πλοήγησης", "Η διαμόρφωση του πίνακα NIO δεν είναι πλήρης."],
      hu: ["NIO-járművek betöltése…", "Jármű", "Nem érhető el bekapcsolt NIO-jármű.", "Az NIO-irányítópult nem tölthető be.", "Újra", "Navigációs menü megnyitása", "Az NIO-irányítópult beállítása hiányos."],
      lb: ["NIO-Gefierer gi gelueden…", "Gefier", "Keen aktivéiert NIO-Gefier ass disponibel.", "Den NIO-Dashboard konnt net geluede ginn.", "Nach eng Kéier probéieren", "Navigatiounsmenü opmaachen", "D’NIO-Dashboard-Konfiguratioun ass net komplett."],
      pl: ["Wczytywanie pojazdów NIO…", "Pojazd", "Brak dostępnego włączonego pojazdu NIO.", "Nie udało się wczytać pulpitu NIO.", "Spróbuj ponownie", "Otwórz menu nawigacji", "Konfiguracja pulpitu NIO jest niekompletna."],
      pt: ["A carregar veículos NIO…", "Veículo", "Não há veículos NIO ativos disponíveis.", "Não foi possível carregar o painel NIO.", "Tentar novamente", "Abrir menu de navegação", "A configuração do painel NIO está incompleta."],
      ro: ["Se încarcă vehiculele NIO…", "Vehicul", "Nu este disponibil niciun vehicul NIO activat.", "Tabloul de bord NIO nu a putut fi încărcat.", "Încearcă din nou", "Deschide meniul de navigare", "Configurația tabloului de bord NIO este incompletă."],
    };
    return Object.fromEntries(keys.map((key, index) => [key, (rows[code] || rows.en)[index]]));
  }

  _renderShell() {
    if (this._shellReady || !this.shadowRoot) return;
    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;min-height:100%;color:var(--primary-text-color);background:var(--primary-background-color);font-family:"Segoe UI",system-ui,Roboto,sans-serif}
        .page{min-height:100vh;min-height:100dvh}
        .toolbar{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:12px;min-height:56px;padding:0 max(16px,calc((100vw - 820px)/2));background:var(--app-header-background-color,var(--primary-background-color));border-bottom:1px solid var(--divider-color);box-sizing:border-box}
        ha-menu-button{flex:none}
        .title{margin:0;font-size:20px;font-weight:400;line-height:1.35}
        main{max-width:820px;margin:0 auto;padding:16px 16px 32px;box-sizing:border-box}
        .selector{display:flex;align-items:center;gap:12px;margin:0 0 12px}
        .selector[hidden]{display:none}
        .selector label{font-size:14px;color:var(--secondary-text-color)}
        select{flex:1;min-width:0;min-height:44px;padding:8px 36px 8px 12px;border:1px solid var(--divider-color);border-radius:8px;background:var(--card-background-color);color:var(--primary-text-color);font:inherit}
        .status{margin:16px 0;padding:12px 14px;border:1px solid var(--divider-color);border-radius:10px;background:var(--card-background-color);color:var(--secondary-text-color);font-size:14px;line-height:1.5}
        .status[hidden]{display:none}
        .status[role=alert]{color:var(--error-color,var(--primary-text-color))}
        .retry{min-height:44px;margin:8px 0 0;padding:7px 13px;border:1px solid var(--divider-color);border-radius:8px;background:var(--card-background-color);color:var(--primary-text-color);font:inherit;cursor:pointer}
        .retry:focus-visible,select:focus-visible{outline:2px solid var(--primary-color);outline-offset:2px}
        .card-host{min-width:0}
        @media(max-width:600px){.toolbar{padding-inline:8px}.title{font-size:18px}main{padding:12px 8px 24px}.selector{display:grid;gap:6px}}
        @media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
      </style>
      <div class="page">
        <header class="toolbar"><ha-menu-button></ha-menu-button><h1 class="title">NIO</h1></header>
        <main>
          <div class="selector" hidden>
            <label for="vehicle-select"></label>
            <select id="vehicle-select" aria-label=""></select>
          </div>
          <div class="status" role="status" aria-live="polite" hidden></div>
          <div class="card-host"></div>
        </main>
      </div>`;
    this._shellReady = true;
    const menu = this.shadowRoot.querySelector("ha-menu-button");
    menu.hass = this._hass;
    menu.narrow = this._narrow;
    menu.setAttribute("aria-label", this._words().openMenu);
    const select = this.shadowRoot.querySelector("select");
    select.addEventListener("change", () => this._selectVehicle(select.value));
  }

  _validConfig() {
    const config = this.config;
    return Boolean(
      config?.owner === "nio_telematics" &&
      config?.schema_version === 1 &&
      Array.isArray(config?.entry_ids) &&
      config.entry_ids.length > 0 &&
      config.entry_ids.every((id) => typeof id === "string" && id.length > 0) &&
      this._isLocalAsset(config?.vehicle_card_url) &&
      this._isLocalAsset(config?.history_url) &&
      this._isLocalAsset(config?.history_base_url)
    );
  }

  _isLocalAsset(url) {
    return typeof url === "string" && url.startsWith("/nio_telematics/") && !url.startsWith("//");
  }

  _setStatus(message, error = false) {
    const status = this.shadowRoot?.querySelector(".status");
    if (!status) return;
    status.replaceChildren();
    status.hidden = !message;
    status.setAttribute("role", error ? "alert" : "status");
    status.setAttribute("aria-live", error ? "assertive" : "polite");
    if (message) {
      const text = document.createElement("span");
      text.textContent = message;
      status.append(text);
    }
    if (error) {
      const retry = document.createElement("button");
      retry.className = "retry";
      retry.type = "button";
      retry.textContent = this._words().retry;
      retry.addEventListener("click", () => this._scheduleLoad(true));
      status.append(retry);
    }
  }

  _scheduleLoad(retry = false) {
    if (!this.config || !this._hass || !this.isConnected) return;
    const key = this._configurationKey();
    if (retry) this._loadKey = null;
    if (this._loadKey === key) return;
    if (this._running) {
      this._pending = true;
      this._loadKey = key;
      return;
    }
    this._running = true;
    this._loadKey = key;
    const request = ++this._request;
    void this._load(request, retry);
  }

  async _load(request, retry = false) {
    try {
      if (!this._validConfig()) {
        this._setStatus(this._words().invalid, true);
        return;
      }
      const config = this.config;
      const hass = this._hass;
      const moduleUrl = retry
        ? `${config.vehicle_card_url}${config.vehicle_card_url.includes("?") ? "&" : "?"}nio_retry=${++this._retryAttempt}`
        : config.vehicle_card_url;
      this._setStatus(this._words().loading, false);
      const [, result] = await Promise.all([
        import(moduleUrl),
        hass.callWS({ type: "nio_telematics/vehicle_dashboard/get" }),
      ]);
      if (request !== this._request) return;
      const optedIn = new Set(config.entry_ids);
      this._vehicles = (Array.isArray(result?.vehicles) ? result.vehicles : [])
        .filter((vehicle) => optedIn.has(vehicle.entry_id))
        .map((vehicle, index) => ({
          entry_id: vehicle.entry_id,
          name: typeof vehicle.name === "string" && vehicle.name.trim()
            ? vehicle.name.trim()
            : `NIO vehicle ${index + 1}`,
        }));
      if (!this._vehicles.length) {
        this._card?.remove();
        this._card = null;
        this._renderSelector();
        this._setStatus(this._words().unavailable, true);
        return;
      }
      if (!customElements.get("nio-vehicle-dashboard")) {
        throw new Error("dashboard component did not register");
      }
      this._renderSelector();
      const selected = this._vehicles.some((vehicle) => vehicle.entry_id === this._selectedEntryId)
        ? this._selectedEntryId
        : this._vehicles[0].entry_id;
      this._selectVehicle(selected);
    } catch (_error) {
      if (request !== this._request) return;
      this._setStatus(this._words().failed, true);
    } finally {
      this._running = false;
      if (this._pending) {
        this._pending = false;
        this._scheduleLoad(true);
      }
    }
  }

  _renderSelector() {
    const wrapper = this.shadowRoot?.querySelector(".selector");
    const label = wrapper?.querySelector("label");
    const select = wrapper?.querySelector("select");
    if (!wrapper || !label || !select) return;
    const words = this._words();
    label.textContent = words.selector;
    select.setAttribute("aria-label", words.selector);
    select.replaceChildren();
    for (const vehicle of this._vehicles) {
      const option = document.createElement("option");
      option.value = vehicle.entry_id;
      option.textContent = vehicle.name;
      select.append(option);
    }
    wrapper.hidden = this._vehicles.length < 2;
    if (this._vehicles.length) {
      select.value = this._vehicles.some((vehicle) => vehicle.entry_id === this._selectedEntryId)
        ? this._selectedEntryId
        : this._vehicles[0].entry_id;
    }
  }

  _selectVehicle(entryId) {
    const vehicle = this._vehicles.find((candidate) => candidate.entry_id === entryId);
    if (!vehicle) return;
    this._selectedEntryId = vehicle.entry_id;
    const host = this.shadowRoot?.querySelector(".card-host");
    if (!host) return;
    if (!this._card) {
      this._card = document.createElement("nio-vehicle-dashboard");
      host.replaceChildren(this._card);
    }
    try {
      this._card.setConfig({
        entry_id: vehicle.entry_id,
        history_url: this.config.history_url,
        history_base_url: this.config.history_base_url,
      });
      this._forwardContext();
      this._setStatus("", false);
    } catch (_error) {
      this._card.remove();
      this._card = null;
      this._setStatus(this._words().failed, true);
    }
  }

  _forwardContext() {
    if (!this._card) return;
    this._card.hass = this._hass;
    this._card.narrow = this._narrow;
    this._card.route = this._route;
  }

  _configurationKey() {
    const config = this.config || {};
    return JSON.stringify([
      config.owner,
      config.schema_version,
      config.entry_ids,
      config.vehicle_card_url,
      config.history_url,
      config.history_base_url,
    ]);
  }
}

customElements.define("nio-vehicle-panel", NioVehiclePanel);
