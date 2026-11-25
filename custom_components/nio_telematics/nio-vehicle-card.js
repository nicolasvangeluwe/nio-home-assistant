/* Optional NIO vehicle overview. No external assets or runtime services. */
const NIO_WORDS = {
  en: ['Remaining charge','Range','Odometer','Charge limit','Charging','Not charging','Last reading','Details','Settings','Save','Cancel','Model','Language','EVCC connection','EVCC power','EVCC sessions','Electricity price','Reimbursement rate','Battery capacity','Unavailable','No vehicle configured','Select a vehicle','Charging history'],
  nl: ['Batterijlading','Actieradius','Kilometerstand','Laadlimiet','Laden','Laadt niet','Laatste meting','Details','Instellingen','Opslaan','Annuleren','Model','Taal','EVCC-verbinding','EVCC-vermogen','EVCC-sessies','Stroomprijs','Vergoedingstarief','Batterijcapaciteit','Niet beschikbaar','Geen auto ingesteld','Selecteer een auto','Laadhistoriek'],
  de: ['Restladung','Reichweite','Kilometerstand','Ladelimit','Lädt','Lädt nicht','Letzte Messung','Details','Einstellungen','Speichern','Abbrechen','Modell','Sprache','EVCC-Verbindung','EVCC-Leistung','EVCC-Sitzungen','Strompreis','Erstattungssatz','Batteriekapazität','Nicht verfügbar','Kein Fahrzeug eingerichtet','Fahrzeug wählen','Ladeverlauf'],
  fr: ['Charge restante','Autonomie','Kilométrage','Limite de charge','En charge','Pas en charge','Dernière mesure','Détails','Paramètres','Enregistrer','Annuler','Modèle','Langue','Connexion EVCC','Puissance EVCC','Sessions EVCC','Prix de l’électricité','Taux de remboursement','Capacité de la batterie','Indisponible','Aucun véhicule configuré','Choisir un véhicule','Historique de charge'],
  nb: ['Gjenværende lading','Rekkevidde','Kilometerstand','Ladegrense','Lader','Lader ikke','Siste måling','Detaljer','Innstillinger','Lagre','Avbryt','Modell','Språk','EVCC-tilkobling','EVCC-effekt','EVCC-økter','Strømpris','Refusjonssats','Batterikapasitet','Utilgjengelig','Ingen bil konfigurert','Velg bil','Ladehistorikk'],
  sv: ['Återstående laddning','Räckvidd','Mätarställning','Laddgräns','Laddar','Laddar inte','Senaste mätning','Detaljer','Inställningar','Spara','Avbryt','Modell','Språk','EVCC-anslutning','EVCC-effekt','EVCC-sessioner','Elpris','Ersättningsnivå','Batterikapacitet','Otillgänglig','Ingen bil konfigurerad','Välj bil','Laddhistorik'],
  da: ['Resterende opladning','Rækkevidde','Kilometertal','Ladegrænse','Oplader','Oplader ikke','Seneste måling','Detaljer','Indstillinger','Gem','Annuller','Model','Sprog','EVCC-forbindelse','EVCC-effekt','EVCC-sessioner','Elpris','Refusionssats','Batterikapacitet','Ikke tilgængelig','Ingen bil konfigureret','Vælg bil','Opladningshistorik'],
  cs: ['Zbývající nabití','Dojezd','Stav tachometru','Limit nabíjení','Nabíjí se','Nenabíjí se','Poslední měření','Podrobnosti','Nastavení','Uložit','Zrušit','Model','Jazyk','Připojení EVCC','Výkon EVCC','Relace EVCC','Cena elektřiny','Sazba náhrady','Kapacita baterie','Nedostupné','Žádné vozidlo','Vybrat vozidlo','Historie nabíjení'],
  el: ['Υπολειπόμενη φόρτιση','Αυτονομία','Χιλιομετρητής','Όριο φόρτισης','Φορτίζει','Δεν φορτίζει','Τελευταία μέτρηση','Λεπτομέρειες','Ρυθμίσεις','Αποθήκευση','Ακύρωση','Μοντέλο','Γλώσσα','Σύνδεση EVCC','Ισχύς EVCC','Συνεδρίες EVCC','Τιμή ρεύματος','Τιμή αποζημίωσης','Χωρητικότητα μπαταρίας','Μη διαθέσιμο','Δεν έχει ρυθμιστεί όχημα','Επιλογή οχήματος','Ιστορικό φόρτισης'],
  hu: ['Hátralévő töltöttség','Hatótáv','Kilométeróra','Töltési korlát','Töltés','Nem tölt','Utolsó mérés','Részletek','Beállítások','Mentés','Mégse','Modell','Nyelv','EVCC-kapcsolat','EVCC-teljesítmény',"EVCC-töltési munkamenetek",'Áramár','Térítési díj','Akkumulátorkapacitás','Nem elérhető','Nincs beállított jármű','Jármű kiválasztása','Töltési előzmények'],
  lb: ['Reschtlech Luedung','Reechwäit','Kilometerstand','Luedlimit','Gëtt opgelueden','Gëtt net opgelueden','Lescht Miessung','Detailer','Astellungen','Späicheren','Ofbriechen','Modell','Sprooch','EVCC-Verbindung','EVCC-Leeschtung','EVCC-Sessiounen','Stroumpräis','Remboursements-Taux','Batteriekapazitéit','Net verfügbar','Keen Auto ageriicht','Auto auswielen','Opluedhistorik'],
  pl: ['Pozostały poziom naładowania','Zasięg','Przebieg','Limit ładowania','Ładowanie','Nie ładuje','Ostatni pomiar','Szczegóły','Ustawienia','Zapisz','Anuluj','Model','Język','Połączenie EVCC','Moc EVCC','Sesje EVCC','Cena energii','Stawka zwrotu','Pojemność baterii','Niedostępne','Brak skonfigurowanego auta','Wybierz auto','Historia ładowania'],
  pt: ['Carga restante','Autonomia','Quilometragem','Limite de carga','A carregar','Não está a carregar','Última leitura','Detalhes','Definições','Guardar','Cancelar','Modelo','Idioma','Ligação EVCC','Potência EVCC','Sessões EVCC','Preço da eletricidade','Taxa de reembolso','Capacidade da bateria','Indisponível','Nenhum veículo configurado','Escolher veículo','Histórico de carregamento'],
  ro: ['Încărcare rămasă','Autonomie','Kilometraj','Limită de încărcare','Se încarcă','Nu se încarcă','Ultima citire','Detalii','Setări','Salvează','Anulează','Model','Limbă','Conexiune EVCC','Putere EVCC','Sesiuni EVCC','Preț energie','Rată de rambursare','Capacitate baterie','Indisponibil','Nicio mașină configurată','Alege mașina','Istoric încărcare']
};
const NIO_KEYS = ['soc','range','odometer','limit','charging','idle','sample','details','settings','save','cancel','model','language','connected','power','history','price','reimbursement','capacity','unavailable','noVehicle','selectVehicle','chargeHistory'];
function nioChargingStatus(native, powerKw, connected){
  const state=String(native??'').toLowerCase();
  if(/^(charging|charge|1|on|true)$/.test(state)||(Number.isFinite(powerKw)&&powerKw>0.1))return 'charging';
  if(/^(not_charging|idle|0|off|false)$/.test(state))return 'idle';
  if(connected===true&&Number.isFinite(powerKw)&&powerKw>=0&&powerKw<=0.1)return 'idle';
  return null;
}
const NIO_CHARGING_UNKNOWN = {en:'Charging status unknown',nl:'Laadstatus onbekend',de:'Ladestatus unbekannt',fr:'État de charge inconnu',nb:'Ladestatus ukjent',sv:'Laddningsstatus okänd',da:'Ladestatus ukendt',cs:'Stav nabíjení neznámý',el:'Άγνωστη κατάσταση φόρτισης',hu:'A töltési állapot ismeretlen',lb:'Opluedstatus onbekannt',pl:'Stan ładowania nieznany',pt:'Estado de carregamento desconhecido',ro:'Starea încărcării este necunoscută'};
const NIO_CONNECTED_STATUS = {en:'Connected',nl:'Verbonden',de:'Verbunden',fr:'Connecté',nb:'Tilkoblet',sv:'Ansluten',da:'Tilsluttet',cs:'Připojeno',el:'Συνδεδεμένο',hu:'Csatlakoztatva',lb:'Verbonnen',pl:'Połączono',pt:'Ligado',ro:'Conectat'};
const NIO_DASHBOARD_UI={
 en:['Car','History','Settings','Appearance & language','Vehicle readings','Charger & cost sources','History & backup','Vehicle appearance, paint and language','Native readings and optional overrides','Charger status, costs and reimbursement','Recording, calculation basis and saved records','Calculated range','Based on recorded driving consumption','Not enough recorded driving data to calculate a range.','Ongoing charge','Energy','Duration','Solar energy','History setup','Enable history in Settings to see trips and charges.','History is unavailable for this vehicle.'],
 nl:['Auto','Historiek','Instellingen','Weergave en taal','Voertuigmetingen','Lader- en kostenbronnen','Historiek en back-up','Voertuigweergave, kleur en taal','NIO-metingen en optionele bronnen','Laderstatus, kosten en vergoeding','Registratie, berekeningsbasis en opgeslagen gegevens','Berekende actieradius','Op basis van geregistreerd rijverbruik','Onvoldoende geregistreerde rijgegevens om de actieradius te berekenen.','Lopende laadsessie','Energie','Duur','Zonne-energie','Historiek instellen','Schakel historiek in bij Instellingen om ritten en laadsessies te zien.','Historiek is niet beschikbaar voor dit voertuig.'],
 de:['Fahrzeug','Verlauf','Einstellungen','Darstellung und Sprache','Fahrzeugmesswerte','Lade- und Kostenquellen','Verlauf und Sicherung','Fahrzeugdarstellung, Farbe und Sprache','NIO-Werte und optionale Quellen','Ladestatus, Kosten und Erstattung','Erfassung, Berechnungsgrundlage und gespeicherte Daten','Berechnete Reichweite','Basierend auf erfasstem Fahrverbrauch','Nicht genügend Fahrdaten für eine Reichweitenberechnung.','Laufender Ladevorgang','Energie','Dauer','Solarenergie','Verlauf einrichten','Aktiviere den Verlauf in den Einstellungen, um Fahrten und Ladevorgänge zu sehen.','Der Verlauf ist für dieses Fahrzeug nicht verfügbar.'],
 fr:['Voiture','Historique','Paramètres','Apparence et langue','Mesures du véhicule','Sources du chargeur et des coûts','Historique et sauvegarde','Apparence, couleur et langue du véhicule','Valeurs NIO et sources facultatives','État du chargeur, coûts et remboursement','Enregistrement, base de calcul et données sauvegardées','Autonomie calculée','Basée sur la consommation de conduite enregistrée','Données de conduite enregistrées insuffisantes pour calculer l’autonomie.','Recharge en cours','Énergie','Durée','Énergie solaire','Configurer l’historique','Activez l’historique dans les paramètres pour voir les trajets et recharges.','Historique indisponible pour ce véhicule.'],
 nb:['Bil','Historikk','Innstillinger','Utseende og språk','Kjøretøymålinger','Lader- og kostnadskilder','Historikk og sikkerhetskopi','Kjøretøyets utseende, farge og språk','NIO-verdier og valgfrie kilder','Ladestatus, kostnader og refusjon','Registrering, beregningsgrunnlag og lagrede data','Beregnet rekkevidde','Basert på registrert kjøreforbruk','Ikke nok registrerte kjøredata til å beregne rekkevidde.','Pågående lading','Energi','Varighet','Solenergi','Sett opp historikk','Aktiver historikk i Innstillinger for å se turer og lading.','Historikk er utilgjengelig for dette kjøretøyet.'],
 sv:['Bil','Historik','Inställningar','Utseende och språk','Fordonsmätvärden','Laddar- och kostnadskällor','Historik och säkerhetskopia','Fordonets utseende, färg och språk','NIO-värden och valfria källor','Laddstatus, kostnader och ersättning','Registrering, beräkningsgrund och sparade data','Beräknad räckvidd','Baserad på registrerad körförbrukning','Det finns inte tillräckligt med registrerade kördata för att beräkna räckvidden.','Pågående laddning','Energi','Varaktighet','Solenergi','Ställ in historik','Aktivera historik i Inställningar för att se resor och laddningar.','Historik är inte tillgänglig för detta fordon.'],
 da:['Bil','Historik','Indstillinger','Udseende og sprog','Køretøjsmålinger','Oplader- og omkostningskilder','Historik og sikkerhedskopi','Køretøjets udseende, farve og sprog','NIO-værdier og valgfrie kilder','Opladerstatus, omkostninger og refusion','Registrering, beregningsgrundlag og gemte data','Beregnet rækkevidde','Baseret på registreret kørselsforbrug','Der er ikke nok registrerede kørselsdata til at beregne rækkevidden.','Igangværende opladning','Energi','Varighed','Solenergi','Konfigurer historik','Aktivér historik i Indstillinger for at se ture og opladninger.','Historik er ikke tilgængelig for dette køretøj.'],
 cs:['Vůz','Historie','Nastavení','Vzhled a jazyk','Údaje o vozidle','Zdroje nabíječky a nákladů','Historie a záloha','Vzhled, barva a jazyk vozidla','Hodnoty NIO a volitelné zdroje','Stav nabíječky, náklady a náhrady','Záznam, základ výpočtu a uložená data','Vypočtený dojezd','Podle zaznamenané spotřeby při jízdě','Pro výpočet dojezdu není dost zaznamenaných jízdních údajů.','Probíhající nabíjení','Energie','Doba','Solární energie','Nastavení historie','Zapněte historii v Nastavení pro zobrazení jízd a nabíjení.','Historie tohoto vozidla není dostupná.'],
 el:['Αυτοκίνητο','Ιστορικό','Ρυθμίσεις','Εμφάνιση και γλώσσα','Μετρήσεις οχήματος','Πηγές φορτιστή και κόστους','Ιστορικό και αντίγραφο ασφαλείας','Εμφάνιση, χρώμα και γλώσσα οχήματος','Τιμές NIO και προαιρετικές πηγές','Κατάσταση φορτιστή, κόστος και επιστροφή','Καταγραφή, βάση υπολογισμού και αποθηκευμένα δεδομένα','Υπολογισμένη αυτονομία','Με βάση την καταγεγραμμένη κατανάλωση οδήγησης','Δεν υπάρχουν αρκετά καταγεγραμμένα δεδομένα οδήγησης για υπολογισμό αυτονομίας.','Φόρτιση σε εξέλιξη','Ενέργεια','Διάρκεια','Ηλιακή ενέργεια','Ρύθμιση ιστορικού','Ενεργοποιήστε το ιστορικό στις Ρυθμίσεις για διαδρομές και φορτίσεις.','Το ιστορικό δεν είναι διαθέσιμο για αυτό το όχημα.'],
 hu:['Autó','Előzmények','Beállítások','Megjelenés és nyelv','Járműadatok','Töltő- és költségforrások','Előzmények és biztonsági mentés','Jármű megjelenése, színe és nyelve','NIO-adatok és opcionális források','Töltőállapot, költségek és visszatérítés','Rögzítés, számítási alap és mentett adatok','Számított hatótáv','A rögzített vezetési fogyasztás alapján','Nincs elég rögzített vezetési adat a hatótáv számításához.','Folyamatban lévő töltés','Energia','Időtartam','Napenergia','Előzmények beállítása','Az utak és töltések megtekintéséhez engedélyezze az előzményeket a Beállításokban.','A jármű előzményei nem érhetők el.'],
 lb:['Auto','Historik','Astellungen','Ausgesinn a Sprooch','Gefiermiessungen','Luedapparat- a Käschtequellen','Historik a Backup','Ausgesinn, Faarf a Sprooch vum Gefier','NIO-Wäerter an optional Quellen','Status vum Luedapparat, Käschten a Remboursement','Registréierung, Berechnungsbasis a gespäichert Donnéeën','Berechent Reechwäit','Baséiert op registréiertem Fuerverbrauch','Net genuch registréiert Fuerdate fir eng Reechwäit ze berechnen.','Lafend Opluedung','Energie','Dauer','Solarstroum','Historik astellen','Aktivéiert d’Historik an den Astellunge fir Faarten an Opluedungen ze gesinn.','D’Historik ass fir dëst Gefier net verfügbar.'],
 pl:['Samochód','Historia','Ustawienia','Wygląd i język','Odczyty pojazdu','Źródła ładowarki i kosztów','Historia i kopia zapasowa','Wygląd, kolor i język pojazdu','Wartości NIO i opcjonalne źródła','Stan ładowarki, koszty i zwrot','Rejestrowanie, podstawa obliczeń i zapisane dane','Obliczony zasięg','Na podstawie zarejestrowanego zużycia podczas jazdy','Za mało zarejestrowanych danych z jazdy, aby obliczyć zasięg.','Trwające ładowanie','Energia','Czas trwania','Energia słoneczna','Konfiguracja historii','Włącz historię w Ustawieniach, aby zobaczyć przejazdy i ładowania.','Historia tego pojazdu jest niedostępna.'],
 pt:['Carro','Histórico','Definições','Aspeto e idioma','Leituras do veículo','Fontes do carregador e custos','Histórico e cópia de segurança','Aspeto, cor e idioma do veículo','Valores NIO e fontes opcionais','Estado do carregador, custos e reembolso','Registo, base de cálculo e dados guardados','Autonomia calculada','Com base no consumo de condução registado','Não existem dados de condução registados suficientes para calcular a autonomia.','Carregamento em curso','Energia','Duração','Energia solar','Configurar histórico','Ative o histórico nas Definições para ver viagens e carregamentos.','O histórico não está disponível para este veículo.'],
 ro:['Mașină','Istoric','Setări','Aspect și limbă','Valori ale vehiculului','Surse încărcător și costuri','Istoric și copie de rezervă','Aspectul, culoarea și limba vehiculului','Valori NIO și surse opționale','Starea încărcătorului, costuri și rambursare','Înregistrare, bază de calcul și date salvate','Autonomie calculată','Pe baza consumului de condus înregistrat','Nu există suficiente date de condus înregistrate pentru calcularea autonomiei.','Încărcare în curs','Energie','Durată','Energie solară','Configurare istoric','Activați istoricul în Setări pentru a vedea călătoriile și încărcările.','Istoricul nu este disponibil pentru acest vehicul.']
};
const NIO_DASHBOARD_SOLAR={en:'Solar share',nl:'Zonne-aandeel',de:'Solarer Anteil',fr:'Part solaire',nb:'Solandel',sv:'Solandel',da:'Solandel',cs:'Podíl solární energie',el:'Ηλιακό μερίδιο',hu:'Napenergia aránya',lb:'Solarundeel',pl:'Udział energii słonecznej',pt:'Parcela solar',ro:'Pondere solară'};
const NIO_DASHBOARD_SETTINGS_INTRO={en:'Appearance, vehicle data and history settings.',nl:'Weergave, voertuiggegevens en historiek.',de:'Darstellung, Fahrzeugdaten und Verlaufseinstellungen.',fr:'Apparence, données du véhicule et historique.',nb:'Utseende, kjøretøydata og historikkinnstillinger.',sv:'Utseende, fordonsdata och historikinställningar.',da:'Udseende, køretøjsdata og historikindstillinger.',cs:'Vzhled, údaje o vozidle a nastavení historie.',el:'Εμφάνιση, δεδομένα οχήματος και ρυθμίσεις ιστορικού.',hu:'Megjelenés, járműadatok és előzmények beállításai.',lb:'Ausgesinn, Gefierdaten an Historikastellungen.',pl:'Wygląd, dane pojazdu i ustawienia historii.',pt:'Aspeto, dados do veículo e definições do histórico.',ro:'Aspect, date despre vehicul și setări ale istoricului.'};
const NIO_DASHBOARD_HISTORY_INTRO={en:'Charging, trips, consumption and energy loss while parked.',nl:'Laden, ritten, verbruik en energieverlies tijdens stilstand.',de:'Ladevorgänge, Fahrten, Verbrauch und Energieverlust im Stand.',fr:'Recharges, trajets, consommation et perte d’énergie à l’arrêt.',nb:'Lading, turer, forbruk og energitap mens bilen står parkert.',sv:'Laddning, resor, förbrukning och energiförlust vid parkering.',da:'Opladning, ture, forbrug og energitab under parkering.',cs:'Nabíjení, jízdy, spotřeba a ztráta energie při stání.',el:'Φόρτιση, διαδρομές, κατανάλωση και απώλεια ενέργειας κατά τη στάθμευση.',hu:'Töltés, utak, fogyasztás és parkolás alatti energiaveszteség.',lb:'Opluedung, Faarten, Verbrauch an Energieverloscht beim Parken.',pl:'Ładowanie, przejazdy, zużycie i utrata energii podczas postoju.',pt:'Carregamento, viagens, consumo e perda de energia durante o estacionamento.',ro:'Încărcare, călătorii, consum și pierdere de energie în timpul parcării.'};
const NIO_DASHBOARD_RETAINED={en:'Last valid reading',nl:'Laatste geldige meting',de:'Letzter gültiger Messwert',fr:'Dernière mesure valide',nb:'Siste gyldige måling',sv:'Senaste giltiga mätning',da:'Seneste gyldige måling',cs:'Poslední platná hodnota',el:'Τελευταία έγκυρη μέτρηση',hu:'Utolsó érvényes mérés',lb:'Lescht valabel Miessung',pl:'Ostatni prawidłowy odczyt',pt:'Última leitura válida',ro:'Ultima citire validă'};
const NIO_HELP_ARIA={en:'Help',nl:'Help',de:'Hilfe',fr:'Aide',nb:'Hjelp',sv:'Hjälp',da:'Hjælp',cs:'Nápověda',el:'Βοήθεια',hu:'Súgó',lb:'Hëllef',pl:'Pomoc',pt:'Ajuda',ro:'Ajutor'};
const NIO_DASHBOARD_RETRY={en:'Retry',nl:'Opnieuw proberen',de:'Erneut versuchen',fr:'Réessayer',nb:'Prøv igjen',sv:'Försök igen',da:'Prøv igen',cs:'Zkusit znovu',el:'Δοκιμάστε ξανά',hu:'Újrapróbálás',lb:'Nach eng Kéier probéieren',pl:'Spróbuj ponownie',pt:'Tentar novamente',ro:'Încearcă din nou'};
const NIO_ERROR_FALLBACK={en:'Something went wrong. Please try again.',nl:'Er ging iets mis. Probeer het opnieuw.',de:'Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.',fr:'Une erreur s’est produite. Veuillez réessayer.',nb:'Noe gikk galt. Prøv igjen.',sv:'Något gick fel. Försök igen.',da:'Noget gik galt. Prøv igen.',cs:'Něco se nepovedlo. Zkuste to znovu.',el:'Κάτι πήγε στραβά. Δοκιμάστε ξανά.',hu:'Hiba történt. Próbálja meg újra.',lb:'Eppes ass schifgaangen. Probéiert nach eng Kéier.',pl:'Coś poszło nie tak. Spróbuj ponownie.',pt:'Ocorreu um erro. Tente novamente.',ro:'A apărut o eroare. Încercați din nou.'};
function nioLocaleTag(locale){const parts=String(locale||'en').replace(/_/g,'-').split('-').filter(Boolean);let code=(parts.shift()||'en').toLowerCase();if(code==='no')code='nb';else if(!NIO_WORDS[code])return 'en';return [code,...parts].join('-');}
function nioLocaleCode(locale){return nioLocaleTag(locale).split('-')[0].toLowerCase();}
const NIO_EXTRA = {
  "en": [
    "Full-charge range",
    "Trip and charging history",
    "Automatic",
    "NIO default"
  ],
  "nl": [
    "Actieradius bij volle batterij",
    "Ritten- en laadhistoriek",
    "Automatisch",
    "NIO-standaard"
  ],
  "de": [
    "Reichweite bei voller Ladung",
    "Fahrten- und Ladeverlauf",
    "Automatisch",
    "NIO-Standard"
  ],
  "fr": [
    "Autonomie à pleine charge",
    "Historique des trajets et recharges",
    "Automatique",
    "NIO par défaut"
  ],
  "nb": [
    "Rekkevidde ved fullading",
    "Tur- og ladehistorikk",
    "Automatisk",
    "NIO-standard"
  ],
  "sv": [
    "Räckvidd vid full laddning",
    "Rese- och laddhistorik",
    "Automatiskt",
    "NIO-standard"
  ],
  "da": [
    "Rækkevidde ved fuld opladning",
    "Tur- og ladehistorik",
    "Automatisk",
    "NIO-standard"
  ],
  "cs": [
    "Dojezd při plném nabití",
    "Historie jízd a nabíjení",
    "Automaticky",
    "Výchozí NIO"
  ],
  "el": [
    "Αυτονομία πλήρους φόρτισης",
    "Ιστορικό διαδρομών και φόρτισης",
    "Αυτόματα",
    "Προεπιλογή NIO"
  ],
  "hu": [
    "Hatótáv teljes töltésnél",
    "Utazási és töltési előzmények",
    "Automatikus",
    "NIO alapértelmezett"
  ],
  "lb": [
    "Reechwäit bei voller Luedung",
    "Faart- an Opluedhistorik",
    "Automatesch",
    "NIO-Standard"
  ],
  "pl": [
    "Zasięg przy pełnym ładowaniu",
    "Historia przejazdów i ładowania",
    "Automatycznie",
    "Domyślne NIO"
  ],
  "pt": [
    "Autonomia com carga completa",
    "Histórico de viagens e carregamentos",
    "Automático",
    "NIO predefinido"
  ],
  "ro": [
    "Autonomie la încărcare completă",
    "Istoric deplasări și încărcări",
    "Automat",
    "NIO implicit"
  ]
};
const NIO_MODELS = ['auto','ET5','ET5 Touring','ET7','EL6','EL7','EL8','ES8','other'];
const NIO_MODEL_IDS = {'ET5':'et5','ET5 Touring':'et5-touring','EL6':'el6','ET7':'et7','EL7':'el7','EL8':'el8','ES8':'es8'};
const NIO_LANGUAGES = ['auto',...Object.keys(NIO_WORDS)];
const NIO_LANGUAGE_NAMES={en:'English',nl:'Nederlands',de:'Deutsch',fr:'Français',nb:'Norsk bokmål',sv:'Svenska',da:'Dansk',cs:'Čeština',el:'Ελληνικά',hu:'Magyar',lb:'Lëtzebuergesch',pl:'Polski',pt:'Português',ro:'Română'};
const NIO_OTHER_MODEL={en:'Other model',nl:'Ander model',de:'Anderes Modell',fr:'Autre modèle',nb:'Annen modell',sv:'Annan modell',da:'Anden model',cs:'Jiný model',el:'Άλλο μοντέλο',hu:'Másik modell',lb:'Aneren Modell',pl:'Inny model',pt:'Outro modelo',ro:'Alt model'};
const NIO_PAINT_LABELS = {en:'Car colour',nl:'Autokleur',fr:'Couleur de la voiture',de:'Fahrzeugfarbe',nb:'Bilfarge',sv:'Bilfärg',da:'Bilfarve',cs:'Barva vozu',el:'Χρώμα αυτοκινήτου',hu:'Autó színe',lb:'Autosfaarf',pl:'Kolor auta',pt:'Cor do carro',ro:'Culoarea mașinii'};
let nioArtworkCataloguePromise;
let nioArtworkRetryAfter=0;
async function nioLoadArtworkCatalogue(){
  if(typeof fetch!=='function')return null;
  if(Date.now()<nioArtworkRetryAfter)return null;
  if(!nioArtworkCataloguePromise)nioArtworkCataloguePromise=fetch('/nio_telematics/artwork/catalogue.json',{credentials:'same-origin'})
    .then(response=>{if(!response.ok)throw new Error('Local artwork unavailable');return response.json();})
    .then(data=>{if(data?.schema_version!==1||data?.selection!=='model_and_paint'||!Array.isArray(data.models))throw new Error('Invalid local artwork catalogue');return data;})
    .catch(()=>{nioArtworkCataloguePromise=null;nioArtworkRetryAfter=Date.now()+30000;return null;});
  return nioArtworkCataloguePromise;
}
const NIO_SOURCE_HINT = {
  en: "Leave a vehicle source empty for NIO. If charging status is unavailable, select the charger's charging-state sensor or W/kW power sensor; use a suitable charger sensor available in Home Assistant; EVCC is not required. Session history requires EVCC-compatible data.",
  nl: "Laat een autobron leeg voor NIO. Kies bij een ontbrekende laadstatus de laadstatussensor of W/kW-vermogenssensor van je lader; gebruik een geschikte lader-sensor die beschikbaar is in Home Assistant; EVCC is niet nodig. Sessiehistoriek vereist EVCC-compatibele gegevens.",
  de: "Fahrzeugquelle für NIO leer lassen. Wenn der Ladestatus fehlt, den Ladestatus- oder W/kW-Leistungssensor des Ladegeräts auswählen; verwenden Sie einen geeigneten, in Home Assistant verfügbaren Ladesensor; EVCC ist nicht erforderlich. Sitzungsverlauf benötigt EVCC-kompatible Daten.",
  fr: "Laissez la source véhicule vide pour NIO. Si l’état de charge manque, sélectionnez le capteur d’état ou de puissance W/kW de la borne ; utilisez un capteur de borne adapté disponible dans Home Assistant ; EVCC n’est pas requis. L’historique exige des données compatibles EVCC.",
  nb: "La bilkilden stå tom for NIO. Hvis ladestatus mangler, velg laderens ladestatus- eller W/kW-effektsensor; bruk en egnet ladesensor som er tilgjengelig i Home Assistant; EVCC er ikke nødvendig. Økthistorikk krever EVCC-kompatible data.",
  sv: "Lämna fordonskällan tom för NIO. Om laddningsstatus saknas väljer du laddarens status- eller W/kW-effektsensor; använd en lämplig laddarsensor som finns i Home Assistant; EVCC krävs inte. Sessionshistorik kräver EVCC-kompatibla data.",
  da: "Lad køretøjskilden være tom for NIO. Hvis ladestatus mangler, vælg opladerens ladestatus- eller W/kW-effektsensor; brug en egnet opladersensor, der findes i Home Assistant; EVCC er ikke påkrævet. Sessionshistorik kræver EVCC-kompatible data.",
  cs: "Zdroj vozidla ponechte prázdný pro NIO. Pokud stav nabíjení chybí, vyberte senzor stavu nebo výkonu W/kW nabíječky; použijte vhodný senzor nabíječky dostupný v Home Assistant; EVCC není nutné. Historie relací vyžaduje data kompatibilní s EVCC.",
  el: "Αφήστε κενή την πηγή οχήματος για το NIO. Αν λείπει η κατάσταση φόρτισης, επιλέξτε τον αισθητήρα κατάστασης ή ισχύος W/kW του φορτιστή· χρησιμοποιήστε κατάλληλο αισθητήρα φορτιστή διαθέσιμο στο Home Assistant· δεν απαιτείται EVCC. Το ιστορικό συνεδριών απαιτεί δεδομένα συμβατά με EVCC.",
  hu: "Hagyja üresen a járműforrást a NIO-hoz. Ha hiányzik a töltési állapot, válassza a töltő állapot- vagy W/kW-teljesítmény-érzékelőjét; használjon a Home Assistantban elérhető megfelelő töltőérzékelőt; EVCC nem szükséges. A munkamenet-előzményekhez EVCC-kompatibilis adat kell.",
  lb: "Loosst d’Gefierquell eidel fir NIO ze benotzen. Wann den Opluedstatus feelt, wielt de Status- oder W/kW-Leeschtungssensor vum Luedapparat. Benotzt e passende Sensor vum Luedapparat, deen an Home Assistant verfügbar ass; EVCC ass net néideg. D’Historik vun Opluedsessioune verlaangt EVCC-kompatibel Donnéeën.",
  pl: "Pozostaw źródło pojazdu puste dla NIO. Jeśli brakuje stanu ładowania, wybierz czujnik stanu lub mocy W/kW ładowarki; użyj odpowiedniego czujnika ładowarki dostępnego w Home Assistant; EVCC nie jest wymagane. Historia sesji wymaga danych zgodnych z EVCC.",
  pt: "Deixe a fonte do veículo vazia para NIO. Se o estado de carregamento não estiver disponível, selecione o sensor de estado ou potência W/kW do carregador; utilize um sensor adequado do carregador disponível no Home Assistant; EVCC não é necessário. O histórico requer dados compatíveis com EVCC.",
  ro: "Lăsați sursa vehiculului goală pentru NIO. Dacă starea încărcării lipsește, selectați senzorul de stare sau putere W/kW al încărcătorului; folosiți un senzor adecvat al încărcătorului disponibil în Home Assistant; EVCC nu este necesar. Istoricul necesită date compatibile cu EVCC."
};
const NIO_INPUT_LABELS = {
  en:['Charger connection','Charging power','EVCC-compatible sessions'],
  nl:['Laderverbinding','Laadvermogen','EVCC-compatibele sessies'],
  de:['Ladegerät-Verbindung','Ladeleistung','EVCC-kompatible Sitzungen'],
  fr:['Connexion à la borne','Puissance de charge','Sessions compatibles EVCC'],
  nb:['Ladertilkobling','Ladeeffekt','EVCC-kompatible økter'],
  sv:['Laddaranslutning','Laddeffekt','EVCC-kompatibla sessioner'],
  da:['Ladertilslutning','Ladeeffekt','EVCC-kompatible sessioner'],
  cs:['Připojení nabíječky','Nabíjecí výkon','Relace kompatibilní s EVCC'],
  el:['Σύνδεση φορτιστή','Ισχύς φόρτισης','Συνεδρίες συμβατές με EVCC'],
  hu:['Töltő csatlakozása','Töltési teljesítmény','EVCC-kompatibilis munkamenetek'],
  lb:['Luedapparat-Verbindung','Luedleeschtung','EVCC-kompatibel Sessiounen'],
  pl:['Połączenie ładowarki','Moc ładowania','Sesje zgodne z EVCC'],
  pt:['Ligação ao carregador','Potência de carregamento','Sessões compatíveis com EVCC'],
  ro:['Conexiune încărcător','Putere de încărcare','Sesiuni compatibile EVCC']
};
const NIO_EVCC_PROMPT = {
  "en": "Quick setup: choose an EVCC charger",
  "nl": "Snel instellen: kies een EVCC-lader",
  "de": "Schnelleinrichtung: EVCC-Ladegerät wählen",
  "fr": "Configuration rapide : choisir une borne EVCC",
  "nb": "Hurtigoppsett: velg en EVCC-lader",
  "sv": "Snabbinstallation: välj en EVCC-laddare",
  "da": "Hurtig opsætning: vælg en EVCC-oplader",
  "cs": "Rychlé nastavení: vyberte nabíječku EVCC",
  "el": "Γρήγορη ρύθμιση: επιλέξτε έναν φορτιστή EVCC",
  "hu": "Gyors beállítás: válasszon EVCC töltőt",
  "lb": "Schnell Setup: wielt en EVCC Ladegerät",
  "pl": "Szybka konfiguracja: wybierz ładowarkę EVCC",
  "pt": "Configuração rápida: escolha um carregador EVCC",
  "ro": "Configurare rapidă: alegeți un încărcător EVCC"
};
const NIO_COST_INPUTS = {
  "en": [
    "Recorded cost sources",
    "Charging energy (cumulative kWh)",
    "Solar charging energy (cumulative kWh)",
    "Charging cost (cumulative currency)",
    "Grid import price (currency/kWh)",
    "Solar export price (currency/kWh)"
  ],
  "nl": [
    "Bronnen voor geregistreerde kosten",
    "Laadenergie (cumulatieve kWh)",
    "Zonnelaadenergie (cumulatieve kWh)",
    "Laadkosten (cumulatieve valuta)",
    "Netafnameprijs (valuta/kWh)",
    "Terugleverprijs (valuta/kWh)"
  ],
  "de": [
    "Quellen für erfasste Kosten",
    "Ladeenergie (kumulierte kWh)",
    "Solarladeenergie (kumulierte kWh)",
    "Ladekosten (kumulierte Währung)",
    "Netzbezugspreis (Währung/kWh)",
    "Einspeisepreis (Währung/kWh)"
  ],
  "fr": [
    "Sources des coûts enregistrés",
    "Énergie de charge (kWh cumulés)",
    "Énergie solaire de charge (kWh cumulés)",
    "Coût de charge (devise cumulée)",
    "Prix du réseau (devise/kWh)",
    "Prix de revente solaire (devise/kWh)"
  ],
  "nb": [
    "Registrerte kostnadskilder",
    "Ladeenergi (kumulativ kWh)",
    "Ladeenergi fra solkraft (kumulativ kWh)",
    "Ladekostnad (akkumulert valuta)",
    "Nettimportpris (valuta/kWh)",
    "Eksportpris for solenergi (valuta/kWh)"
  ],
  "sv": [
    "Registrerade kostnadskällor",
    "Laddningsenergi (ackumulerad kWh)",
    "Laddningsenergi från solen (ackumulerad kWh)",
    "Laddningskostnad (ackumulerad valuta)",
    "Nätimportpris (valuta/kWh)",
    "Exportpris för solenergi (valuta/kWh)"
  ],
  "da": [
    "Registrerede omkostningskilder",
    "Opladningsenergi (kumulativ kWh)",
    "Opladningsenergi fra solceller (kumulativ kWh)",
    "Opladningsomkostninger (akkumuleret valuta)",
    "Netimportpris (valuta/kWh)",
    "Eksportpris for solenergi (valuta/kWh)"
  ],
  "cs": [
    "Zaznamenané zdroje nákladů",
    "Nabíjecí energie (kumulativní kWh)",
    "Solární nabíjecí energie (kumulativní kWh)",
    "Náklady na nabíjení (kumulativní měna)",
    "Cena odběru ze sítě (měna/kWh)",
    "Cena za dodávku solární energie do sítě (měna/kWh)"
  ],
  "el": [
    "Καταγεγραμμένες πηγές κόστους",
    "Ενέργεια φόρτισης (αθροιστική kWh)",
    "Ηλιακή ενέργεια φόρτισης (αθροιστική kWh)",
    "Κόστος φόρτισης (σωρευτικό ποσό)",
    "Τιμή εισαγωγής δικτύου (νόμισμα/kWh)",
    "Τιμή εξαγωγής ηλιακής ενέργειας (νόμισμα/kWh)"
  ],
  "hu": [
    "Rögzített költségforrások",
    "Töltési energia (halmozott kWh)",
    "Napelemes töltési energia (halmozott kWh)",
    "Töltési költség (halmozott pénznem)",
    "Hálózati importár (valuta/kWh)",
    "Napenergia betáplálási ára (valuta/kWh)"
  ],
  "lb": [
    "Quelle fir registréiert Käschten",
    "Opluedenergie (kumulativ kWh)",
    "Solar Opluedenergie (kumulativ kWh)",
    "Opluedskäschte (kumulativ Währung)",
    "Netimportpräis (Währung/kWh)",
    "Solarexportpräis (Währung/kWh)"
  ],
  "pl": [
    "Zarejestrowane źródła kosztów",
    "Energia ładowania (skumulowana kWh)",
    "Energia ładowania słonecznego (skumulowana kWh)",
    "Koszt ładowania (waluta skumulowana)",
    "Cena importu sieci (waluta/kWh)",
    "Cena eksportowa energii słonecznej (waluta/kWh)"
  ],
  "pt": [
    "Fontes dos custos registados",
    "Energia de carregamento (kWh acumulada)",
    "Energia de carregamento solar (kWh acumulada)",
    "Custo de carregamento (moeda acumulada)",
    "Preço de importação da rede (moeda/kWh)",
    "Preço de exportação solar (moeda/kWh)"
  ],
  "ro": [
    "Surse de cost înregistrate",
    "Energie de încărcare (kWh cumulat)",
    "Energie solară de încărcare (kWh cumulat)",
    "Cost de încărcare (valută cumulată)",
    "Preț de import al rețelei (valută/kWh)",
    "Preț de export solar (valută/kWh)"
  ]
};
const NIO_FIELD_HELP = {
  "en": {
    "vehicle": "Optional. Leave empty to use the matching NIO sensor. Select another Home Assistant entity only if you need an override.",
    "evcc_connected": "Optional charger connection sensor. Accepts on/off, connected/disconnected or true/false; EVCC is not required.",
    "evcc_power": "Optional charger power sensor in W or kW. This is shown beside charging status.",
    "evcc_history": "Optional EVCC-compatible charging-session history. Leave empty if your charger does not provide it.",
    "electricity_price": "Optional current electricity price per kWh, for the overview only.",
    "reimbursement_rate": "Optional reimbursement rate per kWh, for the overview only.",
    "battery_capacity_kwh": "Usable battery capacity in kWh. Required only for trip and charging history.",
    "full_range_km": "Range shown by your car at 100% charge, in km. Required only for trip and charging history.",
    "ledger_enabled": "Store trips and charging history locally in Home Assistant. Disabling it does not erase saved history.",
    "costs": "Optional recorded-cost inputs. Supply all five from the same accounting source, or leave all empty."
  },
  "nl": {
    "vehicle": "Optioneel. Laat leeg om de bijbehorende NIO-sensor te gebruiken. Kies alleen een andere Home Assistant-entiteit als je die wilt gebruiken.",
    "evcc_connected": "Optionele sensor voor de verbinding met de lader. Ondersteunt aan/uit, verbonden/niet verbonden en waar/onwaar; EVCC is niet vereist.",
    "evcc_power": "Optionele sensor voor het laadvermogen in W of kW. Dit wordt naast de laadstatus getoond.",
    "evcc_history": "Optionele EVCC-compatibele laadsessiehistoriek. Laat leeg als je lader dit niet levert.",
    "electricity_price": "Optionele actuele stroomprijs per kWh voor het overzicht.",
    "reimbursement_rate": "Optioneel vergoedingstarief per kWh voor het overzicht.",
    "battery_capacity_kwh": "Bruikbare batterijcapaciteit in kWh. Alleen nodig voor ritten- en laadhistoriek.",
    "full_range_km": "Actieradius die je auto bij 100% lading aangeeft, in km. Alleen nodig voor de rit- en laadhistoriek.",
    "ledger_enabled": "Sla ritten en laadsessies lokaal in Home Assistant op. Uitschakelen wist de opgeslagen historiek niet.",
    "costs": "Optionele gegevens over geregistreerde kosten. Vul alle vijf waarden in op basis van dezelfde afrekening, of laat alles leeg."
  },
  "de": {
    "vehicle": "Optional. Leer lassen, damit der passende NIO-Sensor verwendet wird. Nur eine andere Home-Assistant-Entität auswählen, wenn sie den NIO-Wert ersetzen soll.",
    "evcc_connected": "Optionaler Sensor für die Ladegerätverbindung. EVCC ist nicht erforderlich.",
    "evcc_power": "Optionaler Ladeleistungssensor in W oder kW.",
    "evcc_history": "Optionaler EVCC-kompatibler Sitzungsverlauf. Sonst leer lassen.",
    "electricity_price": "Optionaler aktueller Strompreis pro kWh für die Übersicht.",
    "reimbursement_rate": "Optionaler Erstattungssatz pro kWh für die Übersicht.",
    "battery_capacity_kwh": "Nutzbare Batteriekapazität in kWh. Nur für Fahrten- und Ladeverlauf erforderlich.",
    "full_range_km": "Bei 100% im Auto angezeigte Reichweite in km. Nur für den Verlauf erforderlich.",
    "ledger_enabled": "Fahrten und Ladevorgänge lokal in Home Assistant speichern. Ausschalten löscht den Verlauf nicht.",
    "costs": "Optionale Kostenquellen. Alle fünf aus derselben Abrechnung eintragen oder alle leer lassen."
  },
  "fr": {
    "vehicle": "Facultatif. Laissez ce champ vide pour utiliser le capteur NIO correspondant. Sélectionnez une autre entité Home Assistant uniquement pour remplacer cette source.",
    "evcc_connected": "Capteur de connexion à la borne facultatif. EVCC n’est pas obligatoire.",
    "evcc_power": "Capteur de puissance de charge facultatif, en W ou kW.",
    "evcc_history": "Historique de sessions compatible EVCC facultatif. Sinon, laissez vide.",
    "electricity_price": "Prix actuel de l’électricité par kWh, facultatif pour la vue d’ensemble.",
    "reimbursement_rate": "Taux de remboursement par kWh, facultatif pour la vue d’ensemble.",
    "battery_capacity_kwh": "Capacité utile de la batterie en kWh. Requise seulement pour l’historique.",
    "full_range_km": "Autonomie affichée à 100% par la voiture, en km. Requise seulement pour l’historique.",
    "ledger_enabled": "Conserver les trajets et charges localement dans Home Assistant. Désactiver ne supprime pas l’historique.",
    "costs": "Sources de coûts facultatives. Indiquez les cinq d’une même comptabilité ou laissez-les vides."
  },
  "nb": {
    "vehicle": "Valgfritt. La stå tomt for å bruke den tilhørende NIO-sensoren. Velg en annen Home Assistant-entitet bare hvis du vil erstatte NIO-verdien.",
    "evcc_connected": "Valgfri ladertilkoblingssensor. Godtar på/av, tilkoblet/frakoblet eller sant/falsk; EVCC er ikke nødvendig.",
    "evcc_power": "Valgfri ladereffektsensor i W eller kW. Dette vises ved siden av ladestatus.",
    "evcc_history": "Valgfri EVCC-kompatibel ladeøktshistorikk. La det stå tomt hvis laderen ikke har det.",
    "electricity_price": "Valgfri gjeldende strømpris per kWh, kun for oversikten.",
    "reimbursement_rate": "Valgfri refusjonssats per kWh, kun for oversikten.",
    "battery_capacity_kwh": "Brukbar batterikapasitet i kWh. Kun nødvendig for tur- og ladehistorikk.",
    "full_range_km": "Rekkevidde vist av bilen din ved 100 % lading, i km. Kun nødvendig for tur- og ladehistorikk.",
    "ledger_enabled": "Lagre turer og ladehistorikk lokalt i Home Assistant. Deaktivering sletter ikke lagret historikk.",
    "costs": "Valgfrie inndata for registrerte kostnader. Oppgi alle fem fra samme regnskapskilde, eller la alle stå tomme."
  },
  "sv": {
    "vehicle": "Valfritt. Lämna tomt för att använda motsvarande NIO-sensor. Välj en annan Home Assistant-entitet endast om du vill ersätta NIO-värdet.",
    "evcc_connected": "Valfri sensor för laddarens anslutning. Accepterar på/av, ansluten/frånkopplad eller sant/falskt; EVCC krävs inte.",
    "evcc_power": "Valfri sensor för laddarens effekt i W eller kW. Effekten visas bredvid laddningsstatus.",
    "evcc_history": "Valfri EVCC-kompatibel laddningssessionshistorik. Lämna det tomt om din laddare inte har det.",
    "electricity_price": "Valfritt aktuellt elpris per kWh, endast för översikten.",
    "reimbursement_rate": "Valfri ersättningsgrad per kWh, endast för översikten.",
    "battery_capacity_kwh": "Användbar batterikapacitet i kWh. Krävs endast för rese- och laddningshistorik.",
    "full_range_km": "Räckvidden som bilen visar vid 100 % laddning, i km. Krävs endast för rese- och laddningshistorik.",
    "ledger_enabled": "Lagra resor och laddningshistorik lokalt i Home Assistant. Att inaktivera det raderar inte sparad historik.",
    "costs": "Valfria uppgifter om registrerade kostnader. Ange alla fem från samma redovisningskälla eller lämna alla tomma."
  },
  "da": {
    "vehicle": "Valgfrit. Lad feltet stå tomt for at bruge den tilsvarende NIO-sensor. Vælg kun en anden Home Assistant-entitet, hvis du vil erstatte NIO-værdien.",
    "evcc_connected": "Valgfri opladertilslutningssensor. Accepterer til/fra, tilsluttet/afbrudt eller sandt/falsk; EVCC er ikke påkrævet.",
    "evcc_power": "Valgfri opladereffektsensor i W eller kW. Dette vises ved siden af ​​ladestatus.",
    "evcc_history": "Valgfri EVCC-kompatibel historik over opladningssessioner. Lad feltet stå tomt, hvis din oplader ikke leverer det.",
    "electricity_price": "Valgfri aktuel elpris pr. kWh, kun til oversigt.",
    "reimbursement_rate": "Valgfri refusionssats pr. kWh, kun for oversigten.",
    "battery_capacity_kwh": "Brugbar batterikapacitet i kWh. Kun påkrævet for tur- og opladningshistorik.",
    "full_range_km": "Rækkevidde vist af din bil ved 100 % opladning, i km. Kun påkrævet for tur- og opladningshistorik.",
    "ledger_enabled": "Gem ture og opladningshistorik lokalt i Home Assistant. Deaktivering sletter ikke den gemte historik.",
    "costs": "Valgfrie oplysninger om registrerede omkostninger. Angiv alle fem fra samme regnskabskilde, eller lad alle felter stå tomme."
  },
  "cs": {
    "vehicle": "Volitelné. Chcete-li použít odpovídající senzor NIO, ponechte prázdné. Jinou entitu Home Assistant vyberte pouze v případě, že potřebujete přepsání.",
    "evcc_connected": "Volitelný snímač připojení nabíječky. Přijímá zapnuto/vypnuto, připojeno/odpojeno nebo pravda/nepravda; EVCC není vyžadováno.",
    "evcc_power": "Volitelný snímač výkonu nabíječky ve W nebo kW. Toto je zobrazeno vedle stavu nabíjení.",
    "evcc_history": "Volitelná historie nabíjení kompatibilní s EVCC. Nechte prázdné, pokud to vaše nabíječka neposkytuje.",
    "electricity_price": "Volitelná aktuální cena elektřiny za kWh, pouze pro přehled.",
    "reimbursement_rate": "Volitelná sazba náhrady za kWh, pouze pro přehled.",
    "battery_capacity_kwh": "Využitelná kapacita baterie v kWh. Vyžaduje se pouze pro historii jízd a nabíjení.",
    "full_range_km": "Dojezd zobrazený vaším autem při 100% nabití, v km. Vyžaduje se pouze pro historii jízd a nabíjení.",
    "ledger_enabled": "Historie jízd a nabíjení se ukládá místně v Home Assistant. Vypnutí této možnosti uloženou historii nevymaže.",
    "costs": "Volitelné vstupy se zaznamenanými náklady. Dodejte všech pět ze stejného účetního zdroje nebo nechte všechny prázdné."
  },
  "el": {
    "vehicle": "Προαιρετικό. Αφήστε το κενό για να χρησιμοποιήσετε τον αντίστοιχο αισθητήρα NIO. Επιλέξτε άλλη οντότητα Home Assistant μόνο εάν χρειάζεστε παράκαμψη.",
    "evcc_connected": "Προαιρετικός αισθητήρας σύνδεσης φορτιστή. Δέχεται ενεργοποίηση/απενεργοποίηση, σύνδεση/αποσύνδεση ή true/false. Δεν απαιτείται EVCC.",
    "evcc_power": "Προαιρετικός αισθητήρας ισχύος φορτιστή σε W ή kW. Αυτό εμφανίζεται δίπλα στην κατάσταση φόρτισης.",
    "evcc_history": "Προαιρετικό ιστορικό περιόδου σύνδεσης φόρτισης συμβατό με EVCC. Αφήστε κενό εάν ο φορτιστής σας δεν το παρέχει.",
    "electricity_price": "Προαιρετική τρέχουσα τιμή ηλεκτρικής ενέργειας ανά kWh, μόνο για την επισκόπηση.",
    "reimbursement_rate": "Προαιρετικό ποσοστό αποζημίωσης ανά kWh, μόνο για την επισκόπηση.",
    "battery_capacity_kwh": "Χρησιμοποιήσιμη χωρητικότητα μπαταρίας σε kWh. Απαιτείται μόνο για το ιστορικό ταξιδιού και φόρτισης.",
    "full_range_km": "Αυτονομία που δείχνει το αυτοκίνητό σας με 100% φόρτιση, σε km. Απαιτείται μόνο για το ιστορικό διαδρομών και φόρτισης.",
    "ledger_enabled": "Αποθηκεύστε ταξίδια και ιστορικό φόρτισης τοπικά στο Home Assistant. Η απενεργοποίησή του δεν διαγράφει το αποθηκευμένο ιστορικό.",
    "costs": "Προαιρετικές εισροές καταγεγραμμένου κόστους. Προμηθευτείτε και τα πέντε από την ίδια λογιστική πηγή ή αφήστε όλα άδεια."
  },
  "hu": {
    "vehicle": "Nem kötelező. Hagyja üresen a megfelelő NIO érzékelő használatához. Csak akkor válasszon másik Home Assistant entitást, ha felülírásra van szüksége.",
    "evcc_connected": "Opcionális töltőcsatlakozási érzékelő. Be/ki, csatlakoztatva/lekapcsolva vagy igaz/hamis; EVCC nem szükséges.",
    "evcc_power": "Opcionális töltőteljesítmény-érzékelő W-ban vagy kW-ban. Ez a töltési állapot mellett látható.",
    "evcc_history": "Opcionális EVCC-kompatibilis töltési munkamenet-előzmények. Hagyja üresen, ha a töltő nem biztosítja.",
    "electricity_price": "Opcionális aktuális villamosenergia-ár kWh-nként, csak az áttekintés kedvéért.",
    "reimbursement_rate": "Választható térítési díj kWh-nként, csak az áttekintés kedvéért.",
    "battery_capacity_kwh": "Használható akkumulátorkapacitás kWh-ban. Csak utazási és töltési előzményekhez szükséges.",
    "full_range_km": "Autója által mutatott hatótáv 100%-os töltöttség mellett, km-ben. Csak utazási és töltési előzményekhez szükséges.",
    "ledger_enabled": "Az utazásokat és a töltési előzményeket helyben tárolhatja a Home Assistant alkalmazásban. A letiltása nem törli a mentett előzményeket.",
    "costs": "Opcionális rögzített költség bemenetek. Adja meg mind az ötöt ugyanabból a könyvelési forrásból, vagy hagyja mindet üresen."
  },
  "lb": {
    "vehicle": "Optional. Loosst d’Feld eidel fir de passende NIO-Sensor ze benotzen. Wielt eng aner Home Assistant-Entitéit nëmme fir de NIO-Wäert ze ersetzen.",
    "evcc_connected": "Optionalen Sensor fir d’Verbindung mam Ladegerät. Akzeptéiert un/aus, verbonnen/getrennt oder richteg/falsch; EVCC ass net néideg.",
    "evcc_power": "Optionalen Leeschtungssensor vum Ladegerät a W oder kW. D’Leeschtung gëtt nieft dem Opluedstatus ugewisen.",
    "evcc_history": "Optional EVCC-kompatibel Historik vun Opluedsessiounen. Loosst d’Feld eidel, wann Äert Ladegerät dat net ubitt.",
    "electricity_price": "Optionalen aktuelle Stroumpräis pro kWh, nëmme fir den Iwwerbléck.",
    "reimbursement_rate": "Optionalen Remboursementstaux pro kWh, nëmme fir den Iwwerbléck.",
    "battery_capacity_kwh": "Notzbar Batteriekapazitéit a kWh. Nëmme fir d’Faart- an Opluedhistorik néideg.",
    "full_range_km": "Reechwäit, déi Ären Auto bei 100 % Ladung uweist, a km. Nëmme fir d’Faart- an Opluedhistorik néideg.",
    "ledger_enabled": "Späichert Faarten an Opluedsessioune lokal an Home Assistant. Desaktivéiere läscht déi gespäichert Historik net.",
    "costs": "Optional Donnéeë fir registréiert Käschten. Gitt all fënnef Wäerter aus där selwechter Comptabilitéitsquell un, oder loosst all Felder eidel."
  },
  "pl": {
    "vehicle": "Opcjonalne. Pozostaw puste, aby użyć odpowiedniego czujnika NIO. Wybierz inną encję Home Assistant tylko wtedy, gdy chcesz zastąpić wartość NIO.",
    "evcc_connected": "Opcjonalny czujnik podłączenia ładowarki. Akceptuje włączenie/wyłączenie, połączenie/rozłączenie lub prawda/fałsz; EVCC nie jest wymagane.",
    "evcc_power": "Opcjonalny czujnik mocy ładowarki w W lub kW. Jest to pokazane obok stanu ładowania.",
    "evcc_history": "Opcjonalna historia sesji ładowania zgodna z EVCC. Pozostaw puste, jeśli Twoja ładowarka tego nie zapewnia.",
    "electricity_price": "Opcjonalna aktualna cena energii elektrycznej za kWh, tylko poglądowa.",
    "reimbursement_rate": "Opcjonalna stawka zwrotu za kWh, tylko w celach poglądowych.",
    "battery_capacity_kwh": "Użyteczna pojemność akumulatora w kWh. Wymagane tylko w przypadku historii podróży i ładowania.",
    "full_range_km": "Zasięg samochodu przy 100% naładowaniu, w km. Wymagane tylko w przypadku historii podróży i ładowania.",
    "ledger_enabled": "Zapisuj historię podróży i ładowania lokalnie w Home Assistant. Wyłączenie tej opcji nie powoduje usunięcia zapisanej historii.",
    "costs": "Opcjonalne dane wejściowe dotyczące zarejestrowanych kosztów. Dostarcz wszystkie pięć z tego samego źródła rozliczeniowego lub pozostaw wszystkie puste."
  },
  "pt": {
    "vehicle": "Opcional. Deixe vazio para usar o sensor NIO correspondente. Selecione outra entidade Home Assistant apenas se precisar de substituir o valor do NIO.",
    "evcc_connected": "Sensor opcional de ligação ao carregador. Aceita on/off, connected/disconnected ou true/false; EVCC não é necessário.",
    "evcc_power": "Sensor opcional da potência do carregador em W ou kW. A potência aparece junto ao estado de carregamento.",
    "evcc_history": "Histórico opcional das sessões de carregamento compatível com EVCC. Deixe vazio se o carregador não o fornecer.",
    "electricity_price": "Preço atual da eletricidade por kWh, opcional e apenas para consulta.",
    "reimbursement_rate": "Taxa de reembolso por kWh, opcional e apenas para consulta.",
    "battery_capacity_kwh": "Capacidade útil da bateria em kWh. Só é necessária para o histórico de viagens e carregamentos.",
    "full_range_km": "Autonomia indicada pelo veículo com 100% de carga, em km. Só é necessária para o histórico de viagens e carregamentos.",
    "ledger_enabled": "Guarda localmente no Home Assistant o histórico de viagens e carregamentos. Desativar esta opção não apaga o histórico guardado.",
    "costs": "Dados opcionais de custos registados. Indique os cinco valores da mesma fonte de faturação ou deixe-os todos vazios."
  },
  "ro": {
    "vehicle": "Opțional. Lăsați gol pentru a utiliza senzorul NIO potrivit. Selectați o altă entitate Home Assistant numai dacă aveți nevoie de o modificare.",
    "evcc_connected": "Senzor opțional de conectare la încărcător. Acceptă on/off, conectat/deconectat sau adevărat/fals; EVCC nu este necesar.",
    "evcc_power": "Senzor opțional de putere a încărcătorului în W sau kW. Aceasta este afișată lângă starea de încărcare.",
    "evcc_history": "Istoricul sesiunilor de încărcare opțional compatibil EVCC. Lăsați gol dacă încărcătorul nu îl oferă.",
    "electricity_price": "Prețul curent al energiei electrice opțional pe kWh, doar pentru prezentare generală.",
    "reimbursement_rate": "Rata opțională de rambursare per kWh, numai pentru prezentare generală.",
    "battery_capacity_kwh": "Capacitatea bateriei utilizabilă în kWh. Necesar numai pentru istoricul călătoriilor și al încărcărilor.",
    "full_range_km": "Autonomie afișată de mașina dvs. la încărcare de 100%, în km. Necesar numai pentru istoricul călătoriilor și al încărcărilor.",
    "ledger_enabled": "Stochează călătoriile și istoricul de încărcare local în Home Assistant. Dezactivarea acestuia nu șterge istoricul salvat.",
    "costs": "Intrări opționale pentru costuri înregistrate. Furnizați toate cele cinci din aceeași sursă contabilă sau lăsați toate goale."
  }
};
const NIO_BACKUP_WORDS = {
  "en": [
    "Backup & restore",
    "Download backup",
    "Choose backup file",
    "Restore backup",
    "Backup contains {imported} trips and {charges} charging sessions; this car currently has {current} trips and {currentCharges} charging sessions. Restoring replaces existing history.",
    "Export your current data first. OAuth credentials are never included.",
    "Replace this car’s dashboard settings and saved history with the selected backup?",
    "Backup exceeds the 8 MB transfer limit",
    "Confirm the restore after reviewing its preview",
    "History changed since preview; review the restore again",
    "Backup history cannot be read by this version"
  ],
  "nl": [
    "Back-up en herstel",
    "Back-up downloaden",
    "Back-upbestand kiezen",
    "Back-up herstellen",
    "Back-up bevat {imported} ritten en {charges} laadsessies; deze auto heeft nu {current} ritten en {currentCharges} laadsessies. Herstel vervangt de bestaande historiek.",
    "Exporteer eerst je huidige gegevens. OAuth-gegevens zijn nooit inbegrepen.",
    "Dashboardinstellingen en opgeslagen historiek van deze auto vervangen door deze back-up?",
    "Back-up overschrijdt de overdrachtslimiet van 8 MB.",
    "Bevestig het herstel nadat je het voorbeeld hebt bekeken.",
    "De historiek is gewijzigd sinds het voorbeeld; bekijk het herstel opnieuw.",
    "De back-uphistoriek kan niet door deze versie worden gelezen."
  ],
  "de": [
    "Sicherung und Wiederherstellung",
    "Sicherung herunterladen",
    "Sicherungsdatei wählen",
    "Sicherung wiederherstellen",
    "Die Sicherung enthält {imported} Fahrten und {charges} Ladevorgänge. Dieses Fahrzeug hat derzeit {current} Fahrten und {currentCharges} Ladevorgänge. Beim Wiederherstellen wird der vorhandene Verlauf ersetzt.",
    "Aktuelle Daten zuerst exportieren. OAuth-Zugangsdaten sind nie enthalten.",
    "Einstellungen und Verlauf dieses Autos durch diese Sicherung ersetzen?",
    "Die Sicherung überschreitet das Übertragungslimit von 8 MB.",
    "Bestätige die Wiederherstellung, nachdem du die Vorschau geprüft hast.",
    "Der Verlauf wurde seit der Vorschau geändert; prüfe die Wiederherstellung erneut.",
    "Der Sicherungsverlauf kann von dieser Version nicht gelesen werden."
  ],
  "fr": [
    "Sauvegarde et restauration",
    "Télécharger la sauvegarde",
    "Choisir un fichier",
    "Restaurer",
    "La sauvegarde contient {imported} trajets et {charges} sessions de recharge. Cette voiture en compte actuellement {current} trajets et {currentCharges} sessions de recharge. La restauration remplace l’historique existant.",
    "Exportez d’abord vos données actuelles. Les identifiants OAuth ne sont jamais inclus.",
    "Remplacer les réglages et l’historique de cette voiture par cette sauvegarde ?",
    "La sauvegarde dépasse la limite de transfert de 8 Mo.",
    "Confirmez la restauration après avoir vérifié l’aperçu.",
    "L’historique a changé depuis l’aperçu ; vérifiez à nouveau la restauration.",
    "Cette version ne peut pas lire l’historique de la sauvegarde."
  ],
  "nb": [
    "Sikkerhetskopiering og gjenoppretting",
    "Last ned sikkerhetskopi",
    "Velg sikkerhetskopifil",
    "Gjenopprett sikkerhetskopi",
    "Sikkerhetskopien inneholder {imported} turer og {charges} ladeøkter. Denne bilen har nå {current} turer og {currentCharges} ladeøkter. Gjenoppretting erstatter den eksisterende historikken.",
    "Eksporter gjeldende data først. OAuth-legitimasjon er aldri inkludert.",
    "Vil du erstatte denne bilens dashbordinnstillinger og lagrede historikk med den valgte sikkerhetskopien?",
    "Sikkerhetskopien overskrider overføringsgrensen på 8 MB.",
    "Bekreft gjenopprettingen etter at du har gjennomgått forhåndsvisningen.",
    "Historikken er endret siden forhåndsvisningen; gå gjennom gjenopprettingen på nytt.",
    "Denne versjonen kan ikke lese sikkerhetskopihistorikken."
  ],
  "sv": [
    "Säkerhetskopiera och återställa",
    "Ladda ner säkerhetskopia",
    "Välj säkerhetskopia",
    "Återställ säkerhetskopia",
    "Säkerhetskopian innehåller {imported} resor och {charges} laddningssessioner. Bilen har för närvarande {current} resor och {currentCharges} laddningssessioner. Återställningen ersätter den befintliga historiken.",
    "Exportera din nuvarande data först. OAuth-uppgifter ingår aldrig.",
    "Ersätta den här bilens instrumentpanelsinställningar och sparade historik med den valda säkerhetskopian?",
    "Säkerhetskopian överskrider överföringsgränsen på 8 MB.",
    "Bekräfta återställningen efter att du har granskat förhandsvisningen.",
    "Historiken har ändrats sedan förhandsvisningen; granska återställningen igen.",
    "Den här versionen kan inte läsa säkerhetskopians historik."
  ],
  "da": [
    "Sikkerhedskopiering og gendannelse",
    "Download sikkerhedskopi",
    "Vælg backup-fil",
    "Gendan backup",
    "Sikkerhedskopien indeholder {imported} ture og {charges} opladningssessioner. Bilen har i øjeblikket {current} ture og {currentCharges} opladningssessioner. Gendannelsen erstatter den eksisterende historik.",
    "Eksportér dine nuværende data først. OAuth-legitimationsoplysninger er aldrig inkluderet.",
    "Vil du erstatte denne bils instrumentbrætindstillinger og gemte historik med den valgte backup?",
    "Sikkerhedskopien overskrider overførselsgrænsen på 8 MB.",
    "Bekræft gendannelsen efter at have gennemgået forhåndsvisningen.",
    "Historikken er ændret siden forhåndsvisningen; gennemgå gendannelsen igen.",
    "Denne version kan ikke læse sikkerhedskopiens historik."
  ],
  "cs": [
    "Zálohování a obnovení",
    "Stáhnout zálohu",
    "Vyberte záložní soubor",
    "Obnovit zálohu",
    "Záloha obsahuje {imported} jízd a {charges} nabíjecích relací. Toto vozidlo má nyní {current} jízd a {currentCharges} nabíjecích relací. Obnovení nahradí stávající historii.",
    "Nejprve exportujte svá aktuální data. Přihlašovací údaje OAuth nejsou nikdy zahrnuty.",
    "Nahradit nastavení palubní desky tohoto auta a uloženou historii vybranou zálohou?",
    "Záloha překračuje limit přenosu 8 MB.",
    "Po kontrole náhledu potvrďte obnovení.",
    "Historie se od náhledu změnila; znovu zkontrolujte obnovení.",
    "Tato verze nedokáže přečíst historii zálohy."
  ],
  "el": [
    "Δημιουργία αντιγράφων ασφαλείας και επαναφορά",
    "Λήψη αντιγράφου ασφαλείας",
    "Επιλέξτε αρχείο αντιγράφου ασφαλείας",
    "Επαναφορά αντιγράφου ασφαλείας",
    "Το αντίγραφο ασφαλείας περιέχει {imported} διαδρομές και {charges} συνεδρίες φόρτισης. Το όχημα έχει τώρα {current} διαδρομές και {currentCharges} συνεδρίες φόρτισης. Η επαναφορά αντικαθιστά το υπάρχον ιστορικό.",
    "Εξάγετε πρώτα τα τρέχοντα δεδομένα σας. Τα διαπιστευτήρια OAuth δεν περιλαμβάνονται ποτέ.",
    "Αντικατάσταση των ρυθμίσεων του ταμπλό και του αποθηκευμένου ιστορικού αυτού του αυτοκινήτου με το επιλεγμένο αντίγραφο ασφαλείας;",
    "Το αντίγραφο ασφαλείας υπερβαίνει το όριο μεταφοράς των 8 MB.",
    "Επιβεβαιώστε την επαναφορά αφού ελέγξετε την προεπισκόπηση.",
    "Το ιστορικό άλλαξε μετά την προεπισκόπηση· ελέγξτε ξανά την επαναφορά.",
    "Αυτή η έκδοση δεν μπορεί να διαβάσει το ιστορικό του αντιγράφου ασφαλείας."
  ],
  "hu": [
    "Biztonsági mentés és visszaállítás",
    "Biztonsági másolat letöltése",
    "Válassza ki a biztonsági mentési fájlt",
    "Biztonsági másolat visszaállítása",
    "A biztonsági másolat {imported} utazást és {charges} töltési alkalmat tartalmaz. Ennek az autónak jelenleg {current} utazása és {currentCharges} töltési alkalma van. A visszaállítás felváltja a meglévő előzményeket.",
    "Először exportálja jelenlegi adatait. Az OAuth hitelesítési adatokat soha nem tartalmazza.",
    "Lecseréli ennek az autónak a műszerfal beállításait és a mentett előzményeket a kiválasztott biztonsági másolatra?",
    "A biztonsági mentés meghaladja a 8 MB-os átviteli korlátot.",
    "Az előnézet áttekintése után erősítse meg a visszaállítást.",
    "Az előzmények megváltoztak az előnézet óta; tekintse át újra a visszaállítást.",
    "Ez a verzió nem tudja beolvasni a biztonsági mentés előzményeit."
  ],
  "lb": [
    "Backup a Restauratioun",
    "Backup eroflueden",
    "Backup-Datei auswielen",
    "Backup restauréieren",
    "De Backup enthält {imported} Faarten an {charges} Opluedsessiounen. Dësen Auto huet aktuell {current} Faarten an {currentCharges} Opluedsessiounen. D’Restauratioun ersetzt déi existent Historik.",
    "Exportéiert fir d’éischt Är aktuell Donnéeën. OAuth-Zougangsdonnéeë sinn ni abegraff.",
    "D’Dashboard-Astellungen an déi gespäichert Historik vun dësem Auto duerch de gewielte Backup ersetzen?",
    "De Backup iwwerschreit d'Iwwerdroungslimit vun 8 MB.",
    "Bestätegt d’Restauratioun nodeems Dir d’Virschau iwwerpréift hutt.",
    "D’Historik huet sech zënter der Virschau geännert; iwwerpréift d’Restauratioun nach eng Kéier.",
    "Dës Versioun kann d’Backup-Historik net liesen."
  ],
  "pl": [
    "Kopia zapasowa i przywracanie",
    "Pobierz kopię zapasową",
    "Wybierz plik kopii zapasowej",
    "Przywróć kopię zapasową",
    "Kopia zapasowa zawiera {imported} przejazdów i {charges} sesji ładowania. Ten samochód ma obecnie {current} przejazdów i {currentCharges} sesji ładowania. Przywrócenie zastąpi istniejącą historię.",
    "Najpierw wyeksportuj bieżące dane. Dane uwierzytelniające OAuth nigdy nie są uwzględniane.",
    "Zamienić ustawienia deski rozdzielczej i zapisaną historię tego samochodu na wybraną kopię zapasową?",
    "Kopia zapasowa przekracza limit transferu 8 MB.",
    "Potwierdź przywracanie po sprawdzeniu podglądu.",
    "Historia zmieniła się od czasu podglądu; sprawdź przywracanie ponownie.",
    "Ta wersja nie może odczytać historii kopii zapasowej."
  ],
  "pt": [
    "Cópia de segurança e restauro",
    "Transferir cópia de segurança",
    "Escolher ficheiro de cópia de segurança",
    "Restaurar cópia de segurança",
    "A cópia de segurança contém {imported} viagens e {charges} sessões de carregamento. Este veículo tem atualmente {current} viagens e {currentCharges} sessões de carregamento. O restauro substitui o histórico existente.",
    "Exporte primeiro os dados atuais. As credenciais OAuth nunca são incluídas.",
    "Substituir as definições do painel e o histórico guardado deste veículo pela cópia de segurança selecionada?",
    "A cópia de segurança excede o limite de transferência de 8 MB.",
    "Confirme o restauro depois de rever a pré-visualização.",
    "O histórico foi alterado desde a pré-visualização; reveja novamente o restauro.",
    "Esta versão não consegue ler o histórico da cópia de segurança."
  ],
  "ro": [
    "Copie de rezervă și restaurare",
    "Descărcați copia de rezervă",
    "Alegeți fișierul copiei de rezervă",
    "Restaurați copia de rezervă",
    "Copia de rezervă conține {imported} călătorii și {charges} sesiuni de încărcare. Mașina are în prezent {current} călătorii și {currentCharges} sesiuni de încărcare. Restaurarea înlocuiește istoricul existent.",
    "Exportați mai întâi datele curente. Datele de autentificare OAuth nu sunt niciodată incluse.",
    "Înlocuiți setările tabloului de bord ale acestei mașini și istoricul salvat cu copia de rezervă selectată?",
    "Copia de rezervă depășește limita de transfer de 8 MB.",
    "Confirmați restaurarea după ce verificați previzualizarea.",
    "Istoricul s-a schimbat de la previzualizare; verificați din nou restaurarea.",
    "Această versiune nu poate citi istoricul copiei de rezervă."
  ]
};

class NioVehicleCard extends HTMLElement {
  constructor(){super();this.attachShadow({mode:'open'});this.vehicles=[];this.loading=false;this.openDetails=false;this.error='';}
  setConfig(config){this.config=config||{};this.render();}
  getCardSize(){return 6;}
  getGridOptions(){return {columns:12,rows:'auto'};}
  static getConfigElement(){return document.createElement('nio-vehicle-card-editor');}
  static getStubConfig(){return {};}
  set hass(value){this._hass=value;if(!this.loaded&&!this.loading)this.load();else {this.updateValues();if(!this.artworkCatalogue)this.refreshArtwork();}}
  connectedCallback(){if(this.loaded){if(!this.artworkCatalogue)this.refreshArtwork();else if(!this.shadowRoot.querySelector('dialog[open]'))this.render();}else if(this._hass&&!this.loading)this.load();}
  async load(){if(!this._hass||this.loading)return;this.loading=true;try{const result=await this._hass.callWS({type:'nio_telematics/vehicle_dashboard/get'});this.vehicles=result.vehicles||[];this.loaded=true;this.error='';}catch(err){this.error=this.serviceErrorSummary(err);}finally{this.loading=false;this.render();}this.refreshArtwork();}
  refreshArtwork(){
    if(this._artworkLoading||this.artworkCatalogue)return;
    this._artworkLoading=true;
    nioLoadArtworkCatalogue().then(catalogue=>{
      if(!catalogue)return;
      this.artworkCatalogue=catalogue;
      if(!this.isConnected)return;
      const dialog=this.shadowRoot.querySelector('dialog[open]');
      if(dialog){
        const picker=dialog.querySelector('[name="paint"]');
        if(picker){const selected=picker.value,model=this.effectiveModel(dialog.querySelector('[name="model"]')?.value,this.vehicle?.name);picker.innerHTML=this.paintOptions(model,selected);picker.value=[...picker.options].some(item=>item.value===selected)?selected:'auto';}
        const carArt=this.shadowRoot.querySelector('.car-art'),model=this.modelFor?this.modelFor(this.vehicle):this.effectiveModel(this.vehicle?.preferences?.model,this.vehicle?.name);
        if(carArt)carArt.innerHTML=this.carImage?this.carImage(model,this.vehicle?.preferences?.paint):this.artwork(model,this.vehicle?.preferences?.paint);
        this._renderCatalogue=catalogue;
      }else this.render();
    }).finally(()=>{this._artworkLoading=false;});
  }
  get vehicle(){return this.vehicles.find(v=>v.entry_id===this.config?.entry_id)||this.vehicles[0];}
  get words(){const language=this.vehicle?.preferences?.language||'auto';const code=nioLocaleCode(language==='auto'?this._hass?.language||'en':language);const row=NIO_WORDS[code]||NIO_WORDS.en;const input=NIO_INPUT_LABELS[code]||NIO_INPUT_LABELS.en;return {...Object.fromEntries(NIO_KEYS.map((key,i)=>[key,row[i]])),...Object.fromEntries(['fullRange','ledgerEnabled','automatic','nativeDefault'].map((key,i)=>[key,(NIO_EXTRA[code]||NIO_EXTRA.en)[i]])),connected:input[0],power:input[1],history:input[2],sourceHint:NIO_SOURCE_HINT[code]||NIO_SOURCE_HINT.en,chargingUnknown:NIO_CHARGING_UNKNOWN[code]||NIO_CHARGING_UNKNOWN.en,connectedStatus:NIO_CONNECTED_STATUS[code]||NIO_CONNECTED_STATUS.en,helpAria:NIO_HELP_ARIA[code]||NIO_HELP_ARIA.en,errorFallback:NIO_ERROR_FALLBACK[code]||NIO_ERROR_FALLBACK.en};}
  markLocalizationRoot(){this.setAttribute?.('data-i18n-ignore','');this.setAttribute?.('translate','no');this.setAttribute?.('lang',this.locale());}
  serviceErrorSummary(error,locale=this.locale(),known={}){const message=String(error?.message||'');return known[message]||NIO_ERROR_FALLBACK[nioLocaleCode(locale)]||NIO_ERROR_FALLBACK.en;}
  esc(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  state(entity){return this._hass?.states[entity];}
  number(entity,digits=0){const state=this.state(entity)?.state;const value=Number(state);if(!state||['unknown','unavailable','none'].includes(state.toLowerCase())||!Number.isFinite(value))return null;return new Intl.NumberFormat(this.locale(),{maximumFractionDigits:digits,minimumFractionDigits:digits}).format(value);}
  powerKw(entity){const state=this.state(entity);const raw=state?.state;const value=Number(raw);if(!raw||!Number.isFinite(value)||['unknown','unavailable','none'].includes(raw.toLowerCase()))return null;const unit=String(state.attributes?.unit_of_measurement||'kW').toLowerCase();if(unit==='w')return value/1000;return unit==='kw'?value:null;}
  connectedState(entity){const value=this.state(entity)?.state;if(value==null)return null;if(/^(on|true|1|connected|plugged_in|plugged)$/i.test(value))return true;if(/^(off|false|0|disconnected|unplugged)$/i.test(value))return false;return null;}
  formatNumber(value,digits=1){return value===null?null:new Intl.NumberFormat(this.locale(),{maximumFractionDigits:digits,minimumFractionDigits:digits}).format(value);}
  evccPresets(){
    return Object.keys(this._hass?.states||{}).flatMap(id=>{
      const match=/^binary_sensor\.evcc_(.+)_connected$/.exec(id);
      if(!match)return [];
      const power=`sensor.evcc_${match[1]}_charge_power`;
      return this._hass.states[power]?[{name:match[1].replace(/_/g,' '),connected:id,power}]:[];
    });
  }
  fieldHelp(key, language){
    const message=(NIO_FIELD_HELP[language]||NIO_FIELD_HELP.en)[key]||NIO_FIELD_HELP.en[key];
    const code=nioLocaleCode(language);
    return `<details class="field-help"><summary aria-label="${this.esc(NIO_HELP_ARIA[code]||NIO_HELP_ARIA.en)}">?</summary><p>${this.esc(message)}</p></details>`;
  }
  locale(){const setting=this.vehicle?.preferences?.language||'auto';const locale=setting==='auto'?this._hass?.language||'en':setting;return nioLocaleTag(locale);}
  stamp(entity){const state=this.state(entity);const raw=state?.attributes?.last_valid_sample||state?.attributes?.source_sample;if(!raw)return null;const date=new Date(raw);return Number.isNaN(date.getTime())?null:new Intl.DateTimeFormat(this.locale(),{dateStyle:'short',timeStyle:'short'}).format(date);}
  artworkChoice(model,paint='auto'){
    const id=NIO_MODEL_IDS[model];
    const family=this.artworkCatalogue?.models?.find(item=>item.id===id);
    if(!family||(model==='ET5 Touring'&&paint==='auto'))return null;
    const choice=family.paints?.find(item=>item.id===(paint==='auto'?family.default_paint:paint));
    return choice&&typeof choice.file==='string'&&new RegExp(`^${id}/[a-z0-9-]+\\.[0-9a-f]{12}\\.webp$`).test(choice.file)?choice:null;
  }
  artworkImage(model,paint='auto'){
    const choice=this.artworkChoice(model,paint);
    return choice?`<img class="car-photo" src="/nio_telematics/artwork/${this.esc(choice.file)}" alt="${this.esc(model)} · ${this.esc(choice.label)}" loading="eager">`:null;
  }
  effectiveModel(selected,name=''){
    return selected&&selected!=='auto'?selected:[...NIO_MODELS].filter(item=>item!=='auto'&&item!=='other').sort((a,b)=>b.length-a.length).find(item=>name.toLowerCase().includes(item.toLowerCase()))||'NIO';
  }
  paintOptions(model,current='auto'){
    const code=nioLocaleCode(this.locale()),auto=(NIO_EXTRA[code]||NIO_EXTRA.en)[2];
    const family=this.artworkCatalogue?.models?.find(item=>item.id===NIO_MODEL_IDS[model]);
    const paints=family?.paints||[];
    return `<option value="auto" ${current==='auto'?'selected':''}>${this.esc(auto)}</option>`+paints.map(item=>`<option value="${this.esc(item.id)}" ${item.id===current?'selected':''}>${this.esc(item.label)}</option>`).join('');
  }
  artwork(model,paint='auto'){
    const image=this.artworkImage(model,paint);if(image)return image;
    const suv=/^(EL|ES)/.test(model),touring=/Touring/.test(model);
    const roof=suv?'M96 113 C112 69 137 62 178 62 L291 63 C319 67 337 85 350 112':touring?'M96 113 C112 81 141 72 183 72 L288 73 C314 76 336 93 350 112':'M96 113 C118 84 146 75 185 75 L272 76 C308 80 332 94 350 112';
    const glass=suv?'M112 111 C125 80 145 74 180 73 L286 74 C306 77 323 89 337 111 Z':touring?'M112 111 C127 87 148 82 181 82 L283 83 C304 85 321 95 336 111 Z':'M112 111 C130 89 150 84 183 84 L269 85 C299 88 317 97 334 111 Z';
    return `<svg viewBox="0 0 440 190" role="img" aria-label="${this.esc(model==='auto'?'NIO':model)}"><defs><linearGradient id="nio-paint" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#d4d9dc"/><stop offset=".55" stop-color="#adb6bb"/><stop offset="1" stop-color="#7f8b92"/></linearGradient><linearGradient id="nio-glass" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#80939f"/><stop offset="1" stop-color="#344752"/></linearGradient></defs><ellipse cx="220" cy="162" rx="184" ry="11" fill="#000" opacity=".10"/><path d="M49 118 Q67 113 96 113 ${roof.slice(8)} Q389 114 397 125 L401 146 Q397 153 386 153 H53 Q40 153 38 145 L41 128 Q42 121 49 118 Z" fill="url(#nio-paint)" stroke="#68757c" stroke-width="1.5"/><path d="${glass}" fill="url(#nio-glass)"/><path d="M216 77 L216 111 M102 114 H350 M49 132 L61 130 M373 127 L391 131" stroke="#72818a" stroke-width="1.3" fill="none"/><path d="M71 119 H382" stroke="#eef1f2" stroke-width="1.3" opacity=".65"/><path d="M40 140 H399" stroke="#5d6b72" opacity=".4"/><circle cx="117" cy="150" r="20" fill="#252e34"/><circle cx="117" cy="150" r="12" fill="#aab4b8"/><circle cx="117" cy="150" r="5" fill="#56656c"/><circle cx="343" cy="150" r="20" fill="#252e34"/><circle cx="343" cy="150" r="12" fill="#aab4b8"/><circle cx="343" cy="150" r="5" fill="#56656c"/></svg>`;
  }
  render(){if(!this.shadowRoot)return;this.markLocalizationRoot();const w=this.words,v=this.vehicle,e=v?.entities||{},p=v?.preferences||{};const soc=this.number(e.battery_state_of_charge,1),range=this.number(e.remaining_range),odo=this.number(e.odometer),limit=this.number(e.maximum_soc),power=this.formatNumber(this.powerKw(p.evcc_power));const sample=this.stamp(e.battery_state_of_charge)||this.stamp(e.remaining_range);const retained=Boolean(this.state(e.battery_state_of_charge)?.attributes?.data_retained);const chargingRaw=this.state(e.charging_state)?.state;const connected=this.connectedState(p.evcc_connected);const chargingStatus=nioChargingStatus(chargingRaw,this.powerKw(p.evcc_power),connected);const charging=chargingStatus==='charging'?w.charging:chargingStatus==='idle'?w.idle:null;const model=this.effectiveModel(p.model,v?.name||'');
    if(this.view==='history'&&v?.ledger_available){this.shadowRoot.innerHTML=`<style>${NioVehicleCard.styles}</style><ha-card><div class="wrap"><header><h2>${this.esc(w.chargeHistory)}</h2><button type="button" data-back aria-label="${this.esc(w.cancel)}">←</button></header><car-ledger-card></car-ledger-card></div></ha-card>`;const ledger=this.shadowRoot.querySelector('car-ledger-card');ledger.setConfig({entry_id:v.entry_id,language:this.locale()});ledger.hass=this._hass;this.shadowRoot.querySelector('[data-back]').onclick=()=>{this.view='overview';this.render();};return;}
    this.shadowRoot.innerHTML=`<style>${NioVehicleCard.styles}</style><ha-card><div class="wrap">${!v?`<p>${this.esc(this.error||w.noVehicle)}</p>`:`<header><div><span class="eyebrow">NIO</span><h2>${this.esc(v.name)}</h2></div><button type="button" data-action="settings" title="${this.esc(w.settings)}" aria-label="${this.esc(w.settings)}">⚙</button></header><div class="car-art">${this.artwork(model,p.paint||"auto")}</div><div class="hero"><div class="charge"><span>${this.esc(w.soc)}</span><strong>${soc??'—'}<small>${soc===null?'':'%'}</small></strong></div><div class="range"><span>${this.esc(w.range)}</span><strong>${range??'—'}<small>${range===null?'':' km'}</small></strong></div></div><div class="status">${this.esc([charging??w.chargingUnknown,connected===true?w.connectedStatus:null].filter(Boolean).join(" · "))}${power!==null?` · ${power} kW`:''}</div><div class="facts"><div><span>${this.esc(w.odometer)}</span><b>${odo??'—'}${odo===null?'':' km'}</b></div><div><span>${this.esc(w.limit)}</span><b>${limit??'—'}${limit===null?'':'%'}</b></div></div><footer><span>${this.esc(w.sample)} · ${sample?this.esc(sample):this.esc(w.unavailable)}${retained?' · ◷':''}</span><button type="button" data-action="details" aria-expanded="${this.openDetails}">${this.esc(w.details)}</button></footer>${this.openDetails?`<div class="detail">${p.evcc_history?`<p>${this.esc(w.history)}: ${this.esc(p.evcc_history)}</p>`:''}${p.electricity_price?`<p>${this.esc(w.price)}: ${this.esc(this.state(p.electricity_price)?.state||w.unavailable)}</p>`:''}${p.reimbursement_rate?`<p>${this.esc(w.reimbursement)}: ${this.esc(this.state(p.reimbursement_rate)?.state||w.unavailable)}</p>`:''}</div>`:''}`}</div></ha-card>`;
    this.shadowRoot.querySelector('[data-action="settings"]')?.addEventListener('click',()=>this.settings());this.shadowRoot.querySelector('[data-action="details"]')?.addEventListener('click',()=>{this.openDetails=!this.openDetails;this.render();});
    if(v?.ledger_available){const button=document.createElement('button');button.type='button';button.textContent=w.chargeHistory;button.onclick=()=>{this.view='history';this.render();};this.shadowRoot.querySelector('footer')?.append(button);}
  }
  updateValues(){if(!this.loaded||this.view==='history'||this.shadowRoot.querySelector('dialog'))return;const v=this.vehicle,e=v?.entities||{},p=v?.preferences||{};const ids=[e.battery_state_of_charge,e.remaining_range,e.odometer,e.maximum_soc,e.charging_state,p.evcc_connected,p.evcc_power,p.electricity_price,p.reimbursement_rate].filter(Boolean);const signature=ids.map(id=>{const s=this.state(id);return `${id}:${s?.state}:${s?.attributes?.unit_of_measurement}:${s?.attributes?.last_valid_sample}:${s?.attributes?.data_retained}`;}).join('|');if(signature!==this.displaySignature){this.displaySignature=signature;this.render();}}
  settings(){
    const v=this.vehicle;if(!v)return;
    const w=this.words,p=v.preferences||{};
    const vehicleFields=[['soc_entity',w.soc,'battery_state_of_charge'],['range_entity',w.range,'remaining_range'],['odometer_entity',w.odometer,'odometer'],['charging_state_entity',w.charging,'charging_state'],['charge_limit_entity',w.limit,'maximum_soc']];
    const householdFields=[['evcc_connected',w.connected],['evcc_power',w.power],['evcc_history',w.history],['electricity_price',w.price],['reimbursement_rate',w.reimbursement]];
    const inputLanguage=nioLocaleCode(this.locale());
    const costLabels=NIO_COST_INPUTS[inputLanguage]||NIO_COST_INPUTS.en;
    const backupWords=NIO_BACKUP_WORDS[inputLanguage]||NIO_BACKUP_WORDS.en;
    const backupError=error=>this.serviceErrorSummary(error,inputLanguage,{"Confirm the restore after reviewing its preview":backupWords[8],"History changed since preview; review the restore again":backupWords[9],"Backup history cannot be read by this version":backupWords[10]});
    const paintLabel=NIO_PAINT_LABELS[inputLanguage]||NIO_PAINT_LABELS.en;
    const costFields=['cost_energy','cost_solar','cost_total_cost','cost_grid_price','cost_export_price'].map((key,i)=>[key,costLabels[i+1]]);
    const fields=[...vehicleFields,...householdFields,...costFields];
    const entities=Object.keys(this._hass.states).sort();
    const presets=this.evccPresets();
    const options=entities.map(id=>`<option value="${this.esc(id)}"></option>`).join('');
    const dialog=document.createElement('dialog');
    const sourceInputs=vehicleFields.map(([key,label,nativeKey])=>`<div class="field-row"><label>${this.esc(label)}<input name="${key}" list="nio-entities" value="${this.esc(p[key]||'')}" placeholder="${this.esc(v.native_entities?.[nativeKey]||w.nativeDefault)}"></label>${this.fieldHelp('vehicle',inputLanguage)}</div>`).join('');
    const extraInputs=householdFields.map(([key,label])=>`<div class="field-row"><label>${this.esc(label)}<input name="${key}" list="nio-entities" value="${this.esc(p[key]||'')}"></label>${this.fieldHelp(key,inputLanguage)}</div>`).join('');
    const costInputs=`<details class="advanced"><summary>${this.esc(costLabels[0])}</summary><p class="source-hint">${this.esc((NIO_FIELD_HELP[inputLanguage]||NIO_FIELD_HELP.en).costs)}</p>${costFields.map(([key,label])=>`<label>${this.esc(label)}<input name="${key}" list="nio-entities" value="${this.esc(p[key]||'')}"></label>`).join('')}</details>`;
    const presetPicker=presets.length?`<label>${this.esc(NIO_EVCC_PROMPT[inputLanguage]||NIO_EVCC_PROMPT.en)}<select data-evcc-preset><option value="">—</option>${presets.map((item,i)=>`<option value="${i}">${this.esc(item.name)}</option>`).join('')}</select></label>`:'';
    dialog.innerHTML=`<style>.backup-file{position:relative;display:flex;align-items:center;min-height:44px;margin:16px 0;border:1px solid var(--divider-color,#8885);border-radius:12px;padding:10px 12px;cursor:pointer}.backup-file input[type=file]{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:pointer}.backup-file:focus-within{outline:2px solid var(--primary-color);outline-offset:2px}.backup-file [data-file-label]{overflow-wrap:anywhere;min-width:0}</style><form><h2>${this.esc(w.settings)}</h2><label>${this.esc(w.model)}<select name="model">${NIO_MODELS.map(m=>`<option value="${m}" ${m===p.model?'selected':''}>${this.esc(m==='auto'?w.automatic:m==='other'?(NIO_OTHER_MODEL[inputLanguage]||NIO_OTHER_MODEL.en):m)}</option>`).join('')}</select></label><label>${this.esc(paintLabel)}<select name="paint">${this.paintOptions(this.effectiveModel(p.model,v.name),p.paint||"auto")}</select></label><label>${this.esc(w.language)}<select name="language">${NIO_LANGUAGES.map(m=>`<option value="${m}" ${m===p.language?'selected':''}>${this.esc(m==='auto'?w.automatic:NIO_LANGUAGE_NAMES[m]||m)}</option>`).join('')}</select></label><datalist id="nio-entities">${options}</datalist><p class="source-hint">${this.esc(w.sourceHint||'Leave a vehicle source empty to use its NIO entity.')}</p>${sourceInputs}${presetPicker}${extraInputs}<label>${this.esc(w.capacity)} (kWh)<input name="battery_capacity_kwh" type="number" min="1" max="300" step="0.1" value="${p.battery_capacity_kwh??''}"></label><label>${this.esc(w.fullRange)} (km)<input name="full_range_km" type="number" min="1" max="2000" step="1" value="${p.full_range_km??''}"></label><label><input name="ledger_enabled" type="checkbox" ${p.ledger_enabled?'checked':''}> ${this.esc(w.ledgerEnabled)}</label>${costInputs}<p class="error" role="alert"></p><div class="actions"><button type="button" data-cancel>${this.esc(w.cancel)}</button><button type="submit">${this.esc(w.save)}</button></div></form>`;
    for(const key of ['battery_capacity_kwh','full_range_km','ledger_enabled']){
      dialog.querySelector(`[name="${key}"]`)?.closest('label')?.insertAdjacentHTML('afterend',this.fieldHelp(key,inputLanguage));
    }
    dialog.querySelector('.error').insertAdjacentHTML('beforebegin',`<details class="backup"><summary>${this.esc(backupWords[0])}</summary><p>${this.esc(backupWords[5])}</p><button type="button" data-export>${this.esc(backupWords[1])}</button><label class="backup-file"><span data-file-label>${this.esc(backupWords[2])}</span><input type="file" accept=".json,application/json" aria-label="${this.esc(backupWords[2])}" data-import></label><p data-backup-preview aria-live="polite"></p><button type="button" data-restore hidden>${this.esc(backupWords[3])}</button></details>`);
    let selectedBackup=null,backupPreview=null;
    const errorNode=dialog.querySelector('.error');
    dialog.querySelector('[data-export]').onclick=async()=>{
      errorNode.textContent='';
      try{
        const data=await this._hass.callWS({type:'nio_telematics/vehicle_dashboard/backup',entry_id:v.entry_id,action:'export'});
        const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
        const link=document.createElement('a');link.href=url;link.download=`nio-dashboard-${new Date().toISOString().slice(0,10)}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
      }catch(err){errorNode.textContent=backupError(err);}
    };
    dialog.querySelector('[data-import]').onchange=async event=>{
      selectedBackup=null;backupPreview=null;dialog.querySelector('[data-restore]').hidden=true;dialog.querySelector('[data-backup-preview]').textContent='';errorNode.textContent='';
      const file=event.target.files?.[0];dialog.querySelector('[data-file-label]').textContent=file?.name||backupWords[2];if(!file)return;
      if(file.size>8*1024*1024){errorNode.textContent=backupWords[7];return;}
      try{
        selectedBackup=JSON.parse(await file.text());
        backupPreview=await this._hass.callWS({type:'nio_telematics/vehicle_dashboard/backup',entry_id:v.entry_id,action:'preview',backup:selectedBackup});
        dialog.querySelector('[data-backup-preview]').textContent=backupWords[4].replace('{imported}',backupPreview.imported.trips).replace('{charges}',backupPreview.imported.charges).replace('{current}',backupPreview.current.trips).replace('{currentCharges}',backupPreview.current.charges);
        dialog.querySelector('[data-restore]').hidden=false;
      }catch(err){selectedBackup=null;backupPreview=null;errorNode.textContent=backupError(err);}
    };
    dialog.querySelector('[data-restore]').onclick=async()=>{
      if(!selectedBackup||!backupPreview||!window.confirm(backupWords[6]))return;
      errorNode.textContent='';
      try{
        const result=await this._hass.callWS({type:'nio_telematics/vehicle_dashboard/backup',entry_id:v.entry_id,action:'restore',backup:selectedBackup,expected_revision:backupPreview.current.revision,confirmation:'RESTORE'});
        this.vehicles=this.vehicles.map(old=>old.entry_id===v.entry_id?result.vehicle:old);dialog.close();this.render();
      }catch(err){errorNode.textContent=backupError(err);dialog.querySelector('[data-restore]').hidden=true;}
    };
    this.shadowRoot.append(dialog);
    dialog.querySelector('[name="model"]')?.addEventListener('change',event=>{
      const picker=dialog.querySelector('[name="paint"]'),previous=picker.value;
      const model=this.effectiveModel(event.target.value,v.name);
      picker.innerHTML=this.paintOptions(model,previous);
      if(![...picker.options].some(option=>option.value===previous))picker.value='auto';
    });
    dialog.querySelector('[data-evcc-preset]')?.addEventListener('change',event=>{if(event.target.value==='')return;const choice=presets[Number(event.target.value)];if(!choice)return;dialog.querySelector('[name="evcc_connected"]').value=choice.connected;dialog.querySelector('[name="evcc_power"]').value=choice.power;});
    dialog.querySelector('[data-cancel]').onclick=()=>dialog.close();dialog.addEventListener('close',()=>dialog.remove());
    dialog.querySelector('form').onsubmit=async event=>{event.preventDefault();const form=new FormData(event.target),preferences={};for(const [key] of fields)preferences[key]=String(form.get(key)||'').trim();preferences.model=String(form.get('model'));preferences.paint=String(form.get('paint')||'auto');preferences.language=String(form.get('language'));preferences.battery_capacity_kwh=form.get('battery_capacity_kwh')===''?null:Number(form.get('battery_capacity_kwh'));preferences.full_range_km=form.get('full_range_km')===''?null:Number(form.get('full_range_km'));preferences.ledger_enabled=form.has('ledger_enabled');try{const updated=await this._hass.callWS({type:'nio_telematics/vehicle_dashboard/save',entry_id:v.entry_id,preferences});this.vehicles=this.vehicles.map(old=>old.entry_id===v.entry_id?updated:old);dialog.close();this.render();}catch(err){dialog.querySelector('.error').textContent=this.serviceErrorSummary(err,inputLanguage);}};
    dialog.showModal();
  }
  static styles=`:host{display:block;color:var(--primary-text-color);font-family:var(--paper-font-body1_-_font-family,Arial,sans-serif)}*{box-sizing:border-box}ha-card{background:var(--card-background-color);border:1px solid var(--divider-color,#8884);border-radius:22px;overflow:hidden}.wrap{max-width:760px;margin:auto;padding:22px 24px 18px}header,footer,.facts,.hero{display:flex;align-items:center;justify-content:space-between;gap:16px}h2{font-size:21px;line-height:1.2;letter-spacing:-.03em;font-weight:500;margin:5px 0 0}.eyebrow{font-size:11px;letter-spacing:.15em;color:var(--secondary-text-color)}button{font:inherit;cursor:pointer;color:inherit}header button{border:1px solid var(--divider-color,#8884);background:transparent;border-radius:12px;width:34px;height:34px;font-size:18px}.car-art{display:grid;place-items:center;padding:10px 0 0}.car-art svg{width:min(100%,430px);height:auto;filter:drop-shadow(0 13px 11px #0002)}.hero{align-items:stretch;gap:10px;margin:4px 0 14px}.hero>div{flex:1;min-width:0;border:1px solid var(--divider-color,#8884);border-radius:16px;padding:15px 17px}.hero span,.facts span{display:block;color:var(--secondary-text-color);font-size:12px}.hero strong{display:block;margin-top:7px;font-size:36px;font-weight:500;line-height:1.1;letter-spacing:-.04em}.hero small{font-size:16px;font-weight:400;letter-spacing:0}.status{font-size:13px;padding:3px 1px 18px}.facts{border-top:1px solid var(--divider-color,#8884);padding:15px 1px}.facts>div{flex:1}.facts b{font-size:17px;font-weight:500}footer{border-top:1px solid var(--divider-color,#8884);padding-top:14px;color:var(--secondary-text-color);font-size:11px}footer button{background:transparent;border:1px solid var(--divider-color,#8884);border-radius:10px;padding:6px 11px;font-size:11px}.detail{padding-top:12px;font-size:12px;color:var(--secondary-text-color)}.detail p{margin:5px 0}dialog{border:1px solid var(--divider-color,#8884);border-radius:18px;padding:22px;width:min(92vw,430px);max-height:88dvh;background:var(--card-background-color);color:var(--primary-text-color)}dialog::backdrop{background:#0007}dialog h2{margin:0 0 12px}dialog label{display:block;font-size:12px;margin:12px 0}dialog input,dialog select{display:block;width:100%;margin-top:5px;padding:9px 10px;background:var(--card-background-color);color:var(--primary-text-color);border:1px solid var(--divider-color,#8886);border-radius:9px;font:inherit}dialog input[type=checkbox]{display:inline-block;width:16px;height:16px;vertical-align:middle;margin:0 7px 2px 0;padding:0;accent-color:var(--primary-color,#426b66)}.actions{display:flex;justify-content:flex-end;gap:8px;margin-top:17px}.actions button{border:1px solid var(--divider-color,#8886);border-radius:10px;background:var(--card-background-color);padding:9px 15px}.actions button[type=submit]{background:var(--primary-color,#426b66);color:white}.error{color:var(--error-color,#b44);font-size:12px}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--primary-color,#426b66)}@media(max-width:480px){.wrap{padding:17px 16px}.hero strong{font-size:30px}.hero>div{padding:12px}.facts b{font-size:15px}footer{align-items:flex-start}}`;
}
class NioVehicleCardEditor extends HTMLElement {
  constructor(){super();this.attachShadow({mode:'open'});}
  esc(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  markLocalizationRoot(){this.setAttribute?.('data-i18n-ignore','');this.setAttribute?.('translate','no');this.setAttribute?.('lang',nioLocaleTag(this._hass?.language||'en'));}
  setConfig(config){this.config=config||{};this.render();}
  set hass(value){const languageChanged=value?.language!==this._hass?.language;this._hass=value;if(!this.loaded)this.load();else if(languageChanged)this.render();}
  async load(){if(!this._hass||this.loading)return;this.loading=true;try{const data=await this._hass.callWS({type:'nio_telematics/vehicle_dashboard/get'});this.vehicles=data.vehicles||[];this.loaded=true;this.error=false;this.render();}catch(_error){this.error=true;this.render();}finally{this.loading=false;}}
  render(){if(!this.shadowRoot)return;this.markLocalizationRoot();const vehicles=this.vehicles||[];this.shadowRoot.innerHTML=`<style>:host{display:block;padding:12px 0}label{display:block;font-size:13px}select{display:block;margin-top:7px;width:100%;padding:10px;border:1px solid var(--divider-color,#8885);border-radius:9px;background:var(--card-background-color);color:var(--primary-text-color)}</style>${this.error?`<p role="alert">${this.esc(NIO_ERROR_FALLBACK[nioLocaleCode(this._hass?.language)]||NIO_ERROR_FALLBACK.en)}</p>`:''}<label>${(NIO_WORDS[nioLocaleCode(this._hass?.language||'en')]||NIO_WORDS.en)[21]}<select>${vehicles.map(v=>`<option value="${this.esc(v.entry_id)}" ${v.entry_id===this.config?.entry_id?'selected':''}>${this.esc(v.name)}</option>`).join('')}</select></label>`;this.shadowRoot.querySelector('select')?.addEventListener('change',event=>{this.config={...this.config,entry_id:event.target.value};this.dispatchEvent(new CustomEvent('config-changed',{detail:{config:this.config},bubbles:true,composed:true}));});}
}

/* Exact approved Car metric artwork. The compact card above stays compatible. */
const NIO_METRIC_ICONS = {"range":"<svg data-car-icon=\"range-nio-d\" viewBox=\"0 0 148 56\" fill=\"currentColor\" aria-hidden=\"true\"><path fill-rule=\"evenodd\" d=\"M123 4L133 4L133 5L135 5L135 6L136 6L136 46L137 46L137 47L138 47L138 49L137 49L137 50L119 50L119 47L120 47L120 7L121 7L121 5L123 5ZM47 13L53 13L53 14L54 14L54 15L55 15L55 17L59 17L59 18L62 18L62 19L64 19L64 20L65 20L65 21L67 21L67 22L68 22L68 23L70 23L70 24L71 24L71 25L73 25L73 26L80 26L80 27L83 27L83 28L85 28L85 29L87 29L87 30L88 30L88 31L89 31L89 33L90 33L90 34L91 34L91 36L90 36L90 39L89 39L89 41L90 41L90 43L88 43L88 44L83 44L83 45L82 45L82 43L83 43L83 38L82 38L82 36L81 36L81 35L80 35L80 34L78 34L78 33L71 33L71 34L70 34L70 35L69 35L69 36L68 36L68 37L67 37L67 40L66 40L66 43L67 43L67 44L30 44L30 45L29 45L29 38L28 38L28 36L27 36L27 35L26 35L26 34L25 34L25 33L18 33L18 34L16 34L16 35L15 35L15 36L14 36L14 38L13 38L13 44L12 44L12 43L8 43L8 42L6 42L6 40L5 40L5 37L4 37L4 35L5 35L5 34L6 34L6 29L10 29L10 28L6 28L6 25L8 25L8 24L9 24L9 23L10 23L10 22L11 22L11 21L13 21L13 20L12 20L12 18L18 18L18 17L20 17L20 16L22 16L22 17L25 17L25 16L33 16L33 15L46 15L46 14L47 14ZM138 15L140 15L140 16L141 16L141 18L142 18L142 21L143 21L143 25L144 25L144 45L143 45L143 46L140 46L140 45L139 45L139 42L140 42L140 43L141 43L141 44L142 44L142 25L141 25L141 21L140 21L140 19L139 19L139 18L138 18ZM128 17L128 19L127 19L127 21L126 21L126 22L125 22L125 24L124 24L124 25L125 25L125 26L127 26L127 28L126 28L126 31L125 31L125 32L127 32L127 31L128 31L128 29L129 29L129 28L130 28L130 26L131 26L131 25L132 25L132 23L129 23L129 21L130 21L130 18L131 18L131 17ZM33 19L33 20L30 20L30 21L29 21L29 26L44 26L44 19ZM46 19L46 26L55 26L55 27L63 27L63 25L62 25L62 24L60 24L60 23L59 23L59 22L56 22L56 21L54 21L54 20L48 20L48 19ZM58 19L57 19L57 20L58 20L58 21L60 21L60 22L62 22L62 23L64 23L64 24L65 24L65 25L66 25L66 26L68 26L68 25L67 25L67 24L66 24L66 23L64 23L64 22L63 22L63 21L61 21L61 20L58 20ZM26 20L26 21L21 21L21 22L19 22L19 23L16 23L16 25L23 25L23 26L26 26L26 25L27 25L27 22L28 22L28 20ZM106 25L108 25L108 26L109 26L109 27L110 27L110 28L111 28L111 29L112 29L112 30L111 30L111 31L110 31L110 32L109 32L109 33L108 33L108 34L107 34L107 35L106 35L106 33L107 33L107 32L108 32L108 31L97 31L97 29L108 29L108 28L107 28L107 27L106 27ZM20 34L22 34L22 35L25 35L25 36L26 36L26 38L27 38L27 45L26 45L26 46L25 46L25 47L24 47L24 48L18 48L18 47L17 47L17 46L16 46L16 45L15 45L15 38L16 38L16 37L17 37L17 36L18 36L18 35L20 35ZM73 34L76 34L76 35L78 35L78 36L79 36L79 37L80 37L80 38L81 38L81 44L80 44L80 46L79 46L79 47L77 47L77 48L72 48L72 47L70 47L70 46L69 46L69 44L68 44L68 39L69 39L69 37L70 37L70 36L71 36L71 35L73 35ZM75 36L74 36L74 37L73 37L73 38L75 38L75 40L77 40L77 39L78 39L78 38L76 38L76 37L75 37ZM18 37L18 40L20 40L20 37ZM24 37L23 37L23 38L22 38L22 39L23 39L23 40L25 40L25 38L24 38ZM71 38L71 40L73 40L73 38ZM78 41L77 41L77 42L76 42L76 43L79 43L79 42L78 42ZM17 42L17 44L19 44L19 43L20 43L20 46L22 46L22 43L20 43L20 42ZM23 42L23 44L25 44L25 42ZM70 42L70 43L71 43L71 44L72 44L72 43L73 43L73 42ZM74 43L74 44L73 44L73 46L76 46L76 43Z\"/></svg>","odometer":"<svg data-car-icon=\"odometer\" viewBox=\"0 0 32 24\" fill=\"currentColor\" aria-hidden=\"true\"><text x=\"16\" y=\"16\" text-anchor=\"middle\" font-family=\"Segoe UI,Arial,sans-serif\" font-size=\"11\" font-weight=\"400\">ODO</text></svg>","forecast":"<svg data-car-icon=\"charge-forecast\" viewBox=\"0 0 32 32\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><rect x=\"2\" y=\"7\" width=\"25\" height=\"18\" rx=\"3\"/><path d=\"M30 12v8M6 21l4-3 3 1 4-4 3 1 3-5\"/><circle cx=\"23\" cy=\"11\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/></svg>"};
const NIO_POWER_ICON = '<svg data-car-icon="power-plug" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3v5M16 3v5M6 8h12v4a6 6 0 0 1-12 0zM12 18v3"/></svg>';
/* Opt-in, app-like presentation. */
class NioVehicleDashboard extends NioVehicleCard {
  getCardSize(){return 10;}
  getGridOptions(){return {columns:12,rows:'auto'};}
  rangeIcon(model){
    // A model-specific silhouette must never be shown for a different car.
    return model==='ET5 Touring'?NIO_METRIC_ICONS.range:'<ha-icon icon="mdi:map-marker-distance" aria-hidden="true"></ha-icon>';
  }
  locale(){
    const setting=this.config?.language;
    const locale=setting&&setting!=='auto'?setting:super.locale();
    return nioLocaleTag(locale);
  }
  get words(){
    const code=nioLocaleCode(this.locale());
    const row=NIO_WORDS[code]||NIO_WORDS.en;
    const base={...Object.fromEntries(NIO_KEYS.map((key,i)=>[key,row[i]])),...Object.fromEntries(['fullRange','ledgerEnabled','automatic','nativeDefault'].map((key,i)=>[key,(NIO_EXTRA[code]||NIO_EXTRA.en)[i]])),errorFallback:NIO_ERROR_FALLBACK[code]||NIO_ERROR_FALLBACK.en};
    const extra={
      en:['Connected','Vehicle history','History is optional. Enable it in Settings.','Vehicle data unavailable'],
      nl:['Verbonden','Autohistoriek','Historiek is optioneel. Schakel die in bij Instellingen.','Autogegevens niet beschikbaar'],
      de:['Verbunden','Fahrzeugverlauf','Der Verlauf ist optional. Aktiviere ihn in den Einstellungen.','Fahrzeugdaten nicht verfügbar'],
      fr:['Connecté','Historique du véhicule','L’historique est facultatif. Activez-le dans les paramètres.','Données du véhicule indisponibles'],
      nb:['Tilkoblet','Kjøretøyhistorikk','Historikk er valgfritt. Aktiver den i innstillingene.','Kjøretøydata er ikke tilgjengelige'],
      sv:['Ansluten','Fordonshistorik','Historik är valfri. Aktivera den i inställningarna.','Fordonsdata är inte tillgängliga'],
      da:['Tilsluttet','Køretøjshistorie','Historik er valgfri. Aktivér den i indstillingerne.','Køretøjsdata er ikke tilgængelige'],
      cs:['Připojeno','Historie vozidla','Historie je volitelná. Povolte ji v nastavení.','Údaje o vozidle nejsou k dispozici'],
      el:['Συνδεδεμένο','Ιστορικό οχήματος','Το ιστορικό είναι προαιρετικό. Ενεργοποιήστε το στις ρυθμίσεις.','Τα δεδομένα του οχήματος δεν είναι διαθέσιμα'],
      hu:['Csatlakoztatva','Járműelőzmények','Az előzmények használata nem kötelező. Engedélyezze a beállításokban.','A jármű adatai nem érhetők el'],
      lb:['Verbonnen','Gefiergeschicht',"D'Historik ass fakultativ. Aktivéiert se an den Astellungen.",'Gefierdaten net verfügbar'],
      pl:['Połączono','Historia pojazdu','Historia jest opcjonalna. Włącz ją w ustawieniach.','Dane pojazdu są niedostępne'],
      pt:['Ligado','Histórico do veículo','O histórico é opcional. Ative-o nas definições.','Dados do veículo indisponíveis'],
      ro:['Conectat','Istoricul vehiculului','Istoricul este opțional. Activați-l în setări.','Datele vehiculului nu sunt disponibile'],
    }[code]||['Connected','Vehicle history','History is optional. Enable it in Settings.','Vehicle data unavailable'];
    const tabs={
      en:['Charging','Trips','Consumption','Parked'],nl:['Laden','Ritten','Verbruik','Stilstand'],
      de:['Laden','Fahrten','Verbrauch','Parken'],fr:['Recharge','Trajets','Consommation','Stationnement'],
      nb:['Lading','Turer','Forbruk','Parkert'],sv:['Laddning','Resor','Förbrukning','Parkerad'],
      da:['Opladning','Ture','Forbrug','Parkeret'],cs:['Nabíjení','Jízdy','Spotřeba','Zaparkováno'],
      el:['Φόρτιση','Ταξίδια','Κατανάλωση','Σταθμευμένο'],hu:['Töltés','Utak','Fogyasztás','Parkolt'],
      lb:['Laden','Reesen','Verbrauch','Parkéiert'],pl:['Ładowanie','Przejazdy','Zużycie','Zaparkowany'],
      pt:['Carregamento','Viagens','Consumo','Estacionado'],ro:['Încărcare','Călătorii','Consum','Parcată'],
    }[code]||['Charging','Trips','Consumption','Parked'];
    const input=NIO_INPUT_LABELS[code]||NIO_INPUT_LABELS.en;
    const ui=NIO_DASHBOARD_UI[code]||NIO_DASHBOARD_UI.en;
    return {...base,connected:input[0],power:input[1],history:input[2],sourceHint:NIO_SOURCE_HINT[code]||NIO_SOURCE_HINT.en,chargingUnknown:NIO_CHARGING_UNKNOWN[code]||NIO_CHARGING_UNKNOWN.en,connectedStatus:NIO_CONNECTED_STATUS[code]||NIO_CONNECTED_STATUS.en,vehicleHistory:extra[1],historyOptional:extra[2],noData:extra[3],retry:NIO_DASHBOARD_RETRY[code]||NIO_DASHBOARD_RETRY.en,historyTabs:tabs,dashboardUI:ui,dashboardSolarShare:NIO_DASHBOARD_SOLAR[code]||NIO_DASHBOARD_SOLAR.en,dashboardSettingsIntro:NIO_DASHBOARD_SETTINGS_INTRO[code]||NIO_DASHBOARD_SETTINGS_INTRO.en,dashboardHistoryIntro:NIO_DASHBOARD_HISTORY_INTRO[code]||NIO_DASHBOARD_HISTORY_INTRO.en};
  }
  carImage(model,paint='auto'){
    const image=this.artworkImage(model,paint);if(image)return image;
    if(model==='ET5 Touring')return '<img class="car-photo" src="/nio_telematics/et5-touring-studio.png" alt="ET5 Touring" loading="eager">';
    // Do not imply that a generic drawing depicts another NIO model.
    return `<div class="car-placeholder" role="img" aria-label="${this.esc(model)}"><svg viewBox="0 0 64 52" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M28 8V5q0-2 2-2h4q2 0 2 2v3h8q5 0 7 5l5 11q5 4 5 10v13q0 3-3 3h-6q-3 0-3-4H15q0 4-3 4H6q-3 0-3-3V34q0-6 5-10l5-11q2-5 7-5Zm-9 5-5 11h36l-5-11q-13-2-26 0ZM9 30q1 3 14 4v-2Zm46 0-14 2v2q13-1 14-4ZM10 38l-1 6q5-5 1-6Zm44 0q-4 1 1 6Zm-30 5-4 3h24l-4-3Zm5-8q3-4 6 0l-2 1q-1-2-2 0Zm1 3q2-3 4 0l-2-1Z"/><path d="M8 20q-7-4-8 2 0 3 7 3Zm48 0q7-4 8 2 0 3-7 3Z"/></svg><span>${this.esc(model)}</span></div>`;
  }
  modelFor(v){
    const chosen=this.config?.model&&this.config.model!=='auto'?this.config.model:v.preferences?.model;
    return this.effectiveModel(chosen,v.name);
  }
  selectScreen(screen){if(!['car','history','settings'].includes(screen))screen='car';this.screen=screen;const root=this.shadowRoot?.querySelector('.dashboard[data-entry-id]');if(!root)return;root.dataset.screen=screen;for(const panel of root.querySelectorAll('[data-panel]'))panel.hidden=panel.dataset.panel!==screen;for(const button of root.querySelectorAll('.primary-navigation [data-screen-target]')){if(button.dataset.screenTarget===screen)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');}}
  navigate(screen){this.selectScreen(screen);const root=this.shadowRoot?.querySelector('.dashboard[data-entry-id]');const target=this.screen==='car'?root:root?.querySelector(`[data-panel="${this.screen}"]`);target?.scrollIntoView?.({block:'start'});}
  render(){
 if(!this.shadowRoot)return;this.markLocalizationRoot();const v=this.vehicle,w=this.words,ui=w.dashboardUI||NIO_DASHBOARD_UI.en,screen=this.screen||'car';
 if(!v){this.shadowRoot.innerHTML=`<style>${NioVehicleDashboard.styles}${NioVehicleDashboard.appStyles}</style><ha-card class="dashboard"><p class="empty">${this.esc(this.error||w.noVehicle)}</p></ha-card>`;return;}
 const model=this.modelFor(v),language=this.locale(),paint=v.preferences?.paint||'auto',root=this.shadowRoot.querySelector('.dashboard[data-entry-id]');
 if(root?.dataset.entryId===v.entry_id&&this._renderModel===model&&this._renderPaint===paint&&this._renderCatalogue===this.artworkCatalogue&&this._renderLanguage===language&&this._renderLedger===Boolean(v.ledger_available)){this.updateDisplay();this.updateDashboardDetails();this.selectScreen(screen);return;}
 this._renderModel=model;this._renderPaint=paint;this._renderCatalogue=this.artworkCatalogue;this._renderLanguage=language;this._renderLedger=Boolean(v.ledger_available);
 const mark='<svg class="nio-mark" viewBox="66 90 368 344" aria-hidden="true"><path d="m334.64 261.9c-12.44-12.44-11.39-12-29-12h-111.64c-17.62 0-16.57-.43-29 12l-59.52 59.53a161.1 161.1 0 0 0 60.34 65.93c15.25-15.24 61-60.95 68.57-68.57 6.25-6.24 9-8.66 12.39-9.7a9.87 9.87 0 0 1 3-.56 9.71 9.71 0 0 1 3 .56c3.39 1 6.15 3.46 12.39 9.7l68.57 68.57a161.06 161.06 0 0 0 60.35-65.93z"/><path d="m173.62 244.05c4.49-4.85 3.86-9 8.26-20.37a72.81 72.81 0 0 1 135.86 0c4.41 11.41 3.78 15.52 8.27 20.37s9 5.84 23.28 5.84h61.63a161.11 161.11 0 0 0 -322.21 0h61.63c14.3 0 18.9-1.11 23.28-5.84"/></svg>';
 const nav=[['car',ui[0],NIO_DASHBOARD_ICONS.car],['history',ui[1],NIO_DASHBOARD_ICONS.history],['settings',ui[2],NIO_DASHBOARD_ICONS.settings]];
 this.shadowRoot.innerHTML=`<style>${NioVehicleDashboard.styles}${NioVehicleDashboard.appStyles}</style><ha-card class="dashboard" data-entry-id="${this.esc(v.entry_id)}" data-screen="${this.esc(screen)}">
 <header class="app-header"><div class="identity">${mark}<h2>${this.esc(v.name)}</h2></div><button class="settings" type="button" data-screen-target="settings" aria-label="${this.esc(ui[2])}" title="${this.esc(ui[2])}">${NIO_DASHBOARD_ICONS.settings}</button></header>
 <section class="vehicle-overview" aria-label="${this.esc(ui[0])}"><div class="hero-car ${model==='ET5 Touring'?'touring':''}">${model==='ET5 Touring'&&paint==='auto'?'<svg class="hero-crop" viewBox="75 175 791 330" role="img" aria-label="ET5 Touring"><image href="/nio_telematics/artwork/et5-touring/approved-hero.png" width="960" height="540"/></svg>':this.carImage(model,paint)}</div>
 <div class="odo-caption"><span class="metric-icon" aria-hidden="true">${NIO_METRIC_ICONS.odometer}</span><strong data-value="odometer">—</strong><button type="button" data-reading-details>${this.esc(w.details)}</button></div>
 <div class="range-grid"><div class="battery"><span class="battery-label">${this.esc(w.soc)}</span><strong data-value="soc">—</strong></div><div class="range-stack"><div class="range-label">${this.rangeIcon(model)}<span>${this.esc(w.range)}</span></div><div class="range-row native-range"><span>NIO</span><strong data-value="range">—</strong></div><div class="range-row calculated"><span>${this.esc(ui[11])}</span><button type="button" class="calculated-value" data-action="calculated"><strong data-value="calculated-range">—</strong><small data-range-note>${this.esc(ui[13])}</small></button></div></div></div>
 <div class="charge-title"><h3><span class="connection-icon" data-connection-icon aria-hidden="true">${NIO_DASHBOARD_ICONS.ac}</span><span data-value="status">—</span></h3></div><div class="metrics"><div><span data-value="third-label">${this.esc(w.limit)}</span><strong data-value="third">—</strong></div><div><span>${NIO_DASHBOARD_ICONS.received} ${this.esc(ui[15])}</span><strong data-value="received">—</strong></div><div><span>${NIO_DASHBOARD_ICONS.solar} ${this.esc(w.dashboardSolarShare)}</span><strong data-value="solar">—</strong></div></div><div class="charge-limit" data-charge-limit-row hidden><span>${this.esc(w.limit)}</span><span data-value="charge-limit">—</span></div><p class="sample-note"><span>${this.esc(w.sample)}</span> <span data-value="sample">—</span></p><p class="retained-note" data-value="retained"></p><details class="vehicle-details"><summary>${this.esc(w.details)}</summary><div data-details></div></details></section>
 <nav class="primary-navigation" aria-label="${this.esc(ui[2])}">${nav.map(([key,label,icon])=>`<button type="button" data-screen-target="${key}" ${key===screen?'aria-current="page"':''}><span class="navigation-icon" aria-hidden="true">${icon}</span><span>${this.esc(label)}</span></button>`).join('')}</nav>
 <main class="screen-panel history-panel" data-panel="history" hidden><div class="section-intro"><h2>${this.esc(ui[1])}</h2><p>${this.esc(w.dashboardHistoryIntro)}</p></div><div data-history></div></main>
 <main class="screen-panel settings-panel" data-panel="settings" hidden><div class="section-intro"><h2>${this.esc(ui[2])}</h2><p>${this.esc(w.dashboardSettingsIntro)}</p></div><div class="settings-menu">${[['appearance',3,7],['readings',4,8],['charger',5,9],['history',6,10]].map(([key,title,description])=>`<button type="button" class="menu-row" data-settings-group="${key}"><span><strong>${this.esc(ui[title])}</strong><small>${this.esc(ui[description])}</small></span><span class="menu-chevron" aria-hidden="true">${NIO_DASHBOARD_ICONS.chevron}</span></button>`).join('')}</div></main>
 </ha-card>`;
 this._historySnapshot=null;this.shadowRoot.querySelectorAll('[data-screen-target]').forEach(button=>button.addEventListener('click',()=>this.navigate(button.dataset.screenTarget)));this.shadowRoot.querySelectorAll('[data-settings-group]').forEach(button=>button.addEventListener('click',()=>this.settings(button.dataset.settingsGroup)));
 this.shadowRoot.querySelector('[data-action="calculated"]')?.addEventListener('click',()=>this.openCalculatedRange());this.shadowRoot.querySelector('[data-reading-details]')?.addEventListener('click',()=>this.shadowRoot.querySelector('.vehicle-details')?.toggleAttribute('open'));this.updateDisplay();this.updateDashboardDetails();this.selectScreen(screen);if(v.ledger_available)this.ensureLedger(v.entry_id);else this.renderHistoryUnavailable();
}
  renderHistoryUnavailable(){const host=this.shadowRoot.querySelector('[data-history]');if(!host)return;const ui=this.words.dashboardUI||NIO_DASHBOARD_UI.en,enabled=Boolean(this.vehicle?.ledger_available),message=enabled?ui[20]:this.words.historyOptional;host.innerHTML=`<p class="history-empty">${this.esc(message)}</p><button type="button" class="history-setup">${this.esc(enabled?(this.words.retry||'Retry'):ui[19])}</button>`;host.querySelector('button').onclick=()=>enabled?this.ensureLedger(this.vehicle.entry_id,true):this.selectScreen('settings');}
  async openCalculatedRange(){this.navigate('history');const history=this.shadowRoot.querySelector('nio-dashboard-history');if(history){history.tab='insight';history.scope='month';history.period='month';history.anchor=null;await history.refresh();}}
  async ensureLedger(entryId,retry=false){
 const host=this.shadowRoot.querySelector('[data-history]');if(!host)return;
 if(!customElements.get('nio-dashboard-history')){try{const url=this.config?.history_url||'/nio_telematics/nio-dashboard-history.js';await import(retry?`${url}${url.includes('?')?'&':'?'}retry=${Date.now()}`:url);}catch(_){this.renderHistoryUnavailable();return;}}
 if(this.vehicle?.entry_id!==entryId||!host.isConnected)return;
 const existing=host.querySelector('nio-dashboard-history');if(existing){existing.hass=this._hass;return;}
 const history=document.createElement('nio-dashboard-history');history.setConfig({entry_id:entryId,language:this.locale(),base_url:this.config?.history_base_url});
 history.addEventListener('nio-history-updated',event=>{if(event.detail?.entry_id!==entryId)return;this._historySnapshot=event.detail.snapshot||null;this.updateDashboardDetails();});host.replaceChildren(history);history.hass=this._hass;
}
  updateDashboardDetails(){
 const root=this.shadowRoot?.querySelector('.dashboard[data-entry-id]');if(!root)return;const v=this.vehicle,w=this.words,ui=w.dashboardUI||NIO_DASHBOARD_UI.en,p=v?.preferences||{};
 const details=root.querySelector('[data-details]'),rows=[[w.history,p.evcc_history],[w.price,p.electricity_price],[w.reimbursement,p.reimbursement_rate]].filter(([,id])=>id);
 details.innerHTML=rows.length?rows.map(([label,id])=>`<p><span>${this.esc(label)}</span><strong>${this.esc(this.state(id)?.state||w.unavailable)}</strong></p>`).join(''):`<p>${this.esc(w.unavailable)}</p>`;
 const activeCurrent=this._historySnapshot?.active_home_charge;
 const received=root.querySelector('[data-value="received"]'),solar=root.querySelector('[data-value="solar"]');if(received){received.textContent=activeCurrent?.kwh==null?'—':`${this.formatNumber(Number(activeCurrent.kwh),1)} kWh`;if(activeCurrent?.kwh!=null)received.innerHTML=`${this.esc(this.formatNumber(Number(activeCurrent.kwh),1))} <small>kWh</small>`;}if(solar){solar.textContent=activeCurrent?.solar_pct==null?'—':`${this.formatNumber(Number(activeCurrent.solar_pct),0)}%`;if(activeCurrent?.solar_pct!=null)solar.innerHTML=`${this.esc(this.formatNumber(Number(activeCurrent.solar_pct),0))}<small>%</small>`;}const range=this._historySnapshot?.statistics?.month?.projected_range_km,calc=root.querySelector('[data-value="calculated-range"]'),note=root.querySelector('[data-range-note]');
 if(Number.isFinite(range)){const value=this.formatNumber(range,0);calc.innerHTML=`${this.esc(value)}<small> km</small>`;calc.setAttribute('aria-label',`${ui[11]} ${value} km`);if(note){note.textContent=ui[12];note.classList?.add('sr-only');}}else{calc.textContent='—';calc.setAttribute('aria-label',`${ui[11]} —`);if(note){note.textContent=ui[13];note.classList?.remove('sr-only');}}
}
  updateValues(){
 if(!this.loaded)return;const history=this.shadowRoot?.querySelector('nio-dashboard-history');if(history)history.hass=this._hass;
 const before=this.displaySignature;this.updateDisplay();const v=this.vehicle,p=v?.preferences||{},e=v?.entities||{},ids=[e.battery_state_of_charge,e.remaining_range,e.odometer,e.maximum_soc,e.charging_state,this.config?.evcc_connected||p.evcc_connected,this.config?.evcc_power||p.evcc_power].filter(Boolean);
 const signature=ids.map(id=>{const s=this.state(id);return `${id}:${s?.state}:${s?.attributes?.unit_of_measurement}:${s?.attributes?.last_valid_sample}:${s?.attributes?.data_retained}`;}).join('|');if(signature!==before){this.displaySignature=signature;this.updateDashboardDetails();}
}
  stamp(entity){const raw=this.state(entity)?.attributes?.last_valid_sample||this.state(entity)?.attributes?.source_sample;if(!raw)return null;const date=new Date(raw);return Number.isNaN(date.getTime())?null:new Intl.DateTimeFormat(this.locale(),{dateStyle:'short',timeStyle:'short',hour12:false,timeZone:this._hass?.config?.time_zone||'UTC'}).format(date);}
  updateDisplay(){
 const v=this.vehicle,root=this.shadowRoot?.querySelector('.dashboard[data-entry-id]');if(!v||!root)return;
 const w=this.words,e=v.entities||{},p=v.preferences||{},powerEntity=this.config?.evcc_power||p.evcc_power,connectedEntity=this.config?.evcc_connected||p.evcc_connected;
 const soc=this.number(e.battery_state_of_charge,1),range=this.number(e.remaining_range),odo=this.number(e.odometer),limit=this.number(e.maximum_soc),powerKw=this.powerKw(powerEntity),power=this.formatNumber(powerKw);
 const state=id=>this.state(id)?.state,native=state(e.charging_state)||'',connected=this.connectedState(connectedEntity),classification=nioChargingStatus(native,powerKw,connected);
 const status=[classification==='charging'?w.charging:classification==='idle'?w.idle:w.chargingUnknown,connected===true?w.connectedStatus:null].filter(Boolean).join(' · ');
 const values={soc:soc===null?'—':`${soc.replace(/[,.]0$/,'')}%`,odometer:odo===null?'—':`${odo} km`,third:power!==null?`${power} kW`:limit!==null?`${limit}%`:'—',status,sample:this.stamp(e.battery_state_of_charge)||this.stamp(e.remaining_range)||''};
 for(const [key,value]of Object.entries(values)){const node=root.querySelector(`[data-value="${key}"]`);if(node&&node.textContent!==value)node.textContent=value;}
 const chargeValue=root.querySelector('[data-value="soc"]');if(chargeValue&&soc!==null)chargeValue.innerHTML=`${this.esc(soc.replace(/[,.]0$/,''))}<small>%</small>`;
 const powerValue=root.querySelector('[data-value="third"]');if(powerValue)powerValue.innerHTML=power!==null?`${this.esc(power)} <small>kW</small>`:limit!==null?`${this.esc(limit)}<small>%</small>`:'—';
 const nativeRange=root.querySelector('[data-value="range"]');if(nativeRange)nativeRange.innerHTML=range===null?'—':`${this.esc(range)}<small> km</small>`;
 const thirdLabel=root.querySelector('[data-value="third-label"],[data-label="third"]');if(thirdLabel)thirdLabel.textContent=power!==null?w.power:w.limit;
 const connectionIcon=root.querySelector('[data-connection-icon]');if(connectionIcon)connectionIcon.innerHTML=connected===false?NIO_DASHBOARD_ICONS.acDisconnected:NIO_DASHBOARD_ICONS.ac;
 const limitRow=root.querySelector('[data-charge-limit-row]'),limitValue=root.querySelector('[data-value="charge-limit"]');if(limitRow)limitRow.hidden=power===null||limit===null;if(limitValue)limitValue.textContent=limit===null?'—':`${limit}%`;
 const fill=root.querySelector('.battery-fill'),level=soc===null?0:Math.max(0,Math.min(100,Number(state(e.battery_state_of_charge))));if(fill){fill.setAttribute('width',String(59*level/100));fill.style.fill=level<=20?'#b65c53':level<=30?'#ad8445':'#758b75';}
 const retained=root.querySelector('[data-value="retained"]');if(retained){const code=nioLocaleCode(this.locale());retained.textContent=this.state(e.battery_state_of_charge)?.attributes?.data_retained?NIO_DASHBOARD_RETAINED[code]||NIO_DASHBOARD_RETAINED.en:'';}
}
  settings(section){
 super.settings();const dialog=this.shadowRoot.querySelector('dialog');if(!dialog)return;const ui=this.words.dashboardUI||NIO_DASHBOARD_UI.en;
 for(const control of dialog.querySelectorAll('[name]')){const label=control.closest('label'),help=label?.nextElementSibling;if(label&&help?.classList.contains('field-help')&&!label.closest('.field-row')){const row=document.createElement('div');row.className='field-row';label.before(row);row.append(label,help);}}
 const titles={appearance:ui[3],readings:ui[4],charger:ui[5],history:ui[6]},groups={
  appearance:new Set(['model','paint','language']),
  readings:new Set(['soc_entity','range_entity','odometer_entity','charging_state_entity','charge_limit_entity','battery_capacity_kwh','full_range_km']),
  charger:new Set(['evcc_connected','evcc_power','evcc_history','electricity_price','reimbursement_rate','cost_energy','cost_solar','cost_total_cost','cost_grid_price','cost_export_price']),
  history:new Set(['ledger_enabled'])
 };
 dialog.dataset.settingsGroup=titles[section]?section:'all';dialog.querySelector('h2').textContent=titles[section]||this.words.settings;
 const back=document.createElement('button');back.type='button';back.className='settings-back';back.textContent=`‹ ${ui[2]}`;dialog.querySelector('form').prepend(back);back.onclick=()=>{dialog.close();this.selectScreen('settings');};
 if(section==='appearance'||section==='history')dialog.querySelector('.source-hint')?.classList.add('settings-hidden');
 for(const control of dialog.querySelectorAll('[name]')){const name=control.name;if(['import'].includes(name))continue;const group=Object.keys(groups).find(key=>groups[key].has(name))||((name==='evcc-preset')?'charger':null);const target=control.closest('details.backup')? 'history':group;const sharedHistoryBasis=section==='history'&&['battery_capacity_kwh','full_range_km'].includes(name);const node=control.closest('.field-row')||control.closest('label')||control.closest('details')||control.parentElement;if(target&&node&&section&&section!==target&&!sharedHistoryBasis){node.classList.add('settings-hidden');if(node.nextElementSibling?.classList.contains('field-help'))node.nextElementSibling.classList.add('settings-hidden');}}
 for(const node of dialog.querySelectorAll('.advanced,.backup')){if(section&&((node.classList.contains('backup')&&section!=='history')||(node.classList.contains('advanced')&&section!=='charger')))node.classList.add('settings-hidden');}
 const advanced=dialog.querySelector('.advanced'),backup=dialog.querySelector('.backup');if(advanced)advanced.open=section==='charger';if(backup)backup.open=section==='history';

 dialog.querySelector('[data-evcc-preset]')?.closest('label')?.classList.toggle('settings-hidden',Boolean(section)&&section!=='charger');
 dialog.querySelector('.actions button[data-cancel]')?.addEventListener('click',()=>this.selectScreen('settings'),{once:true});
}
  static styles=`:host{display:block;font-family:"Segoe UI",system-ui,Arial,sans-serif;color:var(--primary-text-color)}*{box-sizing:border-box}.dashboard{display:block;max-width:590px;margin:0 auto;padding:13px 15px 20px;border:0;border-radius:0;box-shadow:none;background:transparent}header{position:relative;display:flex;align-items:center;justify-content:center;min-height:44px}.identity{display:flex;align-items:center;justify-content:center;gap:11px}.nio-mark{width:29px;height:29px;fill:currentColor;flex:none}h2{font-size:22px;font-weight:400;line-height:1.2;margin:0}.settings{position:absolute;right:0;top:4px;width:34px;height:34px;border:1px solid color-mix(in srgb,currentColor 22%,transparent);border-radius:50%;background:transparent;color:inherit;cursor:pointer;font-size:17px}.showcase{display:grid;grid-template-columns:minmax(0,1.75fr) minmax(100px,1fr);align-items:center;min-height:220px;gap:4px}.car-art{display:grid;place-items:center;min-width:0}.car-art img,.car-art svg{display:block;width:100%;max-width:370px;height:auto;object-fit:contain}.battery{text-align:center}.battery svg{display:block;width:51px;margin:0 auto 7px}.battery strong{display:block;font-weight:300;font-size:42px;line-height:1}.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px;padding:1px 0 12px}.metric{display:flex;align-items:center;justify-content:center;gap:6px;white-space:nowrap;min-width:0}.metric-icon{display:inline-flex;align-items:center;justify-content:center;flex:none}.metric-icon svg[data-car-icon="range-nio-d"]{width:40px;height:22px}.metric-icon svg[data-car-icon="odometer"]{width:30px;height:22px}.metric ha-icon{--mdc-icon-size:21px;width:21px;height:21px;flex:none;color:var(--secondary-text-color)}.metric strong{font-size:14px;font-weight:400;white-space:nowrap}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.status{text-align:center;color:var(--secondary-text-color);font-size:11px;padding:6px 0 14px}.status [data-value="sample"]:not(:empty):before{content:' · '}.history{padding-top:2px}.history-empty,.empty{text-align:center;color:var(--secondary-text-color);padding:22px 8px;font-size:12px;margin:0}button:focus-visible{outline:2px solid var(--primary-color,#47776e);outline-offset:2px}@media(max-width:500px){.dashboard{padding:9px 0 18px}.showcase{min-height:190px;grid-template-columns:minmax(0,1.7fr) minmax(95px,1fr)}.battery strong{font-size:36px}.battery svg{width:44px}.metric{gap:3px}.metric strong{font-size:12px}.metric-icon svg[data-car-icon="range-nio-d"]{width:36px}.metric-icon svg[data-car-icon="odometer"]{width:27px}.metric ha-icon{--mdc-icon-size:19px;width:19px;height:19px}.status{font-size:10px}}`;
}
NioVehicleDashboard.styles+=' .car-placeholder{display:grid;place-items:center;gap:7px;min-height:175px;color:var(--secondary-text-color);font-size:13px}.car-placeholder svg{width:110px;height:90px;opacity:.7}.empty-tabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;padding:7px 0}.empty-tabs span{text-align:center;padding:10px 1px;font-size:12px;color:var(--secondary-text-color);border:1px solid color-mix(in srgb,currentColor 14%,transparent);border-radius:10px}.history-setup{display:block;margin:0 auto 16px;padding:9px 13px;border:1px solid color-mix(in srgb,currentColor 22%,transparent);border-radius:10px;background:transparent;color:inherit;font:inherit;font-size:12px;cursor:pointer}';
NioVehicleCard.styles+=' .source-hint{font-size:11px;line-height:1.45;color:var(--secondary-text-color);margin:14px 0 8px}.advanced{border-top:1px solid var(--divider-color,#8884);margin-top:17px;padding-top:13px}.advanced summary{cursor:pointer;font-size:12px;font-weight:400}';
NioVehicleCard.styles+=' dialog .field-row{display:flex;align-items:center;gap:8px}dialog .field-row label{flex:1;min-width:0}dialog .field-help{font-size:11px;color:var(--secondary-text-color);margin:3px 0 9px}dialog .field-row .field-help{flex:none;margin:15px 0 0}dialog .field-help summary{display:grid;place-items:center;width:24px;height:24px;border:1px solid color-mix(in srgb,currentColor 30%,transparent);border-radius:50%;cursor:pointer;list-style:none}dialog .field-help summary::-webkit-details-marker{display:none}dialog .field-help summary:focus-visible{outline:2px solid var(--primary-color,#426b66)}dialog .field-help p{margin:6px 0 10px;line-height:1.45}dialog .field-row .field-help[open] p{position:absolute;z-index:2;right:20px;left:20px;padding:10px 12px;border:1px solid var(--divider-color,#8886);border-radius:10px;background:var(--card-background-color,#fff);box-shadow:0 6px 20px #0002}';
NioVehicleDashboard.styles+=' .car-art{position:relative;isolation:isolate}.car-art:before{content:"";position:absolute;z-index:-1;left:18%;right:18%;bottom:16%;height:12%;border-radius:50%;background:radial-gradient(ellipse,#0003 0%,#0002 46%,transparent 75%);filter:blur(7px)}.car-photo{position:relative;filter:drop-shadow(0 5px 4px #0002)}.metric-icon ha-icon{--mdc-icon-size:22px;width:30px;height:22px;color:var(--secondary-text-color)}.third-icon svg[data-car-icon="power-plug"]{width:22px;height:22px;color:var(--primary-text-color)}.metric strong{font-weight:300}.settings{background:color-mix(in srgb,var(--card-background-color,#fff) 87%,transparent)}';
NioVehicleDashboard.styles+=' dialog{width:min(92vw,440px);max-height:85dvh;overflow:auto;border:1px solid color-mix(in srgb,currentColor 22%,transparent);border-radius:18px;padding:20px;background:var(--card-background-color,#fff);color:var(--primary-text-color);font-family:"Segoe UI",system-ui,Arial,sans-serif}dialog::backdrop{background:#0008}dialog h2{font-size:20px;font-weight:400;margin:0 0 12px}dialog label{display:block;font-size:12px;margin:12px 0}dialog input,dialog select{display:block;width:100%;margin-top:5px;padding:9px 10px;border:1px solid color-mix(in srgb,currentColor 22%,transparent);border-radius:9px;background:var(--card-background-color,#fff);color:inherit;font:inherit}dialog input[type=checkbox]{display:inline-block;width:16px;height:16px;margin:0 7px 2px 0;vertical-align:middle;accent-color:var(--primary-color,#426b66)}dialog .source-hint{font-size:11px;line-height:1.45;color:var(--secondary-text-color)}dialog .advanced{border-top:1px solid color-mix(in srgb,currentColor 22%,transparent);margin-top:16px;padding-top:12px}dialog .advanced summary{font-size:12px;cursor:pointer}dialog .actions{display:flex;justify-content:flex-end;gap:8px;margin-top:18px}dialog .actions button{border:1px solid color-mix(in srgb,currentColor 22%,transparent);border-radius:10px;padding:9px 14px;background:var(--card-background-color,#fff);color:inherit;font:inherit;cursor:pointer}dialog .actions button[type=submit]{background:var(--primary-color,#426b66);color:white}dialog .error{color:var(--error-color,#b44);font-size:12px}';
NioVehicleCard.styles+=' dialog .backup{border-top:1px solid color-mix(in srgb,currentColor 22%,transparent);margin-top:16px;padding-top:12px;font-size:12px}dialog .backup summary{cursor:pointer}dialog .backup p{font-size:11px;line-height:1.45;color:var(--secondary-text-color)}dialog .backup button{border:1px solid color-mix(in srgb,currentColor 22%,transparent);border-radius:9px;padding:8px 11px;background:var(--card-background-color,#fff);color:inherit;cursor:pointer}dialog .backup button[hidden]{display:none}dialog .backup input[type=file]{font-size:11px}';
NioVehicleCard.styles+=' .car-art img{display:block;width:min(100%,430px);height:auto;object-fit:contain}';
NioVehicleDashboard.styles+=' dialog .field-row{display:flex;align-items:center;gap:8px}dialog .field-row label{flex:1;min-width:0}dialog .field-help{font-size:11px;color:var(--secondary-text-color);margin:3px 0 9px}dialog .field-row .field-help{flex:none;margin:15px 0 0}dialog .field-help summary{display:grid;place-items:center;width:24px;height:24px;border:1px solid color-mix(in srgb,currentColor 30%,transparent);border-radius:50%;cursor:pointer;list-style:none}dialog .field-help summary::-webkit-details-marker{display:none}dialog .field-help summary:focus-visible{outline:2px solid var(--primary-color,#426b66)}dialog .field-help p{margin:6px 0 10px;line-height:1.45}dialog .field-row .field-help[open] p{position:absolute;z-index:2;right:20px;left:20px;padding:10px 12px;border:1px solid color-mix(in srgb,currentColor 22%,transparent);border-radius:10px;background:var(--card-background-color,#fff);box-shadow:0 6px 20px #0002}dialog .backup{border-top:1px solid color-mix(in srgb,currentColor 22%,transparent);margin-top:16px;padding-top:12px;font-size:12px}dialog .backup summary{cursor:pointer}dialog .backup p{font-size:11px;line-height:1.45;color:var(--secondary-text-color)}dialog .backup button{border:1px solid color-mix(in srgb,currentColor 22%,transparent);border-radius:9px;padding:8px 11px;background:var(--card-background-color,#fff);color:inherit;cursor:pointer}dialog .backup button[hidden]{display:none}dialog .backup input[type=file]{font-size:11px}';
// The studio artwork includes its own soft contact shadow. Do not stack the
// synthetic ellipse and drop-shadow that made the car resemble a toy model.
NioVehicleDashboard.styles+=' .car-art:before{display:none}.car-photo{filter:none}.showcase{min-height:228px;grid-template-columns:minmax(0,2.15fr) minmax(92px,.85fr)}@media(max-width:500px){.showcase{min-height:207px;grid-template-columns:minmax(0,2.4fr) minmax(82px,.8fr)}}';
if(!customElements.get('nio-vehicle-card-editor'))customElements.define('nio-vehicle-card-editor',NioVehicleCardEditor);
if(!customElements.get('nio-vehicle-card'))customElements.define('nio-vehicle-card',NioVehicleCard);
if(!customElements.get('nio-vehicle-dashboard'))customElements.define('nio-vehicle-dashboard',NioVehicleDashboard);
window.customCards=window.customCards||[];
window.customCards.push({type:'nio-vehicle-card',name:'NIO Vehicle',description:'Local, multilingual NIO vehicle overview'});
window.customCards.push({type:'nio-vehicle-dashboard',name:'NIO Vehicle Dashboard',description:'App-like NIO vehicle view with optional trip and charging history'});

// Complete NIO-only dashboard shell. The compact card above retains its own
// render path and the separately registered household history card is untouched.
const NIO_DASHBOARD_ICONS={
 "car": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 64 52\" fill=\"currentColor\" aria-hidden=\"true\"><path fill-rule=\"evenodd\" d=\"M28 8V5q0-2 2-2h4q2 0 2 2v3h8q5 0 7 5l5 11q5 4 5 10v13q0 3-3 3h-6q-3 0-3-4H15q0 4-3 4H6q-3 0-3-3V34q0-6 5-10l5-11q2-5 7-5Zm-9 5-5 11h36l-5-11q-13-2-26 0ZM9 30q1 3 14 4v-2Zm46 0-14 2v2q13-1 14-4ZM10 38l-1 6q5-5 1-6Zm44 0q-4 1 1 6Zm-30 5-4 3h24l-4-3Zm5-8q3-4 6 0l-2 1q-1-2-2 0Zm1 3q2-3 4 0l-2-1Z\"/><path d=\"M8 20q-7-4-8 2 0 3 7 3Zm48 0q7-4 8 2 0 3-7 3Z\"/></svg>",
 "history": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M3 12a9 9 0 1 0 2.64-6.36L3 8\"/><path d=\"M3 3v5h5M12 7v5l3 2\"/></svg>",
 "settings": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M10 5H3M12 19H3M14 3v4M16 17v4M21 12h-9M21 19h-5M21 5h-7M8 10v4M8 12H3\"/></svg>",
 "received": "<svg data-car-icon=\"received-charge-energy\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 30 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.4\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><rect x=\"10\" y=\"5\" width=\"17\" height=\"14\" rx=\"2\"/><path d=\"M29 10v4M2 12h15m-4-4 4 4-4 4\"/></svg>",
 "solar": "<svg data-approved-icon=\"sun\" viewBox=\"0 0 24 24\" fill=\"currentColor\"><path d=\"M3.55 19.09L4.96 20.5L6.76 18.71L5.34 17.29M12 6C8.69 6 6 8.69 6 12S8.69 18 12 18 18 15.31 18 12C18 8.68 15.31 6 12 6M20 13H23V11H20M17.24 18.71L19.04 20.5L20.45 19.09L18.66 17.29M20.45 5L19.04 3.6L17.24 5.39L18.66 6.81M13 1H11V4H13M6.76 5.39L4.96 3.6L3.55 5L5.34 6.81L6.76 5.39M1 13H4V11H1M13 20H11V23H13\"/></svg>",
 "ac": "<svg viewBox=\"0 0 64 64\" aria-hidden=\"true\"><svg x=\"11\" y=\"13.33\" width=\"42\" height=\"48\" viewBox=\"0 0 48 54\"><defs><mask id=\"ac\"><rect width=\"48\" height=\"54\" fill=\"white\"/><g fill=\"none\" stroke=\"black\" stroke-width=\"1.4\" stroke-linejoin=\"round\"><path d=\"M18 10h12C34 12 36 16 36 21a12 12 0 0 1-24 0c0-5 2-9 6-11Z\"/></g><g fill=\"black\"><circle cx=\"20\" cy=\"15\" r=\"1.25\"/><circle cx=\"28\" cy=\"15\" r=\"1.25\"/><circle cx=\"16.5\" cy=\"22\" r=\"1.7\"/><circle cx=\"24\" cy=\"22\" r=\"1.7\"/><circle cx=\"31.5\" cy=\"22\" r=\"1.7\"/><circle cx=\"20\" cy=\"28\" r=\"1.7\"/><circle cx=\"28\" cy=\"28\" r=\"1.7\"/></g></mask></defs><rect x=\"7\" y=\"6\" width=\"34\" height=\"32\" rx=\"7\" fill=\"currentColor\" mask=\"url(#ac)\"/></svg></svg>",
 "acDisconnected": "<svg viewBox=\"0 0 64 64\" aria-hidden=\"true\"><defs><mask id=\"acOffslash\"><rect width=\"64\" height=\"64\" fill=\"white\"/><path d=\"M17.150757595082503 47.8492424049175 46.8492424049175 18.150757595082503\" stroke=\"black\" stroke-width=\"4\"/></mask></defs><g mask=\"url(#acOffslash)\"><svg x=\"11\" y=\"13.33\" width=\"42\" height=\"48\" viewBox=\"0 0 48 54\"><defs><mask id=\"acOff\"><rect width=\"48\" height=\"54\" fill=\"white\"/><g fill=\"none\" stroke=\"black\" stroke-width=\"1.4\" stroke-linejoin=\"round\"><path d=\"M18 10h12C34 12 36 16 36 21a12 12 0 0 1-24 0c0-5 2-9 6-11Z\"/></g><g fill=\"black\"><circle cx=\"20\" cy=\"15\" r=\"1.25\"/><circle cx=\"28\" cy=\"15\" r=\"1.25\"/><circle cx=\"16.5\" cy=\"22\" r=\"1.7\"/><circle cx=\"24\" cy=\"22\" r=\"1.7\"/><circle cx=\"31.5\" cy=\"22\" r=\"1.7\"/><circle cx=\"20\" cy=\"28\" r=\"1.7\"/><circle cx=\"28\" cy=\"28\" r=\"1.7\"/></g></mask></defs><rect x=\"7\" y=\"6\" width=\"34\" height=\"32\" rx=\"7\" fill=\"currentColor\" mask=\"url(#acOff)\"/></svg></g><g fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.2\"><circle cx=\"32\" cy=\"33\" r=\"21\"/><path d=\"M17.150757595082503 47.8492424049175 46.8492424049175 18.150757595082503\"/></g></svg>",
 "plug": "<svg data-car-icon=\"power-plug\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M8 3v5M16 3v5M6 8h12v4a6 6 0 0 1-12 0zM12 18v3\"/></svg>",
 "chevron": "<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"m9 18 6-6-6-6\"/></svg>"
};
NioVehicleDashboard.appStyles="\n:host{--nio-accent:#00878b;--nio-border:var(--divider-color,color-mix(in srgb,var(--primary-text-color,#141414) 20%,transparent));--nio-surface:var(--card-background-color,#fff);--nio-muted:var(--secondary-text-color,#626262);--nio-range-size:26px;font-family:\"Segoe UI\",sans-serif;color:var(--primary-text-color,#141414)}\n.dashboard{scroll-margin-top:56px;max-width:760px;margin:auto;padding:16px 20px 24px;background:transparent}.app-header{display:flex;align-items:center;justify-content:space-between;min-height:44px;margin:0 0 4px}.identity{display:flex;align-items:center;gap:10px}.app-header .identity h2{font:400 22px/1.4 \"Segoe UI\",sans-serif;margin:0}.nio-mark{width:26px;height:26px}.settings{position:static;display:grid;place-items:center;flex:none;width:44px;height:44px;border:0;background:none;padding:10px;color:var(--nio-muted)}.settings svg{width:22px;height:22px}\n.vehicle-overview{max-width:590px;margin:0 auto}.hero-car{display:grid;place-items:center;padding:12px 0 0;background:radial-gradient(ellipse,color-mix(in srgb,var(--nio-accent) 16%,transparent),transparent 70%)}.hero-crop{display:block;width:100%;height:auto}.hero-car .car-photo{width:100%;max-height:none;filter:none}.hero-car.touring .car-photo{aspect-ratio:2.4;object-fit:cover;object-position:center}.car-art:before{display:none}.odo-caption{display:flex;align-items:center;gap:8px;margin:6px 0 12px;color:var(--nio-muted);font:400 12px/1.5 \"Segoe UI\",sans-serif}.odo-caption .metric-icon{display:flex;width:30px;height:24px}.odo-caption svg{width:30px;height:24px}.odo-caption strong{font:400 12px/1.5 \"Segoe UI\",sans-serif}.odo-caption button{margin-left:auto;min-height:44px;border:0;padding:6px;background:none;color:var(--nio-muted);font:400 12px/1.5 \"Segoe UI\",sans-serif;cursor:pointer}\n.range-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);align-items:start;gap:24px;padding:7px 0 22px;border:0}.battery{display:grid;justify-items:start;align-content:start;padding:0}.battery-label,.range-label{display:flex;align-items:center;gap:7px;min-height:30px;font:400 12px/1.5 \"Segoe UI\",sans-serif;color:var(--nio-muted)}.battery strong{font:300 45px/1.3 \"Segoe UI\",sans-serif;white-space:nowrap}.range-label svg{width:40px;height:22px}.range-stack{display:grid;min-width:0}.range-row{display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:44px;padding:0;border:0}.range-row>span{font:400 12px/1.5 \"Segoe UI\",sans-serif;color:var(--nio-muted)}.range-row>strong,.calculated-value strong{font:300 var(--nio-range-size)/1.25 \"Segoe UI\",sans-serif;color:var(--primary-text-color);white-space:nowrap}.range-row strong small{font:400 12px/1.25 \"Segoe UI\",sans-serif}.calculated-value{display:grid;justify-items:end;border:0;background:none;padding:0;color:inherit;cursor:pointer;text-align:right;min-height:44px}.calculated-value>.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}.calculated-value>small{max-width:220px;font:400 12px/1.5 \"Segoe UI\",sans-serif;color:var(--nio-muted);white-space:normal}\n.charge-title{border-top:1px solid var(--nio-border);padding-top:20px}.charge-title h3{display:flex;align-items:center;gap:8px;margin:0;font:400 17px/1.5 \"Segoe UI\",sans-serif}.connection-icon{display:flex;flex:none}.connection-icon svg{width:28px;height:28px}.charge-title+.metrics{border-top:0}.metrics strong small,.battery strong small{font:400 12px/1.4 \"Segoe UI\",sans-serif}.charge-limit{display:flex;align-items:center;justify-content:space-between;min-height:44px;font:400 12px/1.5 \"Segoe UI\",sans-serif;color:var(--nio-muted)}.charge-limit[hidden]{display:none}.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;border-top:1px solid var(--nio-border);border-bottom:1px solid var(--nio-border);padding:20px 0 16px}.metrics>div{display:grid;gap:8px;min-width:0}.metrics>div>span{display:flex;align-items:center;gap:6px;min-height:36px;font:400 12px/1.5 \"Segoe UI\",sans-serif;color:var(--nio-muted)}.metrics svg{width:26px;height:24px;flex:none}.metrics strong{font:300 23px/1.4 \"Segoe UI\",sans-serif;white-space:nowrap}.sample-note,.status,.retained-note{font:400 12px/1.6 \"Segoe UI\",sans-serif;color:var(--nio-muted);margin:12px 0}.retained-note:empty{display:none}.vehicle-details{margin-top:16px;border-top:1px solid var(--nio-border)}.vehicle-details>summary{min-height:44px;padding:12px 0;font:400 14px/1.5 \"Segoe UI\",sans-serif;cursor:pointer}.vehicle-details p{display:flex;justify-content:space-between;gap:16px;font:400 12px/1.6 \"Segoe UI\",sans-serif}.vehicle-details p strong{font-weight:400}\n.primary-navigation{position:sticky;top:56px;z-index:10;isolation:isolate;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));height:44px;margin:24px 0;border:0;border-radius:0;padding:0;background:var(--primary-background-color,#fafafa);overflow:visible}.primary-navigation::after{content:\"\";position:absolute;inset:4px 0;border:1px solid var(--nio-border);border-radius:999px;pointer-events:none;z-index:2}.primary-navigation button{position:relative;isolation:isolate;display:flex;align-items:center;justify-content:center;gap:8px;height:44px;min-height:44px;margin:0;padding:0 8px;border:0;border-radius:0;background:none;color:var(--nio-muted);font:400 14px/1.4 \"Segoe UI\",sans-serif;cursor:pointer}.primary-navigation button::before{content:\"\";position:absolute;inset:4px 0;z-index:-1;border-right:1px solid var(--nio-border);pointer-events:none}.primary-navigation button:first-child::before{border-radius:18px 0 0 18px}.primary-navigation button:last-child::before{border-right:0;border-radius:0 18px 18px 0}.primary-navigation button[aria-current=page]{color:var(--primary-text-color)}.primary-navigation button[aria-current=page]::before{background:color-mix(in srgb,var(--nio-accent) 20%,var(--nio-surface))}.navigation-icon{display:flex;align-items:center;justify-content:center;width:26px;height:24px}.navigation-icon svg{display:block;width:23px;height:23px}.primary-navigation button:focus-visible,.menu-row:focus-visible,.calculated-value:focus-visible{outline:2px solid var(--nio-accent);outline-offset:-3px}\n.screen-panel{scroll-margin-top:116px;max-width:760px;margin:0 auto 28px}.screen-panel[hidden]{display:none!important}.section-intro{margin:0 0 16px}.section-intro h2{font:400 20px/1.4 \"Segoe UI\",sans-serif;margin:0 0 6px}.section-intro p{font:400 12px/1.6 \"Segoe UI\",sans-serif;color:var(--nio-muted);margin:0}.settings-menu{border:1px solid var(--nio-border);border-radius:12px;overflow:hidden;background:var(--nio-surface)}.menu-row{display:flex;align-items:center;justify-content:space-between;gap:16px;width:100%;min-height:76px;padding:16px;text-align:left;color:inherit;background:none;border:0;border-bottom:1px solid var(--nio-border);font-family:inherit;cursor:pointer}.menu-row:last-child{border-bottom:0}.menu-row strong{display:block;font:400 14px/1.4 \"Segoe UI\",sans-serif}.menu-row small{display:block;margin-top:4px;color:var(--nio-muted);font:400 12px/1.5 \"Segoe UI\",sans-serif}.menu-chevron{display:flex;flex:none;color:var(--nio-muted)}.menu-chevron svg{width:20px;height:20px}.history-empty{padding:24px 0;color:var(--nio-muted);font:400 14px/1.6 \"Segoe UI\",sans-serif}.history-setup{min-height:44px;border:1px solid var(--nio-border);border-radius:8px;padding:8px 14px;background:var(--nio-surface);color:inherit;font:400 14px/1.5 \"Segoe UI\",sans-serif;cursor:pointer}\ndialog{box-sizing:border-box;width:min(calc(100vw - 32px),500px);max-width:none;max-height:calc(100dvh - 32px);padding:20px;font:400 14px/1.5 \"Segoe UI\",sans-serif}dialog .field-row{grid-template-columns:minmax(0,1fr) 44px;gap:8px;align-items:end;margin:0 0 16px}dialog .field-row>label{margin:0}dialog .actions{position:sticky;bottom:0;padding-top:16px;background:var(--nio-surface);z-index:2}dialog .settings-back,dialog .actions button{min-height:44px}dialog .field-help summary{position:relative;display:grid;place-items:center;min-width:44px;min-height:44px;padding:0;border:0;background:none;box-shadow:none;list-style:none}dialog .field-help summary::before{content:\"\";position:absolute;inset:10px;border:1px solid var(--nio-border);border-radius:50%;pointer-events:none}dialog h2{font:400 20px/1.4 \"Segoe UI\",sans-serif}dialog h3{font:400 17px/1.4 \"Segoe UI\",sans-serif}dialog label{font-size:12px;line-height:1.5}dialog input:not([type=checkbox]),dialog select{min-height:44px;font:400 14px/1.5 \"Segoe UI\",sans-serif}dialog .advanced>summary,dialog .backup>summary{min-height:44px;padding:12px 0;font:400 14px/1.5 \"Segoe UI\",sans-serif}\n@media(max-width:800px){.dashboard{padding:8px 8px calc(100px + env(safe-area-inset-bottom))}.app-header .identity h2{font-size:20px}.vehicle-overview{max-width:520px}.dashboard[data-screen=history] .vehicle-overview,.dashboard[data-screen=settings] .vehicle-overview{display:none}.primary-navigation{position:fixed;top:auto;left:0;right:0;bottom:0;z-index:50;height:auto;min-height:68px;max-width:none;margin:0;padding:6px 12px calc(6px + env(safe-area-inset-bottom));border:0;border-top:1px solid var(--nio-border);border-radius:0;background:var(--nio-surface)}.primary-navigation::after{display:none}.primary-navigation button{flex-direction:column;gap:4px;height:auto;min-height:57px;padding:5px 8px;border:0;font-size:12px}.primary-navigation button::before{display:none}.navigation-icon{width:64px;height:30px;border-radius:999px}.primary-navigation button[aria-current=page] .navigation-icon{background:color-mix(in srgb,var(--nio-accent) 20%,var(--nio-surface));color:var(--primary-text-color)}.screen-panel{scroll-margin-top:72px;padding:0}.metrics{gap:12px}.metrics strong{font-size:21px}}\n@media(max-width:350px){:host{--nio-range-size:23px}.range-grid{gap:16px}.battery strong{font-size:42px}.metrics strong{font-size:19px}.primary-navigation{padding-left:8px;padding-right:8px}dialog{padding:16px}}\n";
NioVehicleDashboard.styles+=` .settings-hidden{display:none!important}.settings-back{border:0;background:transparent;color:var(--secondary-text-color);font:400 12px "Segoe UI",sans-serif;padding:0 0 12px;cursor:pointer}.range-row>strong{display:flex;align-items:baseline;gap:4px}.range-row>strong small{font:400 12px/1.25 "Segoe UI",sans-serif}.range-note{grid-column:1/-1;font:400 12px/1.5 "Segoe UI",sans-serif;color:var(--secondary-text-color);margin:4px 12px 2px}dialog .actions button[type=submit]{background:#00bebe;color:#000}`;
