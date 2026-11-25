/* Car Ledger: snapshot UI. Source updates never replace the visible session list. */
const LEDGER_ENGLISH = {
  "Laden": "Charging",
  "Ritten": "Trips",
  "Verbruik": "Consumption",
  "Stilstand": "Parked",
  "Lopende sessie": "Ongoing session",
  "Vernieuwen": "Refresh",
  "Autohistoriek": "Vehicle history",
  "Laatste laadsessies": "Recent charging",
  "Laatste ritten": "Recent trips",
  "Alle laadsessies": "All charging sessions",
  "Alle ritten": "All trips",
  "Terug naar de laatste drie": "Back to recent three",
  "Alle stilstandperiodes": "All parked periods",
  "Nog geen laadsessies": "No charging sessions yet",
  "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "The first trip appears after the car reports new readings.",
  "Ritten en laadkosten laden…": "Loading trips and charging…",
  "Laatste stilstandperiodes": "Recent parked periods",
  "Nog geen geregistreerde bereikafname bij stilstand.": "No parked battery loss recorded yet.",
  "Laatste rit": "Last trip",
  "Huidige rit": "Current trip",
  "Sinds laadbeurt": "Since charging",
  "Sinds laatste laadbeurt": "Since last charge",
  "Laatste 100 km": "Last 100 km",
  "Vandaag": "Today",
  "Maand": "Month",
  "Jaar": "Year",
  "Gemiddeld verbruik": "Average consumption",
  "Gem. verbruik": "Average consumption",
  "Rijkosten": "Driving cost",
  "Afstand": "Distance",
  "Naam": "Name",
  "Kosten": "Costs",
  "Verbruikt": "Consumption",
  "Gebruikt": "Used",
  "Batterij": "Battery",
  "Laadkosten": "Charging cost",
  "Totaal": "Total",
  "Geladen": "Charged",
  "Gem. tarief": "Average tariff",
  "Grafieken & actieradius": "Charts & range",
  "Actieradius bij dit verbruik": "Range at this consumption",
  "Rittellers & instellingen": "Trip counters & settings",
  "Rekeninstellingen": "Calculation settings",
  "Nieuwe ritteller": "New trip counter",
  "Ritteller opnieuw starten": "Reset trip counter",
  "Ritdetails": "Trip details",
  "Energie gebruikt": "Energy used",
  "Batterij bij vertrek": "Battery at departure",
  "Batterij bij aankomst": "Battery at arrival",
  "Duur": "Duration",
  "Laadsessie toevoegen": "Add charge",
  "Lading controleren": "Review charge",
  "Lading bevestigen": "Confirm charge",
  "Laadprijs": "Charging price",
  "Laadvoordeel": "Charging benefit",
  "Tarief": "Tariff",
  "Thuis": "Home",
  "Werk": "Work",
  "Snellader": "Fast charger",
  "Onderweg": "Away",
  "Prijs aanvullen": "Add price",
  "Bon & energie": "Receipt & energy",
  "Berekende energie": "Estimated energy",
  "Gem.": "Avg.",
  "Zon": "Solar",
  "Geladen kWh": "Charged kWh",
  "Prijs per kWh": "Price per kWh",
  "Totaal op bon (optioneel)": "Receipt total (optional)",
  "Locatie": "Location",
  "Start": "Start",
  "Einde": "End",
  "Opslaan": "Save",
  "Sluiten": "Close",
  "Reset": "Reset",
  "Meer tonen": "Show more",
  "Geschat uit batterijafname": "Estimated from battery decrease",
  "Dit was geen lading": "This was not a charge",
  "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "The car reported more range. Confirm only if it was actually charged.",
  "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "The price of the energy already in the battery is needed to calculate driving costs from the start. Leave it blank if unknown.",
  "Prijs energie bij start van registratie (€/kWh)": "Initial battery energy price (€/kWh)",
  "Referentieverbruik (kWh/100 km)": "Reference consumption (kWh/100 km)",
  "Vorige auto (l/100 km)": "Previous car (l/100 km)",
  "Benzineprijs (€/l)": "Petrol price (€/l)",
  "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Waiting for a fresh car reading; retained values do not create a new trip.",
  "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Estimated battery loss between readings at the same odometer. Separate from driving consumption; the cause was not measured.",
  "Rit bezig": "Trip in progress",
  "Meting ontbreekt": "Reading missing",
  "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Consumption appears after the first measured trip.",
  "Vergelijking benzine": "Petrol comparison",
  "Benzine voor deze afstand": "Petrol for this distance",
  "Besparing": "Savings",
  "Verbruik t.o.v. referentie": "Consumption versus reference",
  "Nog niet beschikbaar": "Not available",
  "Laden en ritten laden…": "Loading charge history and trips…",
  "Vergoeding": "Reimbursement",
  "Batterij gebruikt": "Battery used",
  "Laadenergie per dag": "Charging energy per day",
  "Verbruik per gemeten rijsegment": "Consumption per measured driving segment",
  "prijs ontbreekt": "price missing",
  "Rittenregistratie nog niet beschikbaar": "Trip ledger is not available yet",
  "prijs": "price",
  "prijzen": "prices",
  "bekend": "Known",
  "zon": "solar",
  "laadkosten": "charging cost",
  "vergoeding": "reimbursement",
  "laadvoordeel": "charging benefit",
  "ritten": "trips"
};
const LEDGER_TRANSLATIONS = {
  "fr": {
    "Laden": "Recharge",
    "Ritten": "Trajets",
    "Verbruik": "Consommation",
    "Stilstand": "Stationné",
    "Lopende sessie": "Séance en cours",
    "Vernieuwen": "Actualiser",
    "Autohistoriek": "Historique du véhicule",
    "Laatste laadsessies": "Recharges récentes",
    "Laatste ritten": "Trajets récents",
    "Alle laadsessies": "Toutes les recharges",
    "Alle ritten": "Tous les déplacements",
    "Terug naar de laatste drie": "Retour aux trois récents",
    "Alle stilstandperiodes": "Toutes les périodes de stationnement",
    "Nog geen laadsessies": "Aucune session de recharge pour l'instant",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Le premier trajet s’affiche dès que la voiture transmet de nouvelles mesures.",
    "Ritten en laadkosten laden…": "Chargement des trajets et des coûts de recharge…",
    "Laatste stilstandperiodes": "Périodes de stationnement récentes",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Aucune baisse de batterie à l’arrêt n’a encore été enregistrée.",
    "Laatste rit": "Dernier trajet",
    "Huidige rit": "Trajet en cours",
    "Sinds laadbeurt": "Depuis la recharge",
    "Sinds laatste laadbeurt": "Depuis la dernière recharge",
    "Laatste 100 km": "Derniers 100 km",
    "Vandaag": "Aujourd'hui",
    "Maand": "Mois",
    "Jaar": "Année",
    "Gemiddeld verbruik": "Consommation moyenne",
    "Gem. verbruik": "Consommation moyenne",
    "Rijkosten": "Coût de conduite",
    "Afstand": "Distance",
    "Naam": "Nom",
    "Kosten": "Coût",
    "Verbruikt": "Consommation",
    "Gebruikt": "Utilisé",
    "Batterij": "Batterie",
    "Laadkosten": "Coût de recharge",
    "Totaal": "Total",
    "Geladen": "Énergie rechargée",
    "Gem. tarief": "Tarif moyen",
    "Grafieken & actieradius": "Graphiques et autonomie",
    "Actieradius bij dit verbruik": "Autonomie à cette consommation",
    "Rittellers & instellingen": "Compteurs de trajets et paramètres",
    "Rekeninstellingen": "Paramètres de calcul",
    "Nieuwe ritteller": "Nouveau compteur journalier",
    "Ritteller opnieuw starten": "Réinitialiser le compteur journalier",
    "Ritdetails": "Détails du trajet",
    "Energie gebruikt": "Énergie utilisée",
    "Batterij bij vertrek": "Batterie au départ",
    "Batterij bij aankomst": "Batterie à l'arrivée",
    "Duur": "Durée",
    "Laadsessie toevoegen": "Ajouter une recharge",
    "Lading controleren": "Vérifier la recharge",
    "Lading bevestigen": "Confirmer la recharge",
    "Laadprijs": "Prix de recharge",
    "Laadvoordeel": "Avantage de recharge",
    "Tarief": "Tarif",
    "Thuis": "Domicile",
    "Werk": "Travail",
    "Snellader": "Chargeur rapide",
    "Onderweg": "À l’extérieur",
    "Prijs aanvullen": "Ajouter un prix",
    "Bon & energie": "Reçu et énergie",
    "Berekende energie": "Énergie estimée",
    "Gem.": "Moy.",
    "Zon": "Solaire",
    "Geladen kWh": "kWh chargés",
    "Prijs per kWh": "Prix du kWh",
    "Totaal op bon (optioneel)": "Montant total du reçu (facultatif)",
    "Locatie": "Emplacement",
    "Start": "Début",
    "Einde": "Fin",
    "Opslaan": "Enregistrer",
    "Sluiten": "Fermer",
    "Reset": "Réinitialiser",
    "Meer tonen": "Afficher plus",
    "Geschat uit batterijafname": "Estimé à partir de la diminution de la batterie",
    "Dit was geen lading": "Ce n’était pas une recharge",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "La voiture a signalé une autonomie plus élevée. Confirmez uniquement s’il s’agissait bien d’une recharge.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Le prix initial de la batterie est nécessaire pour calculer le coût de conduite dès le départ. Laissez-le vide si inconnu.",
    "Prijs energie bij start van registratie (€/kWh)": "Prix initial de l’énergie en batterie (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Consommation de référence (kWh/100 km)",
    "Vorige auto (l/100 km)": "Voiture précédente (l/100 km)",
    "Benzineprijs (€/l)": "Prix essence (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "En attente d’une nouvelle mesure de la voiture ; les valeurs conservées ne créent pas de nouveau trajet.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Baisse estimée de la batterie entre deux mesures avec le même kilométrage. Elle est distincte de la consommation en conduite ; les causes n’ont pas été mesurées.",
    "Rit bezig": "Trajet en cours",
    "Meting ontbreekt": "Mesure manquante",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "La consommation apparaît après le premier trajet mesuré.",
    "Vergelijking benzine": "Comparaison essence",
    "Benzine voor deze afstand": "Essence pour cette distance",
    "Besparing": "Économies",
    "Verbruik t.o.v. referentie": "Consommation versus référence",
    "Nog niet beschikbaar": "Non disponible",
    "Laden en ritten laden…": "Chargement des trajets et des recharges…",
    "Vergoeding": "Remboursement",
    "Batterij gebruikt": "Batterie utilisée",
    "Laadenergie per dag": "Énergie de charge par jour",
    "Verbruik per gemeten rijsegment": "Consommation par segment de conduite mesuré",
    "prijs ontbreekt": "prix manquant",
    "Rittenregistratie nog niet beschikbaar": "Le registre des déplacements n'est pas encore disponible",
    "prijs": "prix",
    "prijzen": "tarifs",
    "bekend": "Connu",
    "zon": "solaire",
    "laadkosten": "coût de recharge",
    "vergoeding": "remboursement",
    "laadvoordeel": "avantage de recharge",
    "ritten": "trajets",
    "__dynamic_battery": "Consommation : {capacity} kWh × variation du SoC calculé. Le coût de conduite utilise le prix moyen de l’énergie contenue dans la batterie. La recharge à domicile inclut la valeur EVCC, y compris le renoncement à l'exportation. Les pertes de charge ne sont pas mesurées séparément.",
    "__dynamic_trip": "Compteur kilométrique {start} → {end} km. Les temps suivent les lectures reçues. La consommation est estimée à partir des relevés de la batterie en utilisant la capacité utilisable {capacity} kWh. Les pertes sans changement du compteur kilométrique sont comptées séparément comme des pertes en stationnement.{unknown}"
  },
  "de": {
    "Laden": "Laden",
    "Ritten": "Fahrten",
    "Verbruik": "Verbrauch",
    "Stilstand": "Geparkt",
    "Lopende sessie": "Laufende Sitzung",
    "Vernieuwen": "Aktualisieren",
    "Autohistoriek": "Fahrzeughistorie",
    "Laatste laadsessies": "Letzte Aufladung",
    "Laatste ritten": "Letzte Reisen",
    "Alle laadsessies": "Alle Ladevorgänge",
    "Alle ritten": "Alle Fahrten",
    "Terug naar de laatste drie": "Zurück zu den letzten drei",
    "Alle stilstandperiodes": "Alle Parkperioden",
    "Nog geen laadsessies": "Noch keine Ladevorgänge",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Die erste Fahrt erscheint, nachdem das Auto neue Messwerte meldet.",
    "Ritten en laadkosten laden…": "Ladevorgänge und Fahrten werden geladen …",
    "Laatste stilstandperiodes": "Letzte Parkzeiten",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Es wurde noch kein Verlust der geparkten Batterie registriert.",
    "Laatste rit": "Letzte Fahrt",
    "Huidige rit": "Aktuelle Fahrt",
    "Sinds laadbeurt": "Seit dem Aufladen",
    "Sinds laatste laadbeurt": "Seit der letzten Ladung",
    "Laatste 100 km": "Letzte 100 km",
    "Vandaag": "Heute",
    "Maand": "Monat",
    "Jaar": "Jahr",
    "Gemiddeld verbruik": "Durchschnittlicher Verbrauch",
    "Gem. verbruik": "Durchschnittlicher Verbrauch",
    "Rijkosten": "Fahrkosten",
    "Afstand": "Entfernung",
    "Naam": "Name",
    "Kosten": "Kosten",
    "Verbruikt": "Verbrauch",
    "Gebruikt": "Verbraucht",
    "Batterij": "Batterie",
    "Laadkosten": "Ladekosten",
    "Totaal": "Gesamt",
    "Geladen": "Geladen",
    "Gem. tarief": "Durchschnittspreis",
    "Grafieken & actieradius": "Diagramme und Reichweite",
    "Actieradius bij dit verbruik": "Reichweite bei diesem Verbrauch",
    "Rittellers & instellingen": "Fahrtzähler und Einstellungen",
    "Rekeninstellingen": "Berechnungseinstellungen",
    "Nieuwe ritteller": "Neuer Fahrtzähler",
    "Ritteller opnieuw starten": "Fahrtzähler zurücksetzen",
    "Ritdetails": "Fahrtdetails",
    "Energie gebruikt": "Verwendete Energie",
    "Batterij bij vertrek": "Batterie bei Abfahrt",
    "Batterij bij aankomst": "Batterie bei Ankunft",
    "Duur": "Dauer",
    "Laadsessie toevoegen": "Ladevorgang hinzufügen",
    "Lading controleren": "Ladevorgang prüfen",
    "Lading bevestigen": "Ladevorgang bestätigen",
    "Laadprijs": "Ladepreis",
    "Laadvoordeel": "Ladevorteil",
    "Tarief": "Tarif",
    "Thuis": "Zuhause",
    "Werk": "Arbeit",
    "Snellader": "Schnellladegerät",
    "Onderweg": "Unterwegs",
    "Prijs aanvullen": "Preis hinzufügen",
    "Bon & energie": "Beleg und Energie",
    "Berekende energie": "Geschätzte Energie",
    "Gem.": "Durchschn.",
    "Zon": "Solar",
    "Geladen kWh": "Geladene kWh",
    "Prijs per kWh": "Preis pro kWh",
    "Totaal op bon (optioneel)": "Gesamtbetrag auf dem Beleg (optional)",
    "Locatie": "Standort",
    "Start": "Start",
    "Einde": "Ende",
    "Opslaan": "Speichern",
    "Sluiten": "Schließen",
    "Reset": "Zurücksetzen",
    "Meer tonen": "Mehr anzeigen",
    "Geschat uit batterijafname": "Geschätzt aufgrund der Batterieabnahme",
    "Dit was geen lading": "Dies war kein Ladevorgang",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Das Auto meldete mehr Reichweite. Bestätigen Sie dies nur, wenn tatsächlich geladen wurde.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Der Preis der bereits in der Batterie gespeicherten Energie wird benötigt, um die Fahrkosten ab Beginn zu berechnen. Lassen Sie das Feld leer, wenn der Preis unbekannt ist.",
    "Prijs energie bij start van registratie (€/kWh)": "Anfangspreis der Energie in der Batterie (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Referenzverbrauch (kWh/100 km)",
    "Vorige auto (l/100 km)": "Vorheriges Auto (l/100 km)",
    "Benzineprijs (€/l)": "Benzinpreis (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Warten auf eine neue Fahrzeuglesung; Beibehaltene Werte erzeugen keine neue Reise.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Geschätzter Batterieverlust zwischen den Messungen auf demselben Kilometerzähler. Getrennt vom Fahrverbrauch; Die Ursache wurde nicht gemessen.",
    "Rit bezig": "Fahrt läuft",
    "Meting ontbreekt": "Lesung fehlt",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Der Verbrauch erscheint nach der ersten gemessenen Fahrt.",
    "Vergelijking benzine": "Benzinvergleich",
    "Benzine voor deze afstand": "Benzin für diese Distanz",
    "Besparing": "Einsparungen",
    "Verbruik t.o.v. referentie": "Verbrauch vs. Referenz",
    "Nog niet beschikbaar": "Nicht verfügbar",
    "Laden en ritten laden…": "Laden und Fahrten laden…",
    "Vergoeding": "Rückerstattung",
    "Batterij gebruikt": "Batterie verwendet",
    "Laadenergie per dag": "Ladeenergie pro Tag",
    "Verbruik per gemeten rijsegment": "Verbrauch pro gemessenem Fahrabschnitt",
    "prijs ontbreekt": "Preis fehlt",
    "Rittenregistratie nog niet beschikbaar": "Das Fahrtenbuch ist noch nicht verfügbar",
    "prijs": "Preis",
    "prijzen": "Preise",
    "bekend": "Bekannt",
    "zon": "Solar",
    "laadkosten": "Ladekosten",
    "vergoeding": "Erstattung",
    "laadvoordeel": "Ladevorteil",
    "ritten": "Fahrten",
    "__dynamic_battery": "Verbrauch: {capacity} kWh × Änderung des berechneten SoC. Bei den Fahrkosten wird der durchschnittliche Energiepreis in der Batterie zugrunde gelegt. Beim Laden zu Hause ist der EVCC-Wert inklusive entgangenem Export enthalten. Ladeverluste werden nicht gesondert gemessen.",
    "__dynamic_trip": "Kilometerzähler {start} → {end} km. Die Zeiten richten sich nach den erhaltenen Messwerten. Der Verbrauch wird anhand der Batteriewerte unter Verwendung der nutzbaren Kapazität {capacity} kWh geschätzt. Ein Batterieverlust ohne Änderung des Kilometerstands wird gesondert als Verlust im Stand gezählt.{unknown}"
  },
  "nb": {
    "Laden": "Lading",
    "Ritten": "Turer",
    "Verbruik": "Forbruk",
    "Stilstand": "Parkert",
    "Lopende sessie": "Pågående økt",
    "Vernieuwen": "Oppdater",
    "Autohistoriek": "Kjøretøyhistorikk",
    "Laatste laadsessies": "Nylig lading",
    "Laatste ritten": "Siste turer",
    "Alle laadsessies": "Alle ladeøkter",
    "Alle ritten": "Alle turer",
    "Terug naar de laatste drie": "Tilbake til de tre siste",
    "Alle stilstandperiodes": "Alle parkerte perioder",
    "Nog geen laadsessies": "Ingen ladeøkter ennå",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Den første turen vises etter at bilen har rapportert nye målinger.",
    "Ritten en laadkosten laden…": "Laster turer og kostnader for lading…",
    "Laatste stilstandperiodes": "Nylige parkerte perioder",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Ingen batteritap under parkering er registrert ennå.",
    "Laatste rit": "Siste tur",
    "Huidige rit": "Nåværende tur",
    "Sinds laadbeurt": "Siden lading",
    "Sinds laatste laadbeurt": "Siden siste lading",
    "Laatste 100 km": "Siste 100 km",
    "Vandaag": "I dag",
    "Maand": "Måned",
    "Jaar": "År",
    "Gemiddeld verbruik": "Gjennomsnittlig forbruk",
    "Gem. verbruik": "Gjennomsnittlig forbruk",
    "Rijkosten": "Kjørekostnad",
    "Afstand": "Avstand",
    "Naam": "Navn",
    "Kosten": "Kostnader",
    "Verbruikt": "Forbruk",
    "Gebruikt": "Forbrukt",
    "Batterij": "Batteri",
    "Laadkosten": "Ladekostnad",
    "Totaal": "Totalt",
    "Geladen": "Ladet",
    "Gem. tarief": "Gjennomsnittspris",
    "Grafieken & actieradius": "Grafer og rekkevidde",
    "Actieradius bij dit verbruik": "Rekkevidde ved dette forbruket",
    "Rittellers & instellingen": "Triptellere og innstillinger",
    "Rekeninstellingen": "Beregningsinnstillinger",
    "Nieuwe ritteller": "Ny tripteller",
    "Ritteller opnieuw starten": "Tilbakestill tripteller",
    "Ritdetails": "Turdetaljer",
    "Energie gebruikt": "Energi brukt",
    "Batterij bij vertrek": "Batteri ved avgang",
    "Batterij bij aankomst": "Batteri ved ankomst",
    "Duur": "Varighet",
    "Laadsessie toevoegen": "Legg til ladeøkt",
    "Lading controleren": "Se gjennom ladeøkten",
    "Lading bevestigen": "Bekreft lading",
    "Laadprijs": "Ladepris",
    "Laadvoordeel": "Ladefordel",
    "Tarief": "Tariff",
    "Thuis": "Hjemme",
    "Werk": "Arbeid",
    "Snellader": "Hurtiglader",
    "Onderweg": "Borte",
    "Prijs aanvullen": "Legg til pris",
    "Bon & energie": "Kvittering og energi",
    "Berekende energie": "Estimert energi",
    "Gem.": "Gj.sn.",
    "Zon": "Solar",
    "Geladen kWh": "ladet kWh",
    "Prijs per kWh": "Pris per kWh",
    "Totaal op bon (optioneel)": "Totalbeløp på kvitteringen (valgfritt)",
    "Locatie": "Plassering",
    "Start": "Start",
    "Einde": "Slutt",
    "Opslaan": "Lagre",
    "Sluiten": "Lukk",
    "Reset": "Tilbakestill",
    "Meer tonen": "Vis mer",
    "Geschat uit batterijafname": "Estimert fra batterireduksjon",
    "Dit was geen lading": "Dette var ikke en ladeøkt",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Bilen meldte om økt rekkevidde. Bekreft bare hvis det faktisk ble ladet.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Prisen på energien som allerede er i batteriet, trengs for å beregne kjørekostnader fra starten. La feltet stå tomt hvis prisen er ukjent.",
    "Prijs energie bij start van registratie (€/kWh)": "Startpris for energien i batteriet (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Referanseforbruk (kWh/100 km)",
    "Vorige auto (l/100 km)": "Forrige bil (l/100 km)",
    "Benzineprijs (€/l)": "Bensinpris (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Venter på en ny billesing; beholdte verdier skaper ikke en ny tur.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Estimert batteritap mellom avlesninger på samme kilometerteller. Atskilt fra kjøreforbruk; årsaken ble ikke målt.",
    "Rit bezig": "Tur pågår",
    "Meting ontbreekt": "Måling mangler",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Forbruk vises etter den første målte turen.",
    "Vergelijking benzine": "Bensinsammenligning",
    "Benzine voor deze afstand": "Bensin for denne distansen",
    "Besparing": "Besparelser",
    "Verbruik t.o.v. referentie": "Forbruk kontra referanse",
    "Nog niet beschikbaar": "Ikke tilgjengelig",
    "Laden en ritten laden…": "Laster lading og turer...",
    "Vergoeding": "Refusjon",
    "Batterij gebruikt": "Batteri brukt",
    "Laadenergie per dag": "Ladeenergi per dag",
    "Verbruik per gemeten rijsegment": "Forbruk per målt kjøresegment",
    "prijs ontbreekt": "pris mangler",
    "Rittenregistratie nog niet beschikbaar": "Kjøreboken er ikke tilgjengelig ennå",
    "prijs": "pris",
    "prijzen": "priser",
    "bekend": "Kjent",
    "zon": "solenergi",
    "laadkosten": "ladekostnad",
    "vergoeding": "refusjon",
    "laadvoordeel": "ladefordel",
    "ritten": "turer",
    "__dynamic_battery": "Forbruk: {capacity} kWh × endring i beregnet SoC. Kjørekostnad bruker gjennomsnittsprisen på energi i batteriet. Hjemmelading inkluderer EVCC-verdien, inkludert mistet eksport. Ladetap måles ikke separat.",
    "__dynamic_trip": "Kilometerteller {start} → {end} km. Tidene følger de mottatte avlesningene. Forbruket er estimert fra batteriavlesninger ved bruk av {capacity} kWh brukbar kapasitet. Tap uten endring av kilometerteller regnes separat som parkert tap.{unknown}"
  },
  "sv": {
    "Laden": "Laddning",
    "Ritten": "Resor",
    "Verbruik": "Förbrukning",
    "Stilstand": "Parkerad",
    "Lopende sessie": "Pågående session",
    "Vernieuwen": "Uppdatera",
    "Autohistoriek": "Fordonshistorik",
    "Laatste laadsessies": "Senaste laddning",
    "Laatste ritten": "Senaste resor",
    "Alle laadsessies": "Alla laddningssessioner",
    "Alle ritten": "Alla resor",
    "Terug naar de laatste drie": "Tillbaka till de tre senaste",
    "Alle stilstandperiodes": "Alla parkerade perioder",
    "Nog geen laadsessies": "Inga laddningssessioner ännu",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Den första trippen visas efter att bilen rapporterat nya avläsningar.",
    "Ritten en laadkosten laden…": "Laddar laddningssessioner och resor…",
    "Laatste stilstandperiodes": "Senaste parkerade perioder",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Ingen batteriförlust under parkering har registrerats ännu.",
    "Laatste rit": "Senaste resan",
    "Huidige rit": "Nuvarande resa",
    "Sinds laadbeurt": "Sedan laddning",
    "Sinds laatste laadbeurt": "Sedan senaste laddning",
    "Laatste 100 km": "Senaste 100 km",
    "Vandaag": "Idag",
    "Maand": "Månad",
    "Jaar": "År",
    "Gemiddeld verbruik": "Genomsnittlig förbrukning",
    "Gem. verbruik": "Genomsnittlig förbrukning",
    "Rijkosten": "Körkostnad",
    "Afstand": "Avstånd",
    "Naam": "Namn",
    "Kosten": "Kostnad",
    "Verbruikt": "Förbrukning",
    "Gebruikt": "Förbrukat",
    "Batterij": "Batteri",
    "Laadkosten": "Laddningskostnad",
    "Totaal": "Totalt",
    "Geladen": "Laddat",
    "Gem. tarief": "Genomsnittspris",
    "Grafieken & actieradius": "Diagram och räckvidd",
    "Actieradius bij dit verbruik": "Räckvidd vid denna förbrukning",
    "Rittellers & instellingen": "Trippmätare och inställningar",
    "Rekeninstellingen": "Beräkningsinställningar",
    "Nieuwe ritteller": "Ny trippmätare",
    "Ritteller opnieuw starten": "Återställ trippmätare",
    "Ritdetails": "Resedetaljer",
    "Energie gebruikt": "Använd energi",
    "Batterij bij vertrek": "Batteri vid avgång",
    "Batterij bij aankomst": "Batteri vid ankomst",
    "Duur": "Varaktighet",
    "Laadsessie toevoegen": "Lägg till laddning",
    "Lading controleren": "Granska laddningen",
    "Lading bevestigen": "Bekräfta laddningen",
    "Laadprijs": "Laddningspris",
    "Laadvoordeel": "Laddningsförmån",
    "Tarief": "Tariff",
    "Thuis": "Hem",
    "Werk": "Arbete",
    "Snellader": "Snabbladdare",
    "Onderweg": "Borta",
    "Prijs aanvullen": "Lägg till pris",
    "Bon & energie": "Kvitto & energi",
    "Berekende energie": "Uppskattad energi",
    "Gem.": "Genomsn.",
    "Zon": "Solar",
    "Geladen kWh": "Laddad kWh",
    "Prijs per kWh": "Pris per kWh",
    "Totaal op bon (optioneel)": "Belopp på kvittot (valfritt)",
    "Locatie": "Plats",
    "Start": "Start",
    "Einde": "Slut",
    "Opslaan": "Spara",
    "Sluiten": "Stäng",
    "Reset": "Återställ",
    "Meer tonen": "Visa mer",
    "Geschat uit batterijafname": "Uppskattad från batteriminskning",
    "Dit was geen lading": "Detta var inte en laddning",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Bilen rapporterade större räckvidd. Bekräfta endast om den faktiskt har laddats.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Det initiala batteripriset behövs för att beräkna körkostnaden från början. Lämna det tomt om det är okänt.",
    "Prijs energie bij start van registratie (€/kWh)": "Ursprungligt energipris i batteriet (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Referensförbrukning (kWh/100 km)",
    "Vorige auto (l/100 km)": "Tidigare bil (l/100 km)",
    "Benzineprijs (€/l)": "Bensinpris (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Väntar på en ny billäsning; bibehållna värden skapar inte en ny resa.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Beräknad batteriförlust mellan avläsningar på samma vägmätare. Separera från körförbrukning; orsaken mättes inte.",
    "Rit bezig": "Resa pågår",
    "Meting ontbreekt": "Mätning saknas",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Förbrukning visas efter den första uppmätta resan.",
    "Vergelijking benzine": "Bensinjämförelse",
    "Benzine voor deze afstand": "Bensin för denna sträcka",
    "Besparing": "Besparingar",
    "Verbruik t.o.v. referentie": "Förbrukning kontra referens",
    "Nog niet beschikbaar": "Ej tillgängligt",
    "Laden en ritten laden…": "Laddar laddning och resor...",
    "Vergoeding": "Ersättning",
    "Batterij gebruikt": "Batteri använt",
    "Laadenergie per dag": "Laddningsenergi per dag",
    "Verbruik per gemeten rijsegment": "Förbrukning per uppmätt körsegment",
    "prijs ontbreekt": "pris saknas",
    "Rittenregistratie nog niet beschikbaar": "Resebok är inte tillgänglig ännu",
    "prijs": "pris",
    "prijzen": "priser",
    "bekend": "Känd",
    "zon": "solenergi",
    "laadkosten": "laddningskostnad",
    "vergoeding": "ersättning",
    "laadvoordeel": "laddningsförmån",
    "ritten": "resor",
    "__dynamic_battery": "Förbrukning: {capacity} kWh × förändring i beräknad SoC. Körkostnaden använder det genomsnittliga priset för energi i batteriet. Hemladdning inkluderar EVCC-värdet, inklusive utebliven export. Laddningsförluster mäts inte separat.",
    "__dynamic_trip": "Vägmätare {start} → {end} km. Tiderna följer de mottagna avläsningarna. Förbrukningen uppskattas från batteriavläsningar med {capacity} kWh användbar kapacitet. Förlust utan ändring av vägmätarställningen räknas separat som batteriförlust vid parkering.{unknown}"
  },
  "da": {
    "Laden": "Opladning",
    "Ritten": "Ture",
    "Verbruik": "Forbrug",
    "Stilstand": "Parkeret",
    "Lopende sessie": "Løbende session",
    "Vernieuwen": "Opdater",
    "Autohistoriek": "Køretøjshistorie",
    "Laatste laadsessies": "Seneste opladning",
    "Laatste ritten": "Seneste ture",
    "Alle laadsessies": "Alle opladningssessioner",
    "Alle ritten": "Alle ture",
    "Terug naar de laatste drie": "Tilbage til de seneste tre",
    "Alle stilstandperiodes": "Alle parkerede perioder",
    "Nog geen laadsessies": "Ingen opladningssessioner endnu",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Den første tur vises, efter at bilen har rapporteret nye aflæsninger.",
    "Ritten en laadkosten laden…": "Indlæser opladningssessioner og ture…",
    "Laatste stilstandperiodes": "Seneste parkerede perioder",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Der er endnu ikke registreret batteritab under parkering.",
    "Laatste rit": "Sidste tur",
    "Huidige rit": "Nuværende tur",
    "Sinds laadbeurt": "Siden opladning",
    "Sinds laatste laadbeurt": "Siden sidste opladning",
    "Laatste 100 km": "Sidste 100 km",
    "Vandaag": "I dag",
    "Maand": "Måned",
    "Jaar": "År",
    "Gemiddeld verbruik": "Gennemsnitligt forbrug",
    "Gem. verbruik": "Gennemsnitligt forbrug",
    "Rijkosten": "Kørselsomkostninger",
    "Afstand": "Afstand",
    "Naam": "Navn",
    "Kosten": "Omkostninger",
    "Verbruikt": "Forbrug",
    "Gebruikt": "Forbrugt",
    "Batterij": "Batteri",
    "Laadkosten": "Opladningsomkostninger",
    "Totaal": "I alt",
    "Geladen": "Opladet",
    "Gem. tarief": "Gennemsnitspris",
    "Grafieken & actieradius": "Diagrammer og rækkevidde",
    "Actieradius bij dit verbruik": "Rækkevidde ved dette forbrug",
    "Rittellers & instellingen": "Triptællere og indstillinger",
    "Rekeninstellingen": "Beregningsindstillinger",
    "Nieuwe ritteller": "Ny triptæller",
    "Ritteller opnieuw starten": "Nulstil triptæller",
    "Ritdetails": "Turdetaljer",
    "Energie gebruikt": "Energiforbrug",
    "Batterij bij vertrek": "Batteri ved afgang",
    "Batterij bij aankomst": "Batteri ved ankomst",
    "Duur": "Varighed",
    "Laadsessie toevoegen": "Tilføj opladning",
    "Lading controleren": "Gennemgå opladningen",
    "Lading bevestigen": "Bekræft opladningen",
    "Laadprijs": "Opladningspris",
    "Laadvoordeel": "Opladningsfordel",
    "Tarief": "Tarif",
    "Thuis": "Hjemme",
    "Werk": "Arbejde",
    "Snellader": "Hurtigoplader",
    "Onderweg": "På farten",
    "Prijs aanvullen": "Tilføj pris",
    "Bon & energie": "Kvittering og energi",
    "Berekende energie": "Estimeret energi",
    "Gem.": "Gns.",
    "Zon": "Solar",
    "Geladen kWh": "Opladet kWh",
    "Prijs per kWh": "Pris pr. kWh",
    "Totaal op bon (optioneel)": "Beløb på kvitteringen (valgfrit)",
    "Locatie": "Placering",
    "Start": "Start",
    "Einde": "Slut",
    "Opslaan": "Gem",
    "Sluiten": "Luk",
    "Reset": "Nulstil",
    "Meer tonen": "Vis mere",
    "Geschat uit batterijafname": "Estimeret ud fra batterifald",
    "Dit was geen lading": "Dette var ikke en opladning",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Bilen meldte om øget rækkevidde. Bekræft kun, hvis bilen faktisk blev opladet.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Prisen på energien, der allerede er i batteriet, er nødvendig for at beregne kørselsomkostninger fra starten. Lad feltet stå tomt, hvis prisen er ukendt.",
    "Prijs energie bij start van registratie (€/kWh)": "Startpris for energien i batteriet (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Referenceforbrug (kWh/100 km)",
    "Vorige auto (l/100 km)": "Tidligere bil (l/100 km)",
    "Benzineprijs (€/l)": "Benzinpris (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Venter på en frisk billæsning; bevarede værdier skaber ikke en ny tur.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Estimeret batteritab mellem aflæsninger på den samme kilometertæller. Adskilt fra kørselsforbrug; årsagen blev ikke målt.",
    "Rit bezig": "Tur i gang",
    "Meting ontbreekt": "Måling mangler",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Forbrug vises efter den første målte tur.",
    "Vergelijking benzine": "Benzin sammenligning",
    "Benzine voor deze afstand": "Benzin til denne afstand",
    "Besparing": "Besparelser",
    "Verbruik t.o.v. referentie": "Forbrug kontra reference",
    "Nog niet beschikbaar": "Ikke tilgængelig",
    "Laden en ritten laden…": "Indlæser opladning og ture...",
    "Vergoeding": "Refusion",
    "Batterij gebruikt": "Batteri brugt",
    "Laadenergie per dag": "Opladningsenergi pr. dag",
    "Verbruik per gemeten rijsegment": "Forbrug pr. målt køresegment",
    "prijs ontbreekt": "pris mangler",
    "Rittenregistratie nog niet beschikbaar": "Kørselsloggen er ikke tilgængelig endnu",
    "prijs": "pris",
    "prijzen": "priser",
    "bekend": "Kendt",
    "zon": "solenergi",
    "laadkosten": "opladningsomkostninger",
    "vergoeding": "refusion",
    "laadvoordeel": "opladningsfordel",
    "ritten": "ture",
    "__dynamic_battery": "Forbrug: {capacity} kWh × ændring i beregnet SoC. Kørselsomkostninger bruger den gennemsnitlige pris for energi i batteriet. Hjemmeopladning inkluderer EVCC-værdien, inklusive mistet eksport. Opladningstab måles ikke særskilt.",
    "__dynamic_trip": "Kilometertæller {start} → {end} km. Tiderne følger de modtagne aflæsninger. Forbruget er estimeret ud fra batteriaflæsninger ved brug af {capacity} kWh brugbar kapacitet. Tab uden ændring af kilometertæller tælles separat som parkeret tab.{unknown}"
  },
  "cs": {
    "Laden": "Nabíjení",
    "Ritten": "Jízdy",
    "Verbruik": "Spotřeba",
    "Stilstand": "zaparkováno",
    "Lopende sessie": "Probíhající nabíjecí relace",
    "Vernieuwen": "Obnovit",
    "Autohistoriek": "Historie vozidla",
    "Laatste laadsessies": "Nedávné nabíjení",
    "Laatste ritten": "Nedávné cesty",
    "Alle laadsessies": "Všechny nabíjecí relace",
    "Alle ritten": "Všechny cesty",
    "Terug naar de laatste drie": "Zpět na poslední tři",
    "Alle stilstandperiodes": "Všechna zaparkovaná období",
    "Nog geen laadsessies": "Zatím žádné nabíjecí relace",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "První jízda se objeví poté, co vůz nahlásí nové hodnoty.",
    "Ritten en laadkosten laden…": "Načítání jízd a nabíjení…",
    "Laatste stilstandperiodes": "Nedávná zaparkovaná období",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Dosud nebyla zaznamenána žádná ztráta zaparkované baterie.",
    "Laatste rit": "Poslední cesta",
    "Huidige rit": "Aktuální cesta",
    "Sinds laadbeurt": "Od nabití",
    "Sinds laatste laadbeurt": "Od posledního nabití",
    "Laatste 100 km": "Posledních 100 km",
    "Vandaag": "Dnes",
    "Maand": "měsíc",
    "Jaar": "Rok",
    "Gemiddeld verbruik": "Průměrná spotřeba",
    "Gem. verbruik": "Průměrná spotřeba",
    "Rijkosten": "Náklady na jízdu",
    "Afstand": "Vzdálenost",
    "Naam": "Název",
    "Kosten": "Náklady",
    "Verbruikt": "Spotřeba",
    "Gebruikt": "Spotřebováno",
    "Batterij": "Baterie",
    "Laadkosten": "Náklady na nabíjení",
    "Totaal": "Celkem",
    "Geladen": "Nabito",
    "Gem. tarief": "Průměrná cena",
    "Grafieken & actieradius": "Grafy a dojezd",
    "Actieradius bij dit verbruik": "Dojezd při této spotřebě",
    "Rittellers & instellingen": "Počítadla jízd a nastavení",
    "Rekeninstellingen": "Nastavení výpočtu",
    "Nieuwe ritteller": "Nové počítadlo jízd",
    "Ritteller opnieuw starten": "Vynulovat počítadlo jízd",
    "Ritdetails": "Podrobnosti o cestě",
    "Energie gebruikt": "Použitá energie",
    "Batterij bij vertrek": "Baterie při odjezdu",
    "Batterij bij aankomst": "Baterie při příjezdu",
    "Duur": "Délka",
    "Laadsessie toevoegen": "Přidat nabíjení",
    "Lading controleren": "Zkontrolovat nabíjení",
    "Lading bevestigen": "Potvrdit nabíjení",
    "Laadprijs": "Nabíjecí cena",
    "Laadvoordeel": "Výhoda nabíjení",
    "Tarief": "Tarif",
    "Thuis": "Doma",
    "Werk": "Práce",
    "Snellader": "Rychlá nabíječka",
    "Onderweg": "Jinde",
    "Prijs aanvullen": "Přidat cenu",
    "Bon & energie": "Účtenka a energie",
    "Berekende energie": "Odhadovaná energie",
    "Gem.": "Prům.",
    "Zon": "Solární",
    "Geladen kWh": "Nabitá kWh",
    "Prijs per kWh": "Cena za kWh",
    "Totaal op bon (optioneel)": "Celková částka na účtence (volitelné)",
    "Locatie": "Umístění",
    "Start": "Start",
    "Einde": "Konec",
    "Opslaan": "Uložit",
    "Sluiten": "Zavřít",
    "Reset": "Resetovat",
    "Meer tonen": "Zobrazit více",
    "Geschat uit batterijafname": "Odhad z poklesu baterie",
    "Dit was geen lading": "Toto nebylo nabíjení",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Auto hlásilo větší dojezd. Potvrďte pouze, zda byl skutečně nabitý.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Počáteční cena baterie je potřebná pro výpočet jízdních nákladů od začátku. Pokud není znám, ponechte jej prázdné.",
    "Prijs energie bij start van registratie (€/kWh)": "Počáteční cena baterie (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Referenční spotřeba (kWh/100 km)",
    "Vorige auto (l/100 km)": "Předchozí vůz (l/100 km)",
    "Benzineprijs (€/l)": "Cena benzínu (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Čekání na nový údaj o autě; uchované hodnoty nevytvářejí novou jízdu.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Odhadovaná ztráta baterie mezi odečty na stejném počítadle kilometrů. Odděleně od spotřeby jízdy; příčina nebyla změřena.",
    "Rit bezig": "Probíhá cesta",
    "Meting ontbreekt": "Chybí měření",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Spotřeba se objeví po první měřené jízdě.",
    "Vergelijking benzine": "Srovnání benzínu",
    "Benzine voor deze afstand": "Benzín na tuto vzdálenost",
    "Besparing": "Úspory",
    "Verbruik t.o.v. referentie": "Spotřeba versus reference",
    "Nog niet beschikbaar": "Není k dispozici",
    "Laden en ritten laden…": "Načítání nabíjecích relací a jízd…",
    "Vergoeding": "Náhrada",
    "Batterij gebruikt": "Použitá baterie",
    "Laadenergie per dag": "Nabíjecí energie za den",
    "Verbruik per gemeten rijsegment": "Spotřeba na měřený segment jízdy",
    "prijs ontbreekt": "chybí cena",
    "Rittenregistratie nog niet beschikbaar": "Kniha jízd zatím není k dispozici",
    "prijs": "cena",
    "prijzen": "ceny",
    "bekend": "Známé",
    "zon": "solární",
    "laadkosten": "náklady na nabíjení",
    "vergoeding": "úhrada",
    "laadvoordeel": "výhoda nabíjení",
    "ritten": "výlety",
    "__dynamic_battery": "Spotřeba: {capacity} kWh × změna vypočteného SoC. Jízdní náklady využívají průměrnou cenu energie v baterii. Domácí nabíjení zahrnuje hodnotu EVCC, včetně ušlého exportu. Nabíjecí ztráty se neměří samostatně.",
    "__dynamic_trip": "Počítadlo kilometrů {start} → {end} km. Časy následují po přijatých odečtech. Spotřeba se odhaduje na základě údajů z baterie s použitelnou kapacitou {capacity} kWh. Ztráta bez změny počítadla kilometrů se počítá samostatně jako ztráta při parkování.{unknown}"
  },
  "el": {
    "Laden": "Φόρτιση",
    "Ritten": "Ταξίδια",
    "Verbruik": "Κατανάλωση",
    "Stilstand": "Σταθμευμένο",
    "Lopende sessie": "Συνεδρία σε εξέλιξη",
    "Vernieuwen": "Ανανέωση",
    "Autohistoriek": "Ιστορικό οχήματος",
    "Laatste laadsessies": "Πρόσφατη φόρτιση",
    "Laatste ritten": "Πρόσφατα ταξίδια",
    "Alle laadsessies": "Όλες οι συνεδρίες φόρτισης",
    "Alle ritten": "Όλα τα ταξίδια",
    "Terug naar de laatste drie": "Επιστροφή στα πρόσφατα τρία",
    "Alle stilstandperiodes": "Όλες οι περίοδοι στάθμευσης",
    "Nog geen laadsessies": "Δεν υπάρχουν ακόμη περίοδοι χρέωσης",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Το πρώτο ταξίδι εμφανίζεται αφού το αυτοκίνητο αναφέρει νέες μετρήσεις.",
    "Ritten en laadkosten laden…": "Φόρτωση ταξιδιών και φόρτιση…",
    "Laatste stilstandperiodes": "Πρόσφατες περίοδοι στάθμευσης",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Δεν έχει καταγραφεί ακόμη απώλεια σταθμευμένης μπαταρίας.",
    "Laatste rit": "Τελευταίο ταξίδι",
    "Huidige rit": "Τρέχον ταξίδι",
    "Sinds laadbeurt": "Από τη φόρτιση",
    "Sinds laatste laadbeurt": "Από την τελευταία φόρτιση",
    "Laatste 100 km": "Τελευταία 100 χλμ.",
    "Vandaag": "Σήμερα",
    "Maand": "Μήνας",
    "Jaar": "Έτος",
    "Gemiddeld verbruik": "Μέση κατανάλωση",
    "Gem. verbruik": "Μέση κατανάλωση",
    "Rijkosten": "Κόστος οδήγησης",
    "Afstand": "Απόσταση",
    "Naam": "Όνομα",
    "Kosten": "Κόστος",
    "Verbruikt": "Κατανάλωση",
    "Gebruikt": "Κατανάλωση",
    "Batterij": "Μπαταρία",
    "Laadkosten": "Κόστος φόρτισης",
    "Totaal": "Σύνολο",
    "Geladen": "Φορτίστηκε",
    "Gem. tarief": "Μέση τιμή",
    "Grafieken & actieradius": "Γραφήματα και αυτονομία",
    "Actieradius bij dit verbruik": "Αυτονομία με αυτήν την κατανάλωση",
    "Rittellers & instellingen": "Μετρητές και ρυθμίσεις ταξιδιού",
    "Rekeninstellingen": "Ρυθμίσεις υπολογισμού",
    "Nieuwe ritteller": "Νέος μετρητής ταξιδιού",
    "Ritteller opnieuw starten": "Επαναφορά μετρητή ταξιδιού",
    "Ritdetails": "Λεπτομέρειες ταξιδιού",
    "Energie gebruikt": "Ενέργεια που χρησιμοποιείται",
    "Batterij bij vertrek": "Μπαταρία κατά την αναχώρηση",
    "Batterij bij aankomst": "Μπαταρία κατά την άφιξη",
    "Duur": "Διάρκεια",
    "Laadsessie toevoegen": "Προσθήκη φόρτισης",
    "Lading controleren": "Έλεγχος φόρτισης",
    "Lading bevestigen": "Επιβεβαίωση φόρτισης",
    "Laadprijs": "Τιμή φόρτισης",
    "Laadvoordeel": "Όφελος φόρτισης",
    "Tarief": "Ταρίφα",
    "Thuis": "Σπίτι",
    "Werk": "Εργασία",
    "Snellader": "Γρήγορος φορτιστής",
    "Onderweg": "Εκτός σπιτιού",
    "Prijs aanvullen": "Προσθήκη τιμής",
    "Bon & energie": "Απόδειξη & ενέργεια",
    "Berekende energie": "Εκτιμώμενη ενέργεια",
    "Gem.": "Μέσος όρος",
    "Zon": "Ηλιακός",
    "Geladen kWh": "Φορτισμένη kWh",
    "Prijs per kWh": "Τιμή ανά kWh",
    "Totaal op bon (optioneel)": "Συνολικό ποσό στην απόδειξη (προαιρετικό)",
    "Locatie": "Τοποθεσία",
    "Start": "Έναρξη",
    "Einde": "Τέλος",
    "Opslaan": "Αποθήκευση",
    "Sluiten": "Κλείσιμο",
    "Reset": "Επαναφορά",
    "Meer tonen": "Εμφάνιση περισσότερων",
    "Geschat uit batterijafname": "Εκτιμάται από μείωση μπαταρίας",
    "Dit was geen lading": "Αυτή δεν ήταν φόρτιση",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Το αυτοκίνητο ανέφερε μεγαλύτερη αυτονομία. Επιβεβαιώστε μόνο εάν φορτίστηκε πραγματικά.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Η τιμή της ενέργειας που υπάρχει ήδη στην μπαταρία χρειάζεται για τον υπολογισμό του κόστους οδήγησης από την αρχή. Αφήστε το πεδίο κενό αν η τιμή είναι άγνωστη.",
    "Prijs energie bij start van registratie (€/kWh)": "Αρχική τιμή της ενέργειας στην μπαταρία (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Κατανάλωση αναφοράς (kWh/100 km)",
    "Vorige auto (l/100 km)": "Προηγούμενο αυτοκίνητο (l/100 km)",
    "Benzineprijs (€/l)": "Τιμή βενζίνης (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Αναμονή για μια νέα ανάγνωση αυτοκινήτου. Οι τιμές που διατηρούνται δεν δημιουργούν νέο ταξίδι.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Εκτιμώμενη απώλεια μπαταρίας μεταξύ μετρήσεων στο ίδιο χιλιομετρητή. Ξεχωριστή από την κατανάλωση οδήγησης. η αιτία δεν μετρήθηκε.",
    "Rit bezig": "Ταξίδι σε εξέλιξη",
    "Meting ontbreekt": "Λείπει μέτρηση",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Η κατανάλωση εμφανίζεται μετά το πρώτο μετρημένο ταξίδι.",
    "Vergelijking benzine": "Σύγκριση βενζίνης",
    "Benzine voor deze afstand": "Βενζίνη για αυτήν την απόσταση",
    "Besparing": "Αποταμίευση",
    "Verbruik t.o.v. referentie": "Κατανάλωση έναντι αναφοράς",
    "Nog niet beschikbaar": "Μη διαθέσιμο",
    "Laden en ritten laden…": "Φόρτωση συνεδριών φόρτισης και διαδρομών…",
    "Vergoeding": "Αποζημίωση",
    "Batterij gebruikt": "Μπαταρία χρησιμοποιημένη",
    "Laadenergie per dag": "Φόρτιση ενέργειας ανά ημέρα",
    "Verbruik per gemeten rijsegment": "Κατανάλωση ανά μετρημένο τμήμα οδήγησης",
    "prijs ontbreekt": "Λείπει η τιμή",
    "Rittenregistratie nog niet beschikbaar": "Το βιβλίο ταξιδιού δεν είναι ακόμη διαθέσιμο",
    "prijs": "τιμή",
    "prijzen": "τιμές",
    "bekend": "Γνωστό",
    "zon": "ηλιακή ενέργεια",
    "laadkosten": "κόστος χρέωσης",
    "vergoeding": "αποζημίωση",
    "laadvoordeel": "όφελος χρέωσης",
    "ritten": "ταξίδια",
    "__dynamic_battery": "Κατανάλωση: {capacity} kWh × αλλαγή στο υπολογισμένο SoC. Το κόστος οδήγησης χρησιμοποιεί τη μέση τιμή ενέργειας στην μπαταρία. Η οικιακή φόρτιση περιλαμβάνει την τιμή EVCC, συμπεριλαμβανομένης της ενέργειας που δεν εξήχθη. Οι απώλειες φόρτισης δεν μετρώνται χωριστά.",
    "__dynamic_trip": "Χιλιόμετρο {start} → {end} χλμ. Οι χρόνοι ακολουθούν τις ληφθείσες αναγνώσεις. Η κατανάλωση υπολογίζεται από τις μετρήσεις της μπαταρίας χρησιμοποιώντας ωφέλιμη χωρητικότητα {capacity} kWh. Η απώλεια μπαταρίας χωρίς αλλαγή στην ένδειξη του οδομέτρου υπολογίζεται ξεχωριστά ως απώλεια κατά τη στάθμευση.{unknown}"
  },
  "hu": {
    "Laden": "Töltés",
    "Ritten": "Utazások",
    "Verbruik": "Fogyasztás",
    "Stilstand": "Parkolt",
    "Lopende sessie": "Folyamatban lévő töltési esemény",
    "Vernieuwen": "Frissítés",
    "Autohistoriek": "Járműelőzmények",
    "Laatste laadsessies": "Legutóbbi töltés",
    "Laatste ritten": "Legutóbbi utazások",
    "Alle laadsessies": "Minden töltési munkamenet",
    "Alle ritten": "Minden utazás",
    "Terug naar de laatste drie": "Vissza a legutóbbi háromhoz",
    "Alle stilstandperiodes": "Minden parkolási időszak",
    "Nog geen laadsessies": "Még nincsenek töltési folyamatok",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Az első út azután jelenik meg, hogy az autó új értékeket közöl.",
    "Ritten en laadkosten laden…": "Utazások betöltése és töltés…",
    "Laatste stilstandperiodes": "Legutóbbi parkolási időszakok",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Még nem rögzítették a parkoló akkumulátor elvesztését.",
    "Laatste rit": "Utolsó utazás",
    "Huidige rit": "Aktuális utazás",
    "Sinds laadbeurt": "A töltés óta",
    "Sinds laatste laadbeurt": "Az utolsó töltés óta",
    "Laatste 100 km": "Utolsó 100 km",
    "Vandaag": "Ma",
    "Maand": "Hónap",
    "Jaar": "Év",
    "Gemiddeld verbruik": "Átlagfogyasztás",
    "Gem. verbruik": "Átlagfogyasztás",
    "Rijkosten": "Vezetési költség",
    "Afstand": "Távolság",
    "Naam": "Név",
    "Kosten": "Költség",
    "Verbruikt": "Fogyasztás",
    "Gebruikt": "Felhasznált",
    "Batterij": "Akkumulátor",
    "Laadkosten": "Töltési költség",
    "Totaal": "Összesen",
    "Geladen": "Töltve",
    "Gem. tarief": "Átlagár",
    "Grafieken & actieradius": "Diagramok és hatótáv",
    "Actieradius bij dit verbruik": "Hatótáv ennél a fogyasztásnál",
    "Rittellers & instellingen": "Utazásszámlálók és beállítások",
    "Rekeninstellingen": "Számítási beállítások",
    "Nieuwe ritteller": "Új útszámláló",
    "Ritteller opnieuw starten": "Utazásszámláló nullázása",
    "Ritdetails": "Utazás részletei",
    "Energie gebruikt": "Felhasznált energia",
    "Batterij bij vertrek": "Akkumulátor induláskor",
    "Batterij bij aankomst": "Akkumulátor érkezéskor",
    "Duur": "Időtartam",
    "Laadsessie toevoegen": "Töltés hozzáadása",
    "Lading controleren": "Töltés áttekintése",
    "Lading bevestigen": "Töltés megerősítése",
    "Laadprijs": "Töltési ár",
    "Laadvoordeel": "Töltési előny",
    "Tarief": "Tarifa",
    "Thuis": "Otthon",
    "Werk": "Munkahely",
    "Snellader": "Gyorstöltő",
    "Onderweg": "Máshol",
    "Prijs aanvullen": "Ár hozzáadása",
    "Bon & energie": "Nyugta és energia",
    "Berekende energie": "Becsült energia",
    "Gem.": "Átl.",
    "Zon": "Solar",
    "Geladen kWh": "Feltöltött kWh",
    "Prijs per kWh": "Ár kWh-nként",
    "Totaal op bon (optioneel)": "Nyugta végösszege (opcionális)",
    "Locatie": "Hely",
    "Start": "Indítás",
    "Einde": "Vége",
    "Opslaan": "Mentés",
    "Sluiten": "Bezárás",
    "Reset": "Visszaállítás",
    "Meer tonen": "Továbbiak megjelenítése",
    "Geschat uit batterijafname": "Becsült az akkumulátor lemerülése alapján",
    "Dit was geen lading": "Ez nem volt töltés",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Az autó nagyobb hatótávot jelentett. Csak akkor erősítse meg, ha valóban fel van töltve.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Az akkumulátor kezdeti ára a vezetési költségek kezdettől fogva történő kiszámításához szükséges. Ha ismeretlen, hagyja üresen.",
    "Prijs energie bij start van registratie (€/kWh)": "Az akkumulátor kezdeti ára (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Referencia-fogyasztás (kWh/100 km)",
    "Vorige auto (l/100 km)": "Előző autó (l/100 km)",
    "Benzineprijs (€/l)": "Benzin ára (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Friss autóolvasásra várva; a megtartott értékek nem hoznak létre új utat.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Az akkumulátor becsült vesztesége ugyanazon kilométer-számláló mérései között. Elkülönítve a vezetési fogyasztástól; az okot nem mérték fel.",
    "Rit bezig": "Utazás folyamatban",
    "Meting ontbreekt": "Hiányzó mérési adat",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "A fogyasztás az első mért út után jelenik meg.",
    "Vergelijking benzine": "Benzin összehasonlítása",
    "Benzine voor deze afstand": "Benzin erre a távolságra",
    "Besparing": "Megtakarítás",
    "Verbruik t.o.v. referentie": "Fogyasztás versus referencia",
    "Nog niet beschikbaar": "Nem elérhető",
    "Laden en ritten laden…": "Töltési munkamenetek és utak betöltése…",
    "Vergoeding": "Visszatérítés",
    "Batterij gebruikt": "Használt akkumulátor",
    "Laadenergie per dag": "Töltési energia naponta",
    "Verbruik per gemeten rijsegment": "Fogyasztás mért vezetési szegmensenként",
    "prijs ontbreekt": "ár hiányzik",
    "Rittenregistratie nog niet beschikbaar": "Az utazási főkönyv még nem elérhető",
    "prijs": "ár",
    "prijzen": "árak",
    "bekend": "Ismert",
    "zon": "napenergia",
    "laadkosten": "töltési költség",
    "vergoeding": "visszatérítés",
    "laadvoordeel": "töltési előny",
    "ritten": "utazások",
    "__dynamic_battery": "Fogyasztás: {capacity} kWh × a számított SoC változása. A vezetési költség az akkumulátorban lévő energia átlagos árát használja fel. Az otthoni töltés magában foglalja az EVCC-értéket, beleértve az elmaradt exportálást is. A töltési veszteségeket nem mérik külön.",
    "__dynamic_trip": "Kilométerszámláló {start} → {end} km. Az idők a beérkezett értékeket követik. A fogyasztás a {capacity} kWh felhasználható kapacitás felhasználásával az akkumulátor leolvasásaiból becsülhető. A kilométeróra állásának változása nélkül jelentkező akkumulátorveszteség külön, álló helyzetben jelentkező veszteségnek számít.{unknown}"
  },
  "lb": {
    "Laden": "Oplueden",
    "Ritten": "Faarten",
    "Verbruik": "Verbrauch",
    "Stilstand": "Stillstand",
    "Lopende sessie": "Lafend Opluedsessioun",
    "Vernieuwen": "Erfrëschen",
    "Autohistoriek": "Gefierhistorik",
    "Laatste laadsessies": "Lescht Opluedsessiounen",
    "Laatste ritten": "Lescht Faarten",
    "Alle laadsessies": "All Opluedsessiounen",
    "Alle ritten": "All Faarten",
    "Terug naar de laatste drie": "Zréck op déi lescht dräi",
    "Alle stilstandperiodes": "All Perioden am Stillstand",
    "Nog geen laadsessies": "Nach keng Opluedsessiounen",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Déi éischt Faart erschéngt, soubal den Auto nei Miesswäerter iwwerdréit.",
    "Ritten en laadkosten laden…": "Faarten an Opluedkäschte gi gelueden…",
    "Laatste stilstandperiodes": "Lescht Perioden am Stillstand",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Nach kee Réckgang vun der Reechwäit am Stillstand registréiert.",
    "Laatste rit": "Lescht Faart",
    "Huidige rit": "Aktuell Faart",
    "Sinds laadbeurt": "Zënter dem Oplueden",
    "Sinds laatste laadbeurt": "Zënter der leschter Opluedung",
    "Laatste 100 km": "Déi lescht 100 km",
    "Vandaag": "Haut",
    "Maand": "Mount",
    "Jaar": "Joer",
    "Gemiddeld verbruik": "Duerchschnëttsverbrauch",
    "Gem. verbruik": "Duerchschnëttsverbrauch",
    "Rijkosten": "Fuerkäschten",
    "Afstand": "Distanz",
    "Naam": "Numm",
    "Kosten": "Käschten",
    "Verbruikt": "Verbraucht",
    "Gebruikt": "Verbraucht",
    "Batterij": "Batterie",
    "Laadkosten": "Opluedkäschten",
    "Totaal": "Total",
    "Geladen": "Opgelueden",
    "Gem. tarief": "Duerchschnëttspräis",
    "Grafieken & actieradius": "Grafiken a Reechwäit",
    "Actieradius bij dit verbruik": "Reechwäit bei dësem Verbrauch",
    "Rittellers & instellingen": "Faartenzieler an Astellungen",
    "Rekeninstellingen": "Berechnungsastellungen",
    "Nieuwe ritteller": "Neie Faartenzieler",
    "Ritteller opnieuw starten": "Faartenzieler zerécksetzen",
    "Ritdetails": "Faartdetailer",
    "Energie gebruikt": "Verbraucht Energie",
    "Batterij bij vertrek": "Batterie beim Départ",
    "Batterij bij aankomst": "Batterie bei der Arrivée",
    "Duur": "Dauer",
    "Laadsessie toevoegen": "Opluedsessioun derbäisetzen",
    "Lading controleren": "Opluedung iwwerpréiwen",
    "Lading bevestigen": "Opluedung bestätegen",
    "Laadprijs": "Opluedpräis",
    "Laadvoordeel": "Opluedvirdeel",
    "Tarief": "Tarif",
    "Thuis": "Doheem",
    "Werk": "Aarbecht",
    "Snellader": "Schnelllueder",
    "Onderweg": "Ënnerwee",
    "Prijs aanvullen": "Präis ergänzen",
    "Bon & energie": "Quittung an Energie",
    "Berekende energie": "Berechent Energie",
    "Gem.": "Duerchschn.",
    "Zon": "Solarstroum",
    "Geladen kWh": "Opgelueden Energie (kWh)",
    "Prijs per kWh": "Präis pro kWh",
    "Totaal op bon (optioneel)": "Gesamtbetrag op der Quittung (fakultativ)",
    "Locatie": "Standuert",
    "Start": "Start",
    "Einde": "Enn",
    "Opslaan": "Späicheren",
    "Sluiten": "Zoumaachen",
    "Reset": "Zerécksetzen",
    "Meer tonen": "Méi weisen",
    "Geschat uit batterijafname": "Aus dem Réckgang vun der Batterieluedung geschat",
    "Dit was geen lading": "Dëst war keng Opluedung",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Den Auto huet eng méi grouss Reechwäit gemellt. Bestätegt nëmmen, wann tatsächlech geluede gouf.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "De Präis vun der Energie, déi schonn an der Batterie ass, gëtt gebraucht, fir d’Fuerkäschte vun Ufank un ze berechnen. Loosst d’Feld eidel, wann dee Präis onbekannt ass.",
    "Prijs energie bij start van registratie (€/kWh)": "Ufankspräis vun der Energie an der Batterie (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Referenzverbrauch (kWh/100 km)",
    "Vorige auto (l/100 km)": "Viregten Auto (l/100 km)",
    "Benzineprijs (€/l)": "Bensinnspräis (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Waart op eng nei Miessung vum Auto; gespäichert Wäerter maachen nach keng nei Faart aus.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Geschaten Energieverloscht tëscht Miessunge mam selwechte Kilometerstand. Getrennt vum Fuerverbrauch; d’Ursaache goufen net gemooss.",
    "Rit bezig": "Faart amgaang",
    "Meting ontbreekt": "Miessung feelt",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "De Verbrauch gëtt no der éischter gemoossener Faart ugewisen.",
    "Vergelijking benzine": "Verglach mat Bensinn",
    "Benzine voor deze afstand": "Bensinn fir dës Distanz",
    "Besparing": "Aspuerung",
    "Verbruik t.o.v. referentie": "Verbrauch par rapport zur Referenz",
    "Nog niet beschikbaar": "Nach net verfügbar",
    "Laden en ritten laden…": "Opluedsessiounen a Faarte gi gelueden…",
    "Vergoeding": "Remboursement",
    "Batterij gebruikt": "Batterie benotzt",
    "Laadenergie per dag": "Opluedenergie pro Dag",
    "Verbruik per gemeten rijsegment": "Verbrauch pro gemoossene Fueresegment",
    "prijs ontbreekt": "Präis feelt",
    "Rittenregistratie nog niet beschikbaar": "D’Faarteregistréierung ass nach net verfügbar",
    "prijs": "Präis",
    "prijzen": "Präisser",
    "bekend": "Bekannt",
    "zon": "Solarstroum",
    "laadkosten": "Opluedkäschten",
    "vergoeding": "Remboursement",
    "laadvoordeel": "Opluedvirdeel",
    "ritten": "Faarten",
    "__dynamic_battery": "Verbrauch: {capacity} kWh × Ännerung vum berechente Luedstand. D’Fuerkäschte ginn mam duerchschnëttleche Präis vun der Energie an der Batterie berechent. D’Oplueden doheem enthält den EVCC-Wäert, inklusiv dem entgaangenen Export. Opluedverloschter ginn net getrennt gemooss.",
    "__dynamic_trip": "Kilometerstand {start} → {end} km. D’Zäite bezéie sech op déi empfaange Miesswäerter. De Verbrauch gëtt aus de Batteriemiessunge mat enger notzbarer Kapazitéit vun {capacity} kWh geschat. Verloschter bei onverännertem Kilometerstand ginn getrennt als Verloschter am Stillstand gezielt.{unknown}"
  },
  "pl": {
    "Laden": "Ładowanie",
    "Ritten": "Przejazdy",
    "Verbruik": "Zużycie",
    "Stilstand": "Zaparkowany",
    "Lopende sessie": "Trwa sesja",
    "Vernieuwen": "Odśwież",
    "Autohistoriek": "Historia pojazdu",
    "Laatste laadsessies": "Ostatnie ładowanie",
    "Laatste ritten": "Ostatnie podróże",
    "Alle laadsessies": "Wszystkie sesje ładowania",
    "Alle ritten": "Wszystkie przejazdy",
    "Terug naar de laatste drie": "Powrót do ostatnich trzech",
    "Alle stilstandperiodes": "Wszystkie okresy parkowania",
    "Nog geen laadsessies": "Nie ma jeszcze sesji ładowania",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Pierwsza podróż pojawia się po zgłoszeniu przez samochód nowych odczytów.",
    "Ritten en laadkosten laden…": "Wczytywanie sesji ładowania i przejazdów…",
    "Laatste stilstandperiodes": "Ostatnie okresy parkowania",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Nie zarejestrowano jeszcze utraty akumulatora podczas postoju.",
    "Laatste rit": "Ostatni przejazd",
    "Huidige rit": "Bieżący przejazd",
    "Sinds laadbeurt": "Od czasu ładowania",
    "Sinds laatste laadbeurt": "Od ostatniego ładowania",
    "Laatste 100 km": "Ostatnie 100 km",
    "Vandaag": "Dzisiaj",
    "Maand": "Miesiąc",
    "Jaar": "Rok",
    "Gemiddeld verbruik": "Średnie zużycie",
    "Gem. verbruik": "Średnie zużycie",
    "Rijkosten": "Koszt jazdy",
    "Afstand": "Odległość",
    "Naam": "Nazwa",
    "Kosten": "Koszty",
    "Verbruikt": "Zużycie",
    "Gebruikt": "Zużyto",
    "Batterij": "Bateria",
    "Laadkosten": "Koszt ładowania",
    "Totaal": "Razem",
    "Geladen": "Naładowany",
    "Gem. tarief": "Średnia cena",
    "Grafieken & actieradius": "Wykresy i zasięg",
    "Actieradius bij dit verbruik": "Zasięg przy tym zużyciu",
    "Rittellers & instellingen": "Liczniki podróży i ustawienia",
    "Rekeninstellingen": "Ustawienia obliczeń",
    "Nieuwe ritteller": "Nowy licznik podróży",
    "Ritteller opnieuw starten": "Wyzeruj licznik podróży",
    "Ritdetails": "Szczegóły podróży",
    "Energie gebruikt": "Zużyta energia",
    "Batterij bij vertrek": "Akumulator przy wyjeździe",
    "Batterij bij aankomst": "Akumulator po przyjeździe",
    "Duur": "Czas trwania",
    "Laadsessie toevoegen": "Dodaj ładowanie",
    "Lading controleren": "Sprawdź ładowanie",
    "Lading bevestigen": "Potwierdź ładowanie",
    "Laadprijs": "Cena ładowania",
    "Laadvoordeel": "Korzyści z ładowania",
    "Tarief": "Taryfa",
    "Thuis": "Dom",
    "Werk": "Praca",
    "Snellader": "Szybka ładowarka",
    "Onderweg": "Poza domem",
    "Prijs aanvullen": "Dodaj cenę",
    "Bon & energie": "Paragon i energia",
    "Berekende energie": "Szacowana energia",
    "Gem.": "Średnio",
    "Zon": "Energia słoneczna",
    "Geladen kWh": "Naładowane kWh",
    "Prijs per kWh": "Cena za kWh",
    "Totaal op bon (optioneel)": "Łączna kwota na paragonie (opcjonalnie)",
    "Locatie": "Lokalizacja",
    "Start": "Początek",
    "Einde": "Koniec",
    "Opslaan": "Zapisz",
    "Sluiten": "Zamknij",
    "Reset": "Resetuj",
    "Meer tonen": "Pokaż więcej",
    "Geschat uit batterijafname": "Oszacowano na podstawie spadku poziomu naładowania akumulatora",
    "Dit was geen lading": "To nie było ładowanie",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Samochód zgłosił większy zasięg. Potwierdź tylko, jeśli faktycznie został naładowany.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Do obliczenia kosztów jazdy od początku potrzebna jest początkowa cena akumulatora. Jeśli nie jest znane, pozostaw to pole puste.",
    "Prijs energie bij start van registratie (€/kWh)": "Początkowa cena energii w akumulatorze (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Referencyjne zużycie paliwa (kWh/100 km)",
    "Vorige auto (l/100 km)": "Poprzedni samochód (l/100 km)",
    "Benzineprijs (€/l)": "Cena benzyny (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Czekam na nowy odczyt samochodu; zachowane wartości nie powodują utworzenia nowego przejazdu.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Szacowany ubytek akumulatora pomiędzy odczytami na tym samym liczniku przebiegu. Oddzielone od zużycia paliwa; przyczyna nie została zmierzona.",
    "Rit bezig": "Trwa podróż",
    "Meting ontbreekt": "Brak pomiaru",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Zużycie pojawia się po pierwszym zmierzonym przejeździe.",
    "Vergelijking benzine": "Porównanie benzyny",
    "Benzine voor deze afstand": "Benzyna na ten dystans",
    "Besparing": "Oszczędności",
    "Verbruik t.o.v. referentie": "Zużycie w porównaniu do odniesienia",
    "Nog niet beschikbaar": "Niedostępne",
    "Laden en ritten laden…": "Wczytywanie sesji ładowania i przejazdów…",
    "Vergoeding": "Zwrot kosztów",
    "Batterij gebruikt": "Zużyty akumulator",
    "Laadenergie per dag": "Ładowanie energii dziennie",
    "Verbruik per gemeten rijsegment": "Zużycie na zmierzony segment jazdy",
    "prijs ontbreekt": "brak ceny",
    "Rittenregistratie nog niet beschikbaar": "Księga podróży nie jest jeszcze dostępna",
    "prijs": "cena",
    "prijzen": "ceny",
    "bekend": "Znany",
    "zon": "energii słonecznej",
    "laadkosten": "koszt ładowania",
    "vergoeding": "zwrot pieniędzy",
    "laadvoordeel": "korzyść z ładowania",
    "ritten": "wycieczki",
    "__dynamic_battery": "Zużycie: {capacity} kWh × zmiana obliczonego SoC. Koszt jazdy uwzględnia średnią cenę energii w akumulatorze. Ładowanie w domu obejmuje wartość EVCC, w tym utracony eksport. Straty ładowania nie są mierzone osobno.",
    "__dynamic_trip": "Licznik przebiegu {start} → {end} km. Czasy są zgodne z otrzymanymi odczytami. Zużycie szacuje się na podstawie odczytów akumulatora przy wykorzystaniu pojemności użytkowej {capacity} kWh. Strata bez zmiany licznika liczona jest osobno jako strata na postoju.{unknown}"
  },
  "pt": {
    "Laden": "Carregamento",
    "Ritten": "Viagens",
    "Verbruik": "Consumo",
    "Stilstand": "Estacionado",
    "Lopende sessie": "Sessão em andamento",
    "Vernieuwen": "Atualizar",
    "Autohistoriek": "Histórico do veículo",
    "Laatste laadsessies": "Carregamento recente",
    "Laatste ritten": "Viagens recentes",
    "Alle laadsessies": "Todas as sessões de carregamento",
    "Alle ritten": "Todas as viagens",
    "Terug naar de laatste drie": "Voltar aos três últimos",
    "Alle stilstandperiodes": "Todos os períodos estacionados",
    "Nog geen laadsessies": "Ainda não há sessões de carregamento",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "A primeira viagem aparece depois que o carro relata novas leituras.",
    "Ritten en laadkosten laden…": "A carregar sessões de carregamento e viagens…",
    "Laatste stilstandperiodes": "Períodos estacionados recentemente",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Nenhuma perda de bateria estacionada registrada ainda.",
    "Laatste rit": "Última viagem",
    "Huidige rit": "Viagem atual",
    "Sinds laadbeurt": "Desde o carregamento",
    "Sinds laatste laadbeurt": "Desde o último carregamento",
    "Laatste 100 km": "Últimos 100 km",
    "Vandaag": "Hoje",
    "Maand": "Mês",
    "Jaar": "Ano",
    "Gemiddeld verbruik": "Consumo médio",
    "Gem. verbruik": "Consumo médio",
    "Rijkosten": "Custo de condução",
    "Afstand": "Distância",
    "Naam": "Nome",
    "Kosten": "Custos",
    "Verbruikt": "Consumo",
    "Gebruikt": "Consumido",
    "Batterij": "Bateria",
    "Laadkosten": "Custo de carregamento",
    "Totaal": "Total",
    "Geladen": "Carregado",
    "Gem. tarief": "Preço médio",
    "Grafieken & actieradius": "Gráficos e autonomia",
    "Actieradius bij dit verbruik": "Autonomia com este consumo",
    "Rittellers & instellingen": "Contadores de viagem e configurações",
    "Rekeninstellingen": "Configurações de cálculo",
    "Nieuwe ritteller": "Novo contador de viagens",
    "Ritteller opnieuw starten": "Redefinir contador de viagem",
    "Ritdetails": "Detalhes da viagem",
    "Energie gebruikt": "Energia utilizada",
    "Batterij bij vertrek": "Bateria na partida",
    "Batterij bij aankomst": "Bateria na chegada",
    "Duur": "Duração",
    "Laadsessie toevoegen": "Adicionar carregamento",
    "Lading controleren": "Rever carregamento",
    "Lading bevestigen": "Confirmar carregamento",
    "Laadprijs": "Preço de carregamento",
    "Laadvoordeel": "Benefício de carregamento",
    "Tarief": "Tarifa",
    "Thuis": "Casa",
    "Werk": "Trabalho",
    "Snellader": "Carregador rápido",
    "Onderweg": "Fora de casa",
    "Prijs aanvullen": "Adicionar preço",
    "Bon & energie": "Recibo e energia",
    "Berekende energie": "Energia estimada",
    "Gem.": "Média.",
    "Zon": "Solar",
    "Geladen kWh": "kWh carregado",
    "Prijs per kWh": "Preço por kWh",
    "Totaal op bon (optioneel)": "Total no recibo (opcional)",
    "Locatie": "Localização",
    "Start": "Início",
    "Einde": "Fim",
    "Opslaan": "Guardar",
    "Sluiten": "Fechar",
    "Reset": "Redefinir",
    "Meer tonen": "Mostrar mais",
    "Geschat uit batterijafname": "Estimado a partir da diminuição da bateria",
    "Dit was geen lading": "Isto não foi um carregamento",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "O carro reportou mais autonomia. Confirme apenas se houve realmente um carregamento.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "O preço inicial da bateria é necessário para calcular o custo de condução desde o início. Deixe em branco se for desconhecido.",
    "Prijs energie bij start van registratie (€/kWh)": "Preço inicial da energia na bateria (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Consumo de referência (kWh/100 km)",
    "Vorige auto (l/100 km)": "Carro anterior (l/100 km)",
    "Benzineprijs (€/l)": "Preço da gasolina (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Aguardando uma nova leitura do carro; valores retidos não criam uma nova viagem.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Perda estimada de bateria entre leituras no mesmo hodômetro. Separado do consumo de condução; a causa não foi medida.",
    "Rit bezig": "Viagem em andamento",
    "Meting ontbreekt": "Leitura faltando",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "O consumo aparece após a primeira viagem medida.",
    "Vergelijking benzine": "Comparação de gasolina",
    "Benzine voor deze afstand": "Gasolina para esta distância",
    "Besparing": "Economia",
    "Verbruik t.o.v. referentie": "Consumo versus referência",
    "Nog niet beschikbaar": "Não disponível",
    "Laden en ritten laden…": "Carregando carregamento e viagens…",
    "Vergoeding": "Reembolso",
    "Batterij gebruikt": "Bateria usada",
    "Laadenergie per dag": "Carregamento de energia por dia",
    "Verbruik per gemeten rijsegment": "Consumo por segmento de condução medido",
    "prijs ontbreekt": "preço faltando",
    "Rittenregistratie nog niet beschikbaar": "O registro de viagem ainda não está disponível",
    "prijs": "preço",
    "prijzen": "preços",
    "bekend": "Conhecido",
    "zon": "solar",
    "laadkosten": "custo de carregamento",
    "vergoeding": "reembolso",
    "laadvoordeel": "cobrando benefício",
    "ritten": "viagens",
    "__dynamic_battery": "Consumo: {capacity} kWh × alteração no SoC calculado. O custo de condução utiliza o preço médio da energia da bateria. O carregamento em casa inclui o valor do EVCC, incluindo a exportação que deixou de ocorrer. As perdas de carga não são medidas separadamente.",
    "__dynamic_trip": "Hodômetro {start} → {end} km. Os tempos seguem as leituras recebidas. O consumo é estimado a partir das leituras da bateria usando a capacidade útil {capacity} kWh. A perda sem alteração do odómetro é contabilizada separadamente como perda durante o estacionamento.{unknown}"
  },
  "ro": {
    "Laden": "Încărcare",
    "Ritten": "Călătorii",
    "Verbruik": "Consum",
    "Stilstand": "Parcată",
    "Lopende sessie": "Sesiune în curs",
    "Vernieuwen": "Reîmprospătare",
    "Autohistoriek": "Istoricul vehiculului",
    "Laatste laadsessies": "Încărcare recentă",
    "Laatste ritten": "Călătorii recente",
    "Alle laadsessies": "Toate sesiunile de încărcare",
    "Alle ritten": "Toate călătoriile",
    "Terug naar de laatste drie": "Înapoi la ultimele trei",
    "Alle stilstandperiodes": "Toate perioadele parcate",
    "Nog geen laadsessies": "Încă nu există sesiuni de încărcare",
    "De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.": "Prima călătorie apare după ce mașina raportează noi citiri.",
    "Ritten en laadkosten laden…": "Se încarcă sesiunile de încărcare și călătoriile…",
    "Laatste stilstandperiodes": "Perioade parcate recente",
    "Nog geen geregistreerde bereikafname bij stilstand.": "Nu s-a înregistrat încă nicio pierdere a bateriei parcate.",
    "Laatste rit": "Ultima călătorie",
    "Huidige rit": "Călătoria curentă",
    "Sinds laadbeurt": "De la încărcare",
    "Sinds laatste laadbeurt": "De la ultima încărcare",
    "Laatste 100 km": "Ultimii 100 km",
    "Vandaag": "Astăzi",
    "Maand": "Luna",
    "Jaar": "Anul",
    "Gemiddeld verbruik": "Consum mediu",
    "Gem. verbruik": "Consum mediu",
    "Rijkosten": "Costul de conducere",
    "Afstand": "Distanța",
    "Naam": "Nume",
    "Kosten": "Costuri",
    "Verbruikt": "Consum",
    "Gebruikt": "Consumat",
    "Batterij": "Baterie",
    "Laadkosten": "Cost de încărcare",
    "Totaal": "Total",
    "Geladen": "Încărcat",
    "Gem. tarief": "Preț mediu",
    "Grafieken & actieradius": "Diagrame și autonomie",
    "Actieradius bij dit verbruik": "Autonomie la acest consum",
    "Rittellers & instellingen": "Contoare de călătorie și setări",
    "Rekeninstellingen": "Setări de calcul",
    "Nieuwe ritteller": "Contor de parcurs nou",
    "Ritteller opnieuw starten": "Resetează contorul de călătorie",
    "Ritdetails": "Detalii călătorie",
    "Energie gebruikt": "Energie utilizată",
    "Batterij bij vertrek": "Bateria la plecare",
    "Batterij bij aankomst": "Bateria la sosire",
    "Duur": "Durata",
    "Laadsessie toevoegen": "Adăugați încărcare",
    "Lading controleren": "Verificați încărcarea",
    "Lading bevestigen": "Confirmați încărcarea",
    "Laadprijs": "Preț de încărcare",
    "Laadvoordeel": "Avantaj de încărcare",
    "Tarief": "Tarif",
    "Thuis": "Acasă",
    "Werk": "Lucru",
    "Snellader": "Încărcător rapid",
    "Onderweg": "Deplasare",
    "Prijs aanvullen": "Adaugă preț",
    "Bon & energie": "Chitanță și energie",
    "Berekende energie": "Energia estimată",
    "Gem.": "medie",
    "Zon": "Solar",
    "Geladen kWh": "kWh încărcat",
    "Prijs per kWh": "Preț pe kWh",
    "Totaal op bon (optioneel)": "Total chitanță (opțional)",
    "Locatie": "Locație",
    "Start": "Început",
    "Einde": "Sfârșit",
    "Opslaan": "Salvează",
    "Sluiten": "Închide",
    "Reset": "Resetare",
    "Meer tonen": "Arată mai multe",
    "Geschat uit batterijafname": "Estimată din scăderea bateriei",
    "Dit was geen lading": "Aceasta nu a fost o încărcare",
    "De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.": "Mașina a raportat mai multă autonomie. Confirmați doar dacă a fost încărcat efectiv.",
    "De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.": "Prețul energiei deja stocate în baterie este necesar pentru calcularea costului de deplasare de la început. Lăsați câmpul necompletat dacă prețul nu este cunoscut.",
    "Prijs energie bij start van registratie (€/kWh)": "Prețul inițial al energiei din baterie (€/kWh)",
    "Referentieverbruik (kWh/100 km)": "Consum de referință (kWh/100 km)",
    "Vorige auto (l/100 km)": "Mașina precedentă (l/100 km)",
    "Benzineprijs (€/l)": "Prețul benzinei (€/l)",
    "Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.": "Se așteaptă o citire proaspătă a mașinii; valorile păstrate nu creează o nouă călătorie.",
    "Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.": "Pierdere estimată a bateriei între citiri la același odometru. Separat de consumul de conducere; cauza nu a fost măsurată.",
    "Rit bezig": "Călătoria în curs",
    "Meting ontbreekt": "Lipsește măsurarea",
    "Verbruik wordt zichtbaar na de eerste gemeten rit.": "Consumul apare după prima călătorie măsurată.",
    "Vergelijking benzine": "Comparație benzină",
    "Benzine voor deze afstand": "Benzină pentru această distanță",
    "Besparing": "Economii",
    "Verbruik t.o.v. referentie": "Consum față de referință",
    "Nog niet beschikbaar": "Nu este disponibil",
    "Laden en ritten laden…": "Se încarcă încărcarea și călătoriile...",
    "Vergoeding": "Rambursare",
    "Batterij gebruikt": "Bateria folosită",
    "Laadenergie per dag": "Încărcare energie pe zi",
    "Verbruik per gemeten rijsegment": "Consum pe segment de conducere măsurat",
    "prijs ontbreekt": "preț lipsește",
    "Rittenregistratie nog niet beschikbaar": "Registrul de călătorie nu este încă disponibil",
    "prijs": "preț",
    "prijzen": "preturi",
    "bekend": "Cunoscut",
    "zon": "solar",
    "laadkosten": "cost de încărcare",
    "vergoeding": "rambursare",
    "laadvoordeel": "avantaj de încărcare",
    "ritten": "călătorii",
    "__dynamic_battery": "Consum: {capacity} kWh × modificarea SoC-ului calculat. Costul de conducere utilizează prețul mediu al energiei din baterie. Încărcarea acasă include valoarea EVCC, inclusiv energia care nu a mai fost exportată. Pierderile de încărcare nu sunt măsurate separat.",
    "__dynamic_trip": "Odometru {start} → {end} km. Timpurile urmează lecturile primite. Consumul este estimat din citirile bateriei folosind capacitatea utilizabilă {capacity} kWh. Pierderea fără schimbarea contorului de parcurs este socotită separat ca pierdere parcata.{unknown}"
  }
};
const LEDGER_DYNAMIC = {
  "fr": {
    "battery": "Consommation : {capacity} kWh × variation du SoC calculé. Le coût de conduite utilise le prix moyen de l’énergie contenue dans la batterie. La recharge à domicile inclut la valeur EVCC, y compris le renoncement à l'exportation. Les pertes de charge ne sont pas mesurées séparément.",
    "trip": "Compteur kilométrique {start} → {end} km. Les temps suivent les lectures reçues. La consommation est estimée à partir des relevés de la batterie en utilisant la capacité utilisable {capacity} kWh. Les pertes sans changement du compteur kilométrique sont comptées séparément comme des pertes en stationnement.{unknown}",
    "missing": " L’énergie est inconnue en raison de mesures manquantes ou d’une recharge intermédiaire."
  },
  "de": {
    "battery": "Verbrauch: {capacity} kWh × Änderung des berechneten SoC. Bei den Fahrkosten wird der durchschnittliche Energiepreis in der Batterie zugrunde gelegt. Beim Laden zu Hause ist der EVCC-Wert inklusive entgangenem Export enthalten. Ladeverluste werden nicht gesondert gemessen.",
    "trip": "Kilometerzähler {start} → {end} km. Die Zeiten richten sich nach den erhaltenen Messwerten. Der Verbrauch wird anhand der Batteriewerte unter Verwendung der nutzbaren Kapazität {capacity} kWh geschätzt. Verlust ohne Tachowechsel wird gesondert als Parkverlust gezählt.{unknown}",
    "missing": " Energie ist wegen fehlender Messwerte oder zwischenzeitlichen Ladens unbekannt."
  },
  "nb": {
    "battery": "Forbruk: {capacity} kWh × endring i beregnet SoC. Kjørekostnad bruker gjennomsnittsprisen på energi i batteriet. Hjemmelading inkluderer EVCC-verdien, inkludert mistet eksport. Ladetap måles ikke separat.",
    "trip": "Kilometerteller {start} → {end} km. Tidene følger de mottatte avlesningene. Forbruket er estimert fra batteriavlesninger ved bruk av {capacity} kWh brukbar kapasitet. Tap uten endring av kilometerteller regnes separat som parkert tap.{unknown}",
    "missing": " Energi er ukjent på grunn av manglende målinger eller lading underveis."
  },
  "sv": {
    "battery": "Förbrukning: {capacity} kWh × förändring i beräknad SoC. Körkostnaden använder det genomsnittliga priset för energi i batteriet. Hemladdning inkluderar EVCC-värdet, inklusive utebliven export. Laddningsförluster mäts inte separat.",
    "trip": "Vägmätare {start} → {end} km. Tiderna följer de mottagna avläsningarna. Förbrukningen uppskattas från batteriavläsningar med {capacity} kWh användbar kapacitet. Förlust utan vägmätarbyte räknas separat som parkerad förlust.{unknown}",
    "missing": " Energin är okänd på grund av saknade mätningar eller laddning däremellan."
  },
  "da": {
    "battery": "Forbrug: {capacity} kWh × ændring i beregnet SoC. Kørselsomkostninger bruger den gennemsnitlige pris for energi i batteriet. Hjemmeopladning inkluderer EVCC-værdien, inklusive mistet eksport. Opladningstab måles ikke særskilt.",
    "trip": "Kilometertæller {start} → {end} km. Tiderne følger de modtagne aflæsninger. Forbruget er estimeret ud fra batteriaflæsninger ved brug af {capacity} kWh brugbar kapacitet. Tab uden ændring af kilometertæller tælles separat som parkeret tab.{unknown}",
    "missing": " Energi er ukendt på grund af manglende målinger eller opladning undervejs."
  },
  "cs": {
    "battery": "Spotřeba: {capacity} kWh × změna vypočteného SoC. Jízdní náklady využívají průměrnou cenu energie v baterii. Domácí nabíjení zahrnuje hodnotu EVCC, včetně ušlého exportu. Nabíjecí ztráty se neměří samostatně.",
    "trip": "Počítadlo kilometrů {start} → {end} km. Časy následují po přijatých odečtech. Spotřeba se odhaduje na základě údajů z baterie s použitelnou kapacitou {capacity} kWh. Ztráta bez změny počítadla kilometrů se počítá samostatně jako ztráta při parkování.{unknown}",
    "missing": " Energie není známa kvůli chybějícím měřením nebo nabíjení mezi nimi."
  },
  "el": {
    "battery": "Κατανάλωση: {capacity} kWh × αλλαγή στο υπολογισμένο SoC. Το κόστος οδήγησης χρησιμοποιεί τη μέση τιμή ενέργειας στην μπαταρία. Η οικιακή χρέωση περιλαμβάνει την τιμή EVCC, συμπεριλαμβανομένης της μη εξαγωγής. Οι απώλειες χρέωσης δεν μετρώνται χωριστά.",
    "trip": "Χιλιόμετρο {start} → {end} χλμ. Οι χρόνοι ακολουθούν τις ληφθείσες αναγνώσεις. Η κατανάλωση υπολογίζεται από τις μετρήσεις της μπαταρίας χρησιμοποιώντας ωφέλιμη χωρητικότητα {capacity} kWh. Η απώλεια χωρίς αλλαγή χιλιομετρητή υπολογίζεται ξεχωριστά ως απώλεια σταθμευμένης απόστασης.{unknown}",
    "missing": " Η ενέργεια είναι άγνωστη λόγω ελλιπών μετρήσεων ή ενδιάμεσης φόρτισης."
  },
  "hu": {
    "battery": "Fogyasztás: {capacity} kWh × a számított SoC változása. A vezetési költség az akkumulátorban lévő energia átlagos árát használja fel. Az otthoni töltés magában foglalja az EVCC-értéket, beleértve az elmaradt exportálást is. A töltési veszteségeket nem mérik külön.",
    "trip": "Kilométerszámláló {start} → {end} km. Az idők a beérkezett értékeket követik. A fogyasztás a {capacity} kWh felhasználható kapacitás felhasználásával az akkumulátor leolvasásaiból becsülhető. A kilométer-számláló változtatása nélküli veszteség külön parkoló veszteségnek számít.{unknown}",
    "missing": " Az energia hiányzó mérések vagy köztes töltés miatt ismeretlen."
  },
  "lb": {
    "battery": "Verbrauch: {capacity} kWh × Ännerung vum berechente Luedstand. D’Fuerkäschte ginn mam duerchschnëttleche Präis vun der Energie an der Batterie berechent. D’Oplueden doheem enthält den EVCC-Wäert, inklusiv dem entgaangenen Export. Opluedverloschter ginn net getrennt gemooss.",
    "trip": "Kilometerstand {start} → {end} km. D’Zäite bezéie sech op déi empfaange Miesswäerter. De Verbrauch gëtt aus de Batteriemiessunge mat enger notzbarer Kapazitéit vun {capacity} kWh geschat. Verloschter bei onverännertem Kilometerstand ginn getrennt als Verloschter am Stillstand gezielt.{unknown}",
    "missing": " D’Energie ass wéinst feelende Miessungen oder enger Opluedung tëschenduerch onbekannt."
  },
  "pl": {
    "battery": "Zużycie: {capacity} kWh × zmiana obliczonego SoC. Koszt jazdy uwzględnia średnią cenę energii w akumulatorze. Ładowanie w domu obejmuje wartość EVCC, w tym utracony eksport. Straty ładowania nie są mierzone osobno.",
    "trip": "Licznik przebiegu {start} → {end} km. Czasy są zgodne z otrzymanymi odczytami. Zużycie szacuje się na podstawie odczytów akumulatora przy wykorzystaniu pojemności użytkowej {capacity} kWh. Strata bez zmiany licznika liczona jest osobno jako strata na postoju.{unknown}",
    "missing": " Energia jest nieznana z powodu brakujących pomiarów lub ładowania w międzyczasie."
  },
  "pt": {
    "battery": "Consumo: {capacity} kWh × alteração no SoC calculado. O custo de condução utiliza o preço médio da energia da bateria. A cobrança doméstica inclui o valor EVCC, incluindo a renúncia à exportação. As perdas de carga não são medidas separadamente.",
    "trip": "Hodômetro {start} → {end} km. Os tempos seguem as leituras recebidas. O consumo é estimado a partir das leituras da bateria usando a capacidade útil {capacity} kWh. A perda sem alteração do hodômetro é contada separadamente como perda de estacionamento.{unknown}",
    "missing": " A energia é desconhecida devido à falta de medições ou a um carregamento intermédio."
  },
  "ro": {
    "battery": "Consum: {capacity} kWh × modificare a SoC calculat. Costul de conducere utilizează prețul mediu al energiei din baterie. Încărcarea acasă include valoarea EVCC, inclusiv exportul renunțat. Pierderile de încărcare nu sunt măsurate separat.",
    "trip": "Odometru {start} → {end} km. Timpurile urmează lecturile primite. Consumul este estimat din citirile bateriei folosind capacitatea utilizabilă {capacity} kWh. Pierderea fără schimbarea contorului de parcurs este socotită separat ca pierdere parcata.{unknown}",
    "missing": " Energia este necunoscută din cauza măsurătorilor lipsă sau a încărcării între timp."
  },
  "en": {
    "missing": " Energy is unknown because of missing readings or charging."
  }
};
const LEDGER_DYNAMIC_UI={
  en:{missingOne:'Missing prices: 1 · Known cost: {amount} €',missingMany:'Missing prices: {count} · Known cost: {amount} €',unconfirmedOnly:'Unconfirmed sessions: {unconfirmed} · Known cost: {amount} €',withUnconfirmed:'Missing prices: {missing} · Unconfirmed sessions: {unconfirmed} · Known cost: {amount} €',counterReset:'Count “{name}” again from now?',genericError:'The request failed. Please try again.'},
  fr:{missingOne:'Prix manquants : 1 · Coût connu : {amount} €',missingMany:'Prix manquants : {count} · Coût connu : {amount} €',unconfirmedOnly:'Sessions non confirmées : {unconfirmed} · Coût connu : {amount} €',withUnconfirmed:'Prix manquants : {missing} · Sessions non confirmées : {unconfirmed} · Coût connu : {amount} €',counterReset:'Recommencer le compteur « {name} » à partir de maintenant ?',genericError:'La demande a échoué. Veuillez réessayer.'},
  de:{missingOne:'Fehlende Preise: 1 · Bekannte Kosten: {amount} €',missingMany:'Fehlende Preise: {count} · Bekannte Kosten: {amount} €',unconfirmedOnly:'Unbestätigte Ladevorgänge: {unconfirmed} · Bekannte Kosten: {amount} €',withUnconfirmed:'Fehlende Preise: {missing} · Unbestätigte Ladevorgänge: {unconfirmed} · Bekannte Kosten: {amount} €',counterReset:'Zähler „{name}“ ab jetzt neu starten?',genericError:'Die Anfrage ist fehlgeschlagen. Bitte versuchen Sie es erneut.'},
  nb:{missingOne:'Manglende priser: 1 · Kjente kostnader: {amount} €',missingMany:'Manglende priser: {count} · Kjente kostnader: {amount} €',unconfirmedOnly:'Ubekreftede ladeøkter: {unconfirmed} · Kjente kostnader: {amount} €',withUnconfirmed:'Manglende priser: {missing} · Ubekreftede ladeøkter: {unconfirmed} · Kjente kostnader: {amount} €',counterReset:'Skal «{name}» fra nå av telles på nytt?',genericError:'Forespørselen mislyktes. Prøv igjen.'},
  sv:{missingOne:'Saknade priser: 1 · Känd kostnad: {amount} €',missingMany:'Saknade priser: {count} · Känd kostnad: {amount} €',unconfirmedOnly:'Obekräftade laddningar: {unconfirmed} · Känd kostnad: {amount} €',withUnconfirmed:'Saknade priser: {missing} · Obekräftade laddningar: {unconfirmed} · Känd kostnad: {amount} €',counterReset:'Börja räkna ”{name}” från och med nu?',genericError:'Begäran misslyckades. Försök igen.'},
  da:{missingOne:'Manglende priser: 1 · Kendt udgift: {amount} €',missingMany:'Manglende priser: {count} · Kendt udgift: {amount} €',unconfirmedOnly:'Ubekræftede opladninger: {unconfirmed} · Kendt udgift: {amount} €',withUnconfirmed:'Manglende priser: {missing} · Ubekræftede opladninger: {unconfirmed} · Kendt udgift: {amount} €',counterReset:'Skal ”{name}” tælles på ny fra nu?',genericError:'Anmodningen mislykkedes. Prøv igen.'},
  cs:{missingOne:'Chybějící ceny: 1 · Známé náklady: {amount} €',missingMany:'Chybějící ceny: {count} · Známé náklady: {amount} €',unconfirmedOnly:'Nepotvrzená nabíjení: {unconfirmed} · Známé náklady: {amount} €',withUnconfirmed:'Chybějící ceny: {missing} · Nepotvrzená nabíjení: {unconfirmed} · Známé náklady: {amount} €',counterReset:'Začít počítadlo „{name}“ odteď znovu?',genericError:'Požadavek se nezdařil. Zkuste to znovu.'},
  el:{missingOne:'Τιμές που λείπουν: 1 · Γνωστό κόστος: {amount} €',missingMany:'Τιμές που λείπουν: {count} · Γνωστό κόστος: {amount} €',unconfirmedOnly:'Μη επιβεβαιωμένες φορτίσεις: {unconfirmed} · Γνωστό κόστος: {amount} €',withUnconfirmed:'Τιμές που λείπουν: {missing} · Μη επιβεβαιωμένες φορτίσεις: {unconfirmed} · Γνωστό κόστος: {amount} €',counterReset:'Να αρχίσει ξανά η καταμέτρηση «{name}» από τώρα;',genericError:'Το αίτημα απέτυχε. Δοκιμάστε ξανά.'},
  hu:{missingOne:'Hiányzó árak: 1 · Ismert költség: {amount} €',missingMany:'Hiányzó árak: {count} · Ismert költség: {amount} €',unconfirmedOnly:'Nem megerősített töltések: {unconfirmed} · Ismert költség: {amount} €',withUnconfirmed:'Hiányzó árak: {missing} · Nem megerősített töltések: {unconfirmed} · Ismert költség: {amount} €',counterReset:'Újrakezdjük a(z) „{name}” számlálását mostantól?',genericError:'A kérés nem sikerült. Próbálja újra.'},
  lb:{missingOne:'Feelend Präisser: 1 · Bekannt Käschten: {amount} €',missingMany:'Feelend Präisser: {count} · Bekannt Käschten: {amount} €',unconfirmedOnly:'Net bestätegt Opluedsessiounen: {unconfirmed} · Bekannt Käschten: {amount} €',withUnconfirmed:'Feelend Präisser: {missing} · Net bestätegt Opluedsessiounen: {unconfirmed} · Bekannt Käschten: {amount} €',counterReset:'De Faartenzieler „{name}“ vun elo un nei starten?',genericError:'D’Ufro ass feelgeschloen. Probéiert et nach eng Kéier.'},
  pl:{missingOne:'Brakujące ceny: 1 · Znany koszt: {amount} €',missingMany:'Brakujące ceny: {count} · Znany koszt: {amount} €',unconfirmedOnly:'Niepotwierdzone ładowania: {unconfirmed} · Znany koszt: {amount} €',withUnconfirmed:'Brakujące ceny: {missing} · Niepotwierdzone ładowania: {unconfirmed} · Znany koszt: {amount} €',counterReset:'Zacząć liczyć „{name}” od teraz?',genericError:'Nie udało się wykonać żądania. Spróbuj ponownie.'},
  pt:{missingOne:'Preços em falta: 1 · Custo conhecido: {amount} €',missingMany:'Preços em falta: {count} · Custo conhecido: {amount} €',unconfirmedOnly:'Carregamentos não confirmados: {unconfirmed} · Custo conhecido: {amount} €',withUnconfirmed:'Preços em falta: {missing} · Carregamentos não confirmados: {unconfirmed} · Custo conhecido: {amount} €',counterReset:'Recomeçar a contagem de «{name}» a partir de agora?',genericError:'O pedido falhou. Tente novamente.'},
  ro:{missingOne:'Prețuri lipsă: 1 · Cost cunoscut: {amount} €',missingMany:'Prețuri lipsă: {count} · Cost cunoscut: {amount} €',unconfirmedOnly:'Încărcări neconfirmate: {unconfirmed} · Cost cunoscut: {amount} €',withUnconfirmed:'Prețuri lipsă: {missing} · Încărcări neconfirmate: {unconfirmed} · Cost cunoscut: {amount} €',counterReset:'Reîncepeți numărătoarea „{name}” de acum?',genericError:'Solicitarea a eșuat. Încercați din nou.'}
};
const LEDGER_GAP_COPY={
  en:{title:'Unaccounted usage',observed:'Observed',distance:'Distance',battery:'Battery change',complete:'Complete manually',ignore:'Ignore',undo:'Undo',energy:'Energy used',cost:'Actual cost (optional)',currency:'Currency',noConvert:'Enter the actual amount in the selected currency; no conversion is applied.',matched:'Energy and consumption use matched driving segments only; gaps are listed separately.',savedRefresh:'Saved. Refresh history to see the update.',open:'Unaccounted',ignored:'Ignored',manual:'Completed manually',stale:'Source changed',staleHelp:'This interval changed. Refresh the history before editing it.',save:'Save'},
  nl:{title:'Niet geregistreerd verbruik',observed:'Waargenomen',distance:'Afstand',battery:'Batterijverandering',complete:'Handmatig aanvullen',ignore:'Negeren',undo:'Ongedaan maken',energy:'Verbruikte energie',cost:'Werkelijke kosten (optioneel)',currency:'Valuta',noConvert:'Voer het werkelijke bedrag in de gekozen valuta in; er vindt geen omrekening plaats.',matched:'Energie en verbruik gebruiken alleen gematchte rijsegmenten; hiaten staan apart.',savedRefresh:'Opgeslagen. Vernieuw de historiek om de wijziging te zien.',open:'Niet geregistreerd',ignored:'Genegeerd',manual:'Handmatig ingevuld',stale:'Bron gewijzigd',staleHelp:'Dit interval is gewijzigd. Vernieuw de historiek voordat je het bewerkt.',save:'Opslaan'},
  fr:{title:'Utilisation non comptabilisée',observed:'Observé',distance:'Distance',battery:'Variation de la batterie',complete:'Compléter manuellement',ignore:'Ignorer',undo:'Annuler',energy:'Énergie utilisée',cost:'Coût réel (facultatif)',currency:'Devise',noConvert:'Saisissez le montant réel dans la devise choisie ; aucune conversion ne sera appliquée.',matched:'L’énergie et la consommation utilisent uniquement les segments de trajet mesurés ; les lacunes sont affichées séparément.',savedRefresh:'Enregistré. Actualisez l’historique pour voir la modification.',open:'Non comptabilisé',ignored:'Ignoré',manual:'Complété manuellement',stale:'Source modifiée',staleHelp:'Cet intervalle a changé. Actualisez l’historique avant de le modifier.',save:'Enregistrer'},
  de:{title:'Nicht erfasster Verbrauch',observed:'Beobachtet',distance:'Entfernung',battery:'Batterieänderung',complete:'Manuell ergänzen',ignore:'Ignorieren',undo:'Rückgängig',energy:'Verbrauchte Energie',cost:'Tatsächliche Kosten (optional)',currency:'Währung',noConvert:'Geben Sie den tatsächlichen Betrag in der ausgewählten Währung ein; es erfolgt keine Umrechnung.',matched:'Energie und Verbrauch verwenden nur zugeordnete Fahrabschnitte; Lücken werden separat aufgeführt.',savedRefresh:'Gespeichert. Aktualisieren Sie den Verlauf, um die Änderung zu sehen.',open:'Nicht erfasst',ignored:'Ignoriert',manual:'Manuell ergänzt',stale:'Quelle geändert',staleHelp:'Dieses Intervall hat sich geändert. Aktualisieren Sie den Verlauf vor der Bearbeitung.',save:'Speichern'},
  nb:{title:'Ikke registrert forbruk',observed:'Observert',distance:'Avstand',battery:'Batteriendring',complete:'Fyll inn manuelt',ignore:'Ignorer',undo:'Angre',energy:'Brukt energi',cost:'Faktisk kostnad (valgfritt)',currency:'Valuta',noConvert:'Skriv inn det faktiske beløpet i valgt valuta; beløpet omregnes ikke.',matched:'Energi og forbruk bruker bare samsvarende kjøresegmenter; hull vises separat.',open:'Ikke registrert',ignored:'Ignorert',manual:'Ført inn manuelt',stale:'Kilden er endret',staleHelp:'Dette intervallet er endret. Oppdater historikken før du redigerer det.',save:'Lagre'},
  sv:{title:'Oregistrerad förbrukning',observed:'Observerat',distance:'Sträcka',battery:'Batteriförändring',complete:'Komplettera manuellt',ignore:'Ignorera',undo:'Ångra',energy:'Förbrukad energi',cost:'Faktisk kostnad (valfritt)',currency:'Valuta',noConvert:'Ange det faktiska beloppet i vald valuta; ingen omräkning görs.',matched:'Energi och förbrukning omfattar bara matchade körsegment; luckor visas separat.',open:'Oregistrerat',ignored:'Ignorerat',manual:'Manuellt ifyllt',stale:'Källan har ändrats',staleHelp:'Det här intervallet har ändrats. Uppdatera historiken innan du redigerar det.',save:'Spara'},
  da:{title:'Ikke registreret forbrug',observed:'Observeret',distance:'Afstand',battery:'Batteriændring',complete:'Udfyld manuelt',ignore:'Ignorer',undo:'Fortryd',energy:'Brugt energi',cost:'Faktisk udgift (valgfri)',currency:'Valuta',noConvert:'Indtast det faktiske beløb i den valgte valuta; der sker ingen omregning.',matched:'Energi og forbrug omfatter kun matchede kørselssegmenter; huller vises separat.',open:'Ikke registreret',ignored:'Ignoreret',manual:'Udfyldt manuelt',stale:'Kilden er ændret',staleHelp:'Dette interval er ændret. Opdater historikken, før du redigerer det.',save:'Gem'},
  cs:{title:'Nezaznamenaná spotřeba',observed:'Zjištěno',distance:'Vzdálenost',battery:'Změna baterie',complete:'Doplnit ručně',ignore:'Ignorovat',undo:'Vrátit zpět',energy:'Spotřebovaná energie',cost:'Skutečné náklady (volitelné)',currency:'Měna',noConvert:'Zadejte skutečnou částku ve zvolené měně; částka se nepřevádí.',matched:'Energie a spotřeba zahrnují pouze spárované jízdní úseky; mezery jsou uvedeny zvlášť.',open:'Nezaznamenáno',ignored:'Ignorováno',manual:'Doplněno ručně',stale:'Zdroj se změnil',staleHelp:'Tento interval se změnil. Před úpravou obnovte historii.',save:'Uložit'},
  el:{title:'Μη καταγεγραμμένη χρήση',observed:'Παρατηρήθηκε',distance:'Απόσταση',battery:'Μεταβολή μπαταρίας',complete:'Χειροκίνητη συμπλήρωση',ignore:'Παράβλεψη',undo:'Αναίρεση',energy:'Ενέργεια που καταναλώθηκε',cost:'Πραγματικό κόστος (προαιρετικό)',currency:'Νόμισμα',noConvert:'Καταχωρίστε το πραγματικό ποσό στο επιλεγμένο νόμισμα· δεν γίνεται μετατροπή.',matched:'Η ενέργεια και η κατανάλωση περιλαμβάνουν μόνο αντιστοιχισμένα τμήματα οδήγησης· τα κενά εμφανίζονται ξεχωριστά.',open:'Μη καταγεγραμμένο',ignored:'Σε παράβλεψη',manual:'Συμπληρώθηκε χειροκίνητα',stale:'Η πηγή άλλαξε',staleHelp:'Αυτό το διάστημα άλλαξε. Ανανεώστε το ιστορικό πριν από την επεξεργασία.',save:'Αποθήκευση'},
  hu:{title:'Nem rögzített fogyasztás',observed:'Megfigyelt',distance:'Távolság',battery:'Akkumulátor változása',complete:'Kézi kiegészítés',ignore:'Kihagyás',undo:'Visszavonás',energy:'Felhasznált energia',cost:'Tényleges költség (nem kötelező)',currency:'Pénznem',noConvert:'A tényleges összeget a kiválasztott pénznemben adja meg; átváltás nem történik.',matched:'Az energia és a fogyasztás csak az illesztett vezetési szakaszokat tartalmazza; a hiányok külön jelennek meg.',open:'Nincs rögzítve',ignored:'Kihagyva',manual:'Kézzel kiegészítve',stale:'A forrás megváltozott',staleHelp:'Ez az időszak megváltozott. Szerkesztés előtt frissítse az előzményeket.',save:'Mentés'},
  lb:{title:'Net erfaasste Verbrauch',observed:'Festgestallt',distance:'Distanz',battery:'Ännerung vum Batteriestand',complete:'Manuell ergänzen',ignore:'Ignoréieren',undo:'Réckgängeg maachen',energy:'Verbraucht Energie',cost:'Tatsächlech Käschten (optional)',currency:'Währung',noConvert:'Gitt den tatsächleche Betrag an der gewielter Währung an; et gëtt näischt ëmgerechent.',matched:'Energie a Verbrauch baséieren nëmmen op zougeuerdente Fuersegmenter; Lücken ginn separat gewisen.',open:'Net erfaasst',ignored:'Ignoréiert',manual:'Manuell ergänzt',stale:'Quell geännert',staleHelp:'Dësen Intervall huet sech geännert. Erfrëscht d’Historik virum Änneren.',save:'Späicheren'},
  pl:{title:'Niezarejestrowane zużycie',observed:'Zaobserwowano',distance:'Dystans',battery:'Zmiana poziomu akumulatora',complete:'Uzupełnij ręcznie',ignore:'Pomiń',undo:'Cofnij',energy:'Zużyta energia',cost:'Rzeczywisty koszt (opcjonalnie)',currency:'Waluta',noConvert:'Wprowadź rzeczywistą kwotę w wybranej walucie; nie jest przeliczana.',matched:'Energia i zużycie obejmują tylko dopasowane odcinki jazdy; luki są pokazane osobno.',open:'Niezarejestrowane',ignored:'Pominięte',manual:'Uzupełniono ręcznie',stale:'Źródło uległo zmianie',staleHelp:'Ten przedział uległ zmianie. Odśwież historię przed edycją.',save:'Zapisz'},
  pt:{title:'Consumo não registado',observed:'Observado',distance:'Distância',battery:'Variação da bateria',complete:'Completar manualmente',ignore:'Ignorar',undo:'Anular',energy:'Energia utilizada',cost:'Custo real (opcional)',currency:'Moeda',noConvert:'Introduza o valor real na moeda selecionada; não é feita qualquer conversão.',matched:'A energia e o consumo incluem apenas segmentos de condução correspondentes; as lacunas são apresentadas à parte.',open:'Não registado',ignored:'Ignorado',manual:'Preenchido manualmente',stale:'A origem foi alterada',staleHelp:'Este intervalo foi alterado. Atualize o histórico antes de o editar.',save:'Guardar'},
  ro:{title:'Consum neînregistrat',observed:'Observat',distance:'Distanță',battery:'Modificarea bateriei',complete:'Completează manual',ignore:'Ignoră',undo:'Anulează',energy:'Energie consumată',cost:'Cost real (opțional)',currency:'Monedă',noConvert:'Introduceți suma reală în moneda selectată; nu se face conversia.',matched:'Energia și consumul includ doar segmentele de deplasare corespunzătoare; intervalele lipsă sunt afișate separat.',open:'Neînregistrat',ignored:'Ignorat',manual:'Completat manual',stale:'Sursa s-a schimbat',staleHelp:'Acest interval s-a modificat. Reîmprospătați istoricul înainte de editare.',save:'Salvează'}
};
const LEDGER_TRIP_COPY={
 en:{odometer:'Odometer {start} → {end} km. Times follow the received measurements.',measured:'Consumption is estimated from battery measurements using {capacity} kWh usable capacity.',gap:'Trip energy includes matched readings and manually entered intervals; unresolved gaps are listed separately.',parked:'Energy loss without distance change is counted separately as parked loss.',missing:' Energy may be missing because readings are incomplete or charging occurred between them.'},
 nl:{odometer:'Kilometerstand {start} → {end} km. Tijden volgen de ontvangen metingen.',measured:'Verbruik is geschat uit batterijmetingen met {capacity} kWh bruikbare capaciteit.',gap:'Ritenergie omvat gematchte metingen en handmatig ingevulde intervallen; open hiaten staan apart.',parked:'Afname zonder kilometerverandering telt afzonderlijk als stilstandsverlies.',missing:' Energie kan ontbreken door onvolledige metingen of tussentijds laden.'},
 fr:{odometer:'Compteur {start} → {end} km. Les heures suivent les mesures reçues.',measured:'La consommation est estimée à partir des mesures de batterie, avec une capacité utile de {capacity} kWh.',gap:'L’énergie du trajet inclut les mesures correspondantes et les intervalles saisis manuellement ; les lacunes non résolues sont indiquées séparément.',parked:'La perte d’énergie sans distance parcourue est comptée séparément comme perte à l’arrêt.',missing:' Il peut manquer de l’énergie en raison de mesures incomplètes ou d’une recharge entre deux mesures.'},
 de:{odometer:'Kilometerstand {start} → {end} km. Die Zeiten folgen den empfangenen Messungen.',measured:'Der Verbrauch wird anhand der Batteriemessungen bei {capacity} kWh nutzbarer Kapazität geschätzt.',gap:'Die Energie der Fahrt umfasst zugeordnete Messwerte und manuell eingetragene Intervalle; offene Lücken werden separat aufgeführt.',parked:'Energieverlust ohne Entfernungsänderung wird separat als Verlust im Stand gezählt.',missing:' Energie kann wegen unvollständiger Messungen oder einer Ladung zwischen den Messungen fehlen.'},
 nb:{odometer:'Kilometerstand {start} → {end} km. Tidene følger mottatte målinger.',measured:'Forbruket beregnes fra batterimålinger med {capacity} kWh brukbar kapasitet.',gap:'Turenergien omfatter samsvarende målinger og manuelt utfylte intervaller; åpne hull vises separat.',parked:'Energifall uten endring i kjørelengde telles separat som forbruk ved parkering.',missing:' Energi kan mangle på grunn av ufullstendige målinger eller lading mellom målingene.'},
 sv:{odometer:'Vägmätare {start} → {end} km. Tiderna följer de mottagna mätningarna.',measured:'Förbrukningen uppskattas från batterimätningar med {capacity} kWh användbar kapacitet.',gap:'Resans energi omfattar matchade mätningar och manuellt ifyllda intervall; olösta luckor visas separat.',parked:'Energiförlust utan ändrad körsträcka räknas separat som förlust vid parkering.',missing:' Energi kan saknas på grund av ofullständiga mätningar eller laddning mellan mätningarna.'},
 da:{odometer:'Kilometertæller {start} → {end} km. Tiderne følger de modtagne målinger.',measured:'Forbruget estimeres ud fra batterimålinger med {capacity} kWh brugbar kapacitet.',gap:'Turens energi omfatter matchede målinger og manuelt indtastede intervaller; uafklarede huller vises separat.',parked:'Energifald uden ændret afstand tælles separat som tab under parkering.',missing:' Energi kan mangle på grund af ufuldstændige målinger eller opladning mellem målingerne.'},
 cs:{odometer:'Tachometr {start} → {end} km. Časy odpovídají přijatým měřením.',measured:'Spotřeba se odhaduje z měření baterie při využitelné kapacitě {capacity} kWh.',gap:'Energie jízdy zahrnuje spárovaná měření a ručně zadané intervaly; nevyřešené mezery jsou uvedeny samostatně.',parked:'Pokles energie bez změny vzdálenosti se počítá samostatně jako ztráta při stání.',missing:' Energie může chybět kvůli neúplným měřením nebo nabíjení mezi měřeními.'},
 el:{odometer:'Οδόμετρο {start} → {end} km. Οι ώρες ακολουθούν τις μετρήσεις που λήφθηκαν.',measured:'Η κατανάλωση εκτιμάται από τις μετρήσεις της μπαταρίας με ωφέλιμη χωρητικότητα {capacity} kWh.',gap:'Η ενέργεια της διαδρομής περιλαμβάνει αντιστοιχισμένες μετρήσεις και χειροκίνητα συμπληρωμένα διαστήματα· τα ανεπίλυτα κενά εμφανίζονται χωριστά.',parked:'Η απώλεια ενέργειας χωρίς αλλαγή απόστασης υπολογίζεται χωριστά ως απώλεια στάθμευσης.',missing:' Ενέργεια μπορεί να λείπει λόγω ελλιπών μετρήσεων ή φόρτισης μεταξύ μετρήσεων.'},
 hu:{odometer:'Kilométeróra {start} → {end} km. Az időpontok a fogadott méréseket követik.',measured:'A fogyasztás becslése az akkumulátormérésekből, {capacity} kWh használható kapacitással történik.',gap:'Az út energiája tartalmazza az illesztett méréseket és a kézzel megadott időszakokat; a megoldatlan hiányok külön jelennek meg.',parked:'A távolságváltozás nélküli energiacsökkenés külön, álló helyzeti veszteségként szerepel.',missing:' Az energia hiányozhat a hiányos mérések vagy a mérések közötti töltés miatt.'},
 lb:{odometer:'Kilometerstand {start} → {end} km. D’Zäite baséieren op den empfaangene Miessungen.',measured:'De Verbrauch gëtt op Basis vun de Batteriemiessunge mat {capacity} kWh notzbarer Kapazitéit geschat.',gap:'D’Energie vun der Faart ëmfaasst zougeuerdente Miessungen a manuell agetragen Intervalle; net geléiste Lücke ginn separat gewisen.',parked:'Energieverloscht ouni Distanzännerung gëtt separat als Verloscht am Stand gezielt.',missing:' Energie kann duerch onvollstänneg Miessungen oder Lueden tëscht de Miessunge feelen.'},
 pl:{odometer:'Licznik {start} → {end} km. Godziny odpowiadają otrzymanym pomiarom.',measured:'Zużycie jest szacowane na podstawie pomiarów akumulatora przy użytecznej pojemności {capacity} kWh.',gap:'Energia jazdy obejmuje dopasowane pomiary i ręcznie wpisane przedziały; nierozwiązane luki są pokazane osobno.',parked:'Spadek energii bez zmiany dystansu jest liczony osobno jako strata podczas postoju.',missing:' Energii może brakować z powodu niepełnych pomiarów lub ładowania między pomiarami.'},
 pt:{odometer:'Odómetro {start} → {end} km. As horas seguem as medições recebidas.',measured:'O consumo é estimado pelas medições da bateria, com capacidade útil de {capacity} kWh.',gap:'A energia da viagem inclui medições correspondentes e intervalos preenchidos manualmente; as lacunas por resolver são apresentadas à parte.',parked:'A perda de energia sem alteração da distância é contabilizada separadamente como perda em repouso.',missing:' Pode faltar energia devido a medições incompletas ou a carregamento entre medições.'},
 ro:{odometer:'Odometru {start} → {end} km. Orele urmează măsurătorile primite.',measured:'Consumul este estimat din măsurătorile bateriei, folosind capacitatea utilă de {capacity} kWh.',gap:'Energia călătoriei include măsurătorile asociate și intervalele introduse manual; lipsurile nerezolvate sunt afișate separat.',parked:'Scăderea energiei fără modificarea distanței este contabilizată separat ca pierdere în staționare.',missing:' Energia poate lipsi din cauza măsurătorilor incomplete sau a încărcării între măsurători.'}
};
const LEDGER_GAP_EXTRA={
 en:{savedRefresh:'Saved. Refresh history to see the update.',usageHelp:'These fields complete missing driving usage. Enter charging receipts under Add charge in Charging.'},
 nl:{savedRefresh:'Opgeslagen. Vernieuw de historiek om de wijziging te zien.',usageHelp:'Deze velden vullen ontbrekend rijverbruik aan. Voer laadbonnen in via Laadsessie toevoegen bij Laden.'},
 fr:{savedRefresh:'Enregistré. Actualisez l’historique pour voir la modification.',usageHelp:'Ces champs complètent la consommation de conduite manquante. Saisissez les reçus de recharge dans Ajouter une session, sous Recharge.'},
 de:{savedRefresh:'Gespeichert. Aktualisieren Sie den Verlauf, um die Änderung zu sehen.',usageHelp:'Diese Felder ergänzen fehlenden Fahrverbrauch. Ladebelege geben Sie unter Ladevorgänge bei Laden ein.'},
 nb:{savedRefresh:'Lagret. Oppdater historikken for å se endringen.',usageHelp:'Disse feltene kompletterer manglende kjøreenergi. Legg inn ladeboner under Legg til lading i Lading.'},
 sv:{savedRefresh:'Sparat. Uppdatera historiken för att se ändringen.',usageHelp:'Fälten kompletterar saknad körförbrukning. Registrera laddkvitton under Lägg till laddning i Laddning.'},
 da:{savedRefresh:'Gemt. Opdater historikken for at se ændringen.',usageHelp:'Felterne udfylder manglende kørselsforbrug. Indtast ladeboner under Tilføj opladning i Opladning.'},
 cs:{savedRefresh:'Uloženo. Aktualizujte historii, abyste viděli změnu.',usageHelp:'Tato pole doplňují chybějící energii při jízdě. Účtenky za nabíjení zadejte přes Přidat nabíjení v části Nabíjení.'},
 el:{savedRefresh:'Αποθηκεύτηκε. Ανανεώστε το ιστορικό για να δείτε την αλλαγή.',usageHelp:'Αυτά τα πεδία συμπληρώνουν την ενέργεια οδήγησης που λείπει. Καταχωρίστε αποδείξεις φόρτισης από την επιλογή Προσθήκη φόρτισης στην ενότητα Φόρτιση.'},
 hu:{savedRefresh:'Mentve. Frissítse az előzményeket a módosítás megtekintéséhez.',usageHelp:'Ezek a mezők a hiányzó vezetési energia pótlására szolgálnak. Töltési nyugtát a Töltés hozzáadása menüpontban, a Töltés résznél rögzítsen.'},
 lb:{savedRefresh:'Gespäichert. Erfrëscht d’Historik fir d’Ännerung ze gesinn.',usageHelp:'Dës Felder ergänzen de feelende Fuerverbrauch. Laadbonge gitt Dir ënner Laadung bei Laadung dobäi an.'},
 pl:{savedRefresh:'Zapisano. Odśwież historię, aby zobaczyć zmianę.',usageHelp:'Te pola uzupełniają brakujące zużycie energii podczas jazdy. Paragony za ładowanie dodaj w opcji Dodaj ładowanie w sekcji Ładowanie.'},
 pt:{savedRefresh:'Guardado. Atualize o histórico para ver a alteração.',usageHelp:'Estes campos completam a energia de condução em falta. Registe recibos de carregamento em Adicionar carregamento, na secção Carregamento.'},
 ro:{savedRefresh:'Salvat. Reîmprospătați istoricul pentru a vedea modificarea.',usageHelp:'Aceste câmpuri completează energia lipsă din timpul deplasării. Introduceți bonurile de încărcare la Adaugă încărcare în secțiunea Încărcare.'}
};
class CarLedgerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode:'open'}); this.tab='charging'; this.period='month'; this.full=false;
    this.pageSize=36; this.graphUnit='kwh'; this.snapshot=null; this.loading=false; this.error='';
    this._visibility=()=>{if(!document.hidden&&this.isConnected)this.refresh();};
    this._touchStart=e=>{this.touchY=e.touches[0]?.clientY;};
    this._touchEnd=e=>{if(this.touchY!=null&&e.changedTouches[0]?.clientY-this.touchY>110&&window.scrollY<30)this.refresh();this.touchY=null;};
  }
  setConfig(config){this.config=config;this.setAttribute?.('lang',this.displayLocale);this.render();}
  get displayLocale(){return this.config?.language||this._hass?.language||'nl-BE';}
  translate(value){
    const language=(this.displayLocale||'nl').toLowerCase().split(/[-_]/)[0];
    if(language==='nl')return value;
    const locale=Object.prototype.hasOwnProperty.call(LEDGER_TRANSLATIONS,language)?language:'en';
    const raw=String(value),leading=raw.match(/^\s*/)[0],trailing=raw.match(/\s*$/)[0],middle=raw.trim();
    const exact=key=>LEDGER_TRANSLATIONS[locale]?.[key]||LEDGER_ENGLISH[key]||key;
    const monthlyCharge=middle.match(/^([\d.,\s−—-]+) kWh · ([\d.,\s−—-]+) (€|[A-Z]{3}) laadkosten(?: · ([\d.,\s−—-]+) (€|[A-Z]{3}) vergoeding · ([\d.,\s−—-]+) (€|[A-Z]{3}) laadvoordeel)?$/);
    if(monthlyCharge)return leading+`${monthlyCharge[1].trim()} kWh · ${monthlyCharge[2].trim()} ${monthlyCharge[3]} ${exact('laadkosten')}`+(monthlyCharge[4]?` · ${monthlyCharge[4].trim()} ${monthlyCharge[5]} ${exact('vergoeding')} · ${monthlyCharge[6].trim()} ${monthlyCharge[7]} ${exact('laadvoordeel')}`:'')+trailing;
    const monthlyTrips=middle.match(/^([\d.,\s−—-]+) km · ([\d.,\s−—-]+) kWh\/100 km · (\d+) ritten$/);
    if(monthlyTrips)return leading+`${monthlyTrips[1].trim()} km · ${monthlyTrips[2].trim()} kWh/100 km · ${monthlyTrips[3]} ${exact('ritten')}`+trailing;
    const activeCharge=middle.match(/^(.+?) · Lopende sessie$/);
    if(activeCharge)return leading+activeCharge[1]+' · '+exact('Lopende sessie')+trailing;
    const solarOnly=middle.match(/^·\s*(.+?)% zon$/);
    if(solarOnly)return leading+'· '+solarOnly[1]+'% '+exact('zon')+trailing;
    const averageLine=middle.match(/^Gem\. (.+?) kWh\/100 km$/);
    if(averageLine)return leading+exact('Gem.')+' '+averageLine[1]+' kWh/100 km'+trailing;
    const combinedNotice=middle.match(/^Ontbrekende prijzen: (\d+) · Niet-bevestigde sessies: (\d+) · Bekende kosten: (.+?) (€|[A-Z]{3})(?: · .+)?$/);
    if(combinedNotice){const template=(LEDGER_DYNAMIC_UI[locale]||LEDGER_DYNAMIC_UI.en).withUnconfirmed;return leading+template.replace('{missing}',combinedNotice[1]).replace('{unconfirmed}',combinedNotice[2]).replace('{amount}',combinedNotice[3]).replace(/ €/g,` ${combinedNotice[4]}`)+trailing;}
    const missingPrices=middle.match(/^Ontbrekende prijzen: (\d+) · Bekende kosten: (.+?) (€|[A-Z]{3})$/);
    if(missingPrices){const templates=LEDGER_DYNAMIC_UI[locale]||LEDGER_DYNAMIC_UI.en,template=Number(missingPrices[1])===1?templates.missingOne:templates.missingMany;return leading+template.replace('{count}',missingPrices[1]).replace('{amount}',missingPrices[2]).replace(/ €/g,` ${missingPrices[3]}`)+trailing;}
    const unconfirmedNotice=middle.match(/^Niet-bevestigde sessies: (\d+) · Bekende kosten: (.+?) (€|[A-Z]{3})$/);
    if(unconfirmedNotice){const template=(LEDGER_DYNAMIC_UI[locale]||LEDGER_DYNAMIC_UI.en).unconfirmedOnly;return leading+template.replace('{unconfirmed}',unconfirmedNotice[1]).replace('{amount}',unconfirmedNotice[2]).replace(/ €/g,` ${unconfirmedNotice[3]}`)+trailing;}
    const chargeNote=middle.match(/^Vergoeding (.+?) (€|[A-Z]{3})(?: · (.+?)% zon)?$/);
    if(chargeNote)return leading+exact('Vergoeding')+' '+chargeNote[1]+' '+chargeNote[2]+(chargeNote[3]?` · ${chargeNote[3]}% ${exact('zon')}`:'')+trailing;
    const tripMissing=middle.match(/^(.+?% → .+?%) · Meting ontbreekt$/);
    if(tripMissing)return leading+tripMissing[1]+' · '+exact('Meting ontbreekt')+trailing;
    const more=middle.match(/^Meer tonen \((\d+)\)$/);
    if(more)return leading+exact('Meer tonen')+' ('+more[1]+')'+trailing;
    const tripCount=middle.match(/^(\d+) ritten$/i);
    if(tripCount)return leading+tripCount[1]+' '+exact('Ritten').toLocaleLowerCase(locale)+trailing;
    const battery=middle.match(/^Verbruik: (.+?) kWh × verschil in berekende SoC\. Rijkosten gebruiken de gemiddelde prijs van de energie in de batterij\. Thuis telt de EVCC-waarde mee, inclusief misgelopen teruglevering\. Laadverliezen zijn niet afzonderlijk gemeten\.$/);
    if(battery){const template=LEDGER_DYNAMIC[locale]?.battery||'Consumption: {capacity} kWh × change in calculated SoC. Driving cost uses the average price of energy in the battery. Home charging includes the EVCC value, including foregone export. Charging losses are not measured separately.';return leading+template.replace('{capacity}',battery[1])+trailing;}
    const trip=middle.match(/^Kilometerstand (.+?) → (.+?) km\. Tijden volgen de ontvangen metingen\. Verbruik is geschat uit batterijmetingen met (.+?) kWh bruikbare capaciteit\. Afname zonder kilometerverandering telt afzonderlijk als stilstandsverlies\.(.*)$/);
    if(trip){const unknown=trip[4]?(LEDGER_DYNAMIC[locale]?.missing||LEDGER_DYNAMIC.en?.missing||' Energy is unknown because of missing readings or charging.'):'';const template=LEDGER_DYNAMIC[locale]?.trip||'Odometer {start} → {end} km. Times follow the received readings. Consumption is estimated from battery readings using {capacity} kWh usable capacity. Loss without odometer change is counted separately as parked loss.{unknown}';let result=template.replace('{start}',trip[1]).replace('{end}',trip[2]).replace('{capacity}',trip[3]).replace('{unknown}',unknown);return leading+result+trailing;}
    // Translate complete phrases only. Substring replacement can corrupt
    // arbitrary record names, server messages, identifiers, and values.
    const result=LEDGER_TRANSLATIONS[locale]?.[middle]||LEDGER_ENGLISH[middle]||middle;
    return leading+(result||middle)+trailing;
  }
  localize(root=this.shadowRoot){
    if(this.displayLocale.toLowerCase().startsWith('nl'))return;
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    for(let node=walker.nextNode();node;node=walker.nextNode()){
      if(node.parentElement?.closest('[data-user-content],[translate="no"]'))continue;
      node.textContent=this.translate(node.textContent);
    }
    for(const element of root.querySelectorAll('[title],[aria-label],[placeholder]')){
      if(element.closest('[data-user-content],[translate="no"]'))continue;
      for(const name of ['title','aria-label','placeholder'])if(element.hasAttribute(name))element.setAttribute(name,this.translate(element.getAttribute(name)));
    }
  }
  localizeError(error,fallback=''){
    const message=String(error?.message??error??'').trim();
    if(!message)return fallback||'Rittenregistratie nog niet beschikbaar';
    const canonical=Object.keys(LEDGER_ENGLISH).find(source=>source===message||LEDGER_ENGLISH[source]===message||Object.values(LEDGER_TRANSLATIONS).some(map=>map[source]===message));
    if(canonical)return canonical;
    if(/^Verbruik: .+ kWh × verschil in berekende SoC\./.test(message)||/^Kilometerstand .+ → .+ km\. Tijden volgen/.test(message))return message;
    const locale=this.displayLocale.toLowerCase().split(/[-_]/)[0];
    return locale==='nl'?'Er is iets misgegaan. Probeer het opnieuw.':(LEDGER_DYNAMIC_UI[locale]||LEDGER_DYNAMIC_UI.en).genericError;
  }
  counterResetPrompt(name){
    const locale=this.displayLocale.toLowerCase().split(/[-_]/)[0],template=locale==='nl'?'“{name}” vanaf nu opnieuw tellen?':(LEDGER_DYNAMIC_UI[locale]||LEDGER_DYNAMIC_UI.en).counterReset;
    const safe=this.esc(name),marker=`<span data-user-content translate="no">${safe}</span>`;
    return this.esc(template.slice(0,template.indexOf('{name}')))+marker+this.esc(template.slice(template.indexOf('{name}')+6));
  }
  getCardSize(){return 8;}
  getGridOptions(){return {columns:12,rows:'auto'};}
  set hass(hass){this._hass=hass;if(!this.snapshot&&!this.loading&&this.isConnected)this.refresh();}
  connectedCallback(){
    // Set the scanner exclusion after construction (custom-element constructors
    // must not add attributes), but before this card creates localized content.
    this.setAttribute?.('data-i18n-ignore','');this.setAttribute?.('translate','no');this.setAttribute?.('lang',this.displayLocale);
    document.addEventListener('visibilitychange',this._visibility);this.addEventListener('touchstart',this._touchStart,{passive:true});this.addEventListener('touchend',this._touchEnd,{passive:true});if(this._hass)this.refresh();
  }
  disconnectedCallback(){document.removeEventListener('visibilitychange',this._visibility);this.removeEventListener('touchstart',this._touchStart);this.removeEventListener('touchend',this._touchEnd);}
  async refresh(){
    if(!this._hass||this.loading)return;this.loading=true;this.refreshState();
    try{this.snapshot=this.prepareSnapshot(await this._hass.callWS({type:'nio_telematics/car_dashboard/get',entry_id:this.config.entry_id}));this.error='';this.render();}
    catch(e){this.error=this.localizeError(e,'Rittenregistratie nog niet beschikbaar');if(!this.snapshot)this.render();else this.refreshState();}
    finally{this.loading=false;this.refreshState();}
  }
  refreshState(){const b=this.shadowRoot.querySelector('[data-action="refresh"]');if(b){b.disabled=this.loading;b.setAttribute('aria-busy',String(this.loading));}const err=this.shadowRoot.querySelector('.error');if(err)err.textContent=this.translate(this.error);}
  esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  n(v,d=1){return v==null||!Number.isFinite(Number(v))?'—':Number(v).toLocaleString(this.displayLocale,{minimumFractionDigits:d,maximumFractionDigits:d});}
  currencyCode(currency){return /^[A-Z]{3}$/.test(String(currency||''))?String(currency):'EUR';}
  accountingCurrency(){return this.currencyCode(this.snapshot?.currency||'EUR');}
  moneyUnit(currency=this.accountingCurrency()){return currency==='EUR'?'€':currency;}
  money(v,currency=this.accountingCurrency(),digits=2){return `${this.n(v,digits)} ${this.moneyUnit(this.currencyCode(currency))}`;}
  moneyRateUnit(currency=this.accountingCurrency()){return `${this.moneyUnit(this.currencyCode(currency))}/kWh`;}
  currencyLabel(){const lang=(this.displayLocale||'en').toLowerCase().split(/[-_]/)[0];return ({en:'Currency',nl:'Valuta',fr:'Devise',de:'Währung',nb:'Valuta',sv:'Valuta',da:'Valuta',cs:'Měna',el:'Νόμισμα',hu:'Pénznem',lb:'Währung',pl:'Waluta',pt:'Moeda',ro:'Monedă'})[lang]||'Currency';}
  currencyHelp(){const lang=(this.displayLocale||'en').toLowerCase().split(/[-_]/)[0];return ({en:'Changing currency does not convert saved prices. Reenter each monetary price in the new currency or leave it blank if unknown.',nl:'Een valutawijziging rekent opgeslagen prijzen niet om. Voer elke geldprijs opnieuw in de nieuwe valuta in of laat die leeg als de prijs onbekend is.',fr:'Le changement de devise ne convertit pas les prix enregistrés. Saisissez à nouveau chaque prix dans la nouvelle devise ou laissez-le vide s’il est inconnu.',de:'Ein Währungswechsel rechnet gespeicherte Preise nicht um. Geben Sie jeden Geldbetrag in der neuen Währung erneut ein oder lassen Sie ihn leer, wenn er unbekannt ist.',nb:'Valutabyttet regner ikke om lagrede priser. Skriv inn hver pengepris på nytt i den nye valutaen, eller la den stå tom hvis den er ukjent.',sv:'Valutabyte räknar inte om sparade priser. Ange varje penningpris på nytt i den nya valutan eller lämna det tomt om det är okänt.',da:'Valutaskift omregner ikke gemte priser. Indtast hver pengepris igen i den nye valuta, eller lad den være tom, hvis den er ukendt.',cs:'Změna měny nepřepočítá uložené ceny. Zadejte každou peněžní cenu znovu v nové měně nebo ji nechte prázdnou, pokud není známa.',el:'Η αλλαγή νομίσματος δεν μετατρέπει τις αποθηκευμένες τιμές. Εισαγάγετε ξανά κάθε χρηματική τιμή στο νέο νόμισμα ή αφήστε την κενή αν είναι άγνωστη.',hu:'A pénznem módosítása nem váltja át a mentett árakat. Adja meg újra az egyes árakat az új pénznemben, vagy hagyja üresen, ha nem ismert.',lb:'Eng Währungsännerung rechent gespäichert Präisser net ëm. Gitt all Geldpräis an der neier Währung nei an oder loosst en eidel, wann en onbekannt ass.',pl:'Zmiana waluty nie przelicza zapisanych cen. Wprowadź ponownie każdą cenę w nowej walucie lub pozostaw ją pustą, jeśli jest nieznana.',pt:'A alteração da moeda não converte os preços guardados. Volte a introduzir cada preço na nova moeda ou deixe-o em branco se for desconhecido.',ro:'Schimbarea monedei nu convertește prețurile salvate. Introduceți din nou fiecare preț în noua monedă sau lăsați-l necompletat dacă este necunoscut.'})[lang]||'Changing currency does not convert saved prices. Reenter each monetary price in the new currency or leave it blank if unknown.';}
  currencyNotice(kind){const lang=(this.displayLocale||'en').toLowerCase().split(/[-_]/)[0],copy={
    en:{mixed:'Costs in different currencies are kept separate; no converted total is shown.',conflict:'This saved amount uses a different currency than the current entry. The original amount and currency are preserved.'},
    nl:{mixed:'Kosten in verschillende valuta blijven apart; er wordt geen omgerekend totaal getoond.',conflict:'Dit opgeslagen bedrag gebruikt een andere valuta dan deze invoer. Bedrag en valuta blijven behouden.'},
    fr:{mixed:'Les coûts dans différentes devises restent séparés ; aucun total converti n’est affiché.',conflict:'Ce montant enregistré utilise une autre devise. Le montant et la devise d’origine sont conservés.'},
    de:{mixed:'Kosten in verschiedenen Währungen bleiben getrennt; eine umgerechnete Summe wird nicht angezeigt.',conflict:'Dieser gespeicherte Betrag verwendet eine andere Währung. Betrag und ursprüngliche Währung bleiben erhalten.'},
    nb:{mixed:'Kostnader i ulike valutaer holdes adskilt; ingen omregnet sum vises.',conflict:'Dette lagrede beløpet bruker en annen valuta. Beløp og opprinnelig valuta beholdes.'},
    sv:{mixed:'Kostnader i olika valutor hålls isär; ingen omräknad summa visas.',conflict:'Det här sparade beloppet använder en annan valuta. Beloppet och den ursprungliga valutan behålls.'},
    da:{mixed:'Omkostninger i forskellige valutaer holdes adskilt; ingen omregnet sum vises.',conflict:'Dette gemte beløb bruger en anden valuta. Beløbet og den oprindelige valuta bevares.'},
    cs:{mixed:'Náklady v různých měnách zůstávají oddělené; přepočtený součet se nezobrazuje.',conflict:'Tato uložená částka používá jinou měnu. Částka i původní měna zůstávají zachovány.'},
    el:{mixed:'Τα κόστη σε διαφορετικά νομίσματα παραμένουν ξεχωριστά· δεν εμφανίζεται μετατρεπόμενο σύνολο.',conflict:'Αυτό το αποθηκευμένο ποσό χρησιμοποιεί διαφορετικό νόμισμα. Το αρχικό ποσό και νόμισμα διατηρούνται.'},
    hu:{mixed:'A különböző pénznemű költségek külön maradnak; átszámított összeg nem jelenik meg.',conflict:'Ez a mentett összeg más pénznemet használ. Az eredeti összeg és pénznem megmarad.'},
    lb:{mixed:'Käschten a verschiddene Währunge bleiwen getrennt; et gëtt kee ëmgerechent Total gewisen.',conflict:'Dëse gespäicherte Betrag benotzt eng aner Währung. Den urspréngleche Betrag an d’Währung bleiwen erhalen.'},
    pl:{mixed:'Koszty w różnych walutach pozostają oddzielone; przeliczona suma nie jest wyświetlana.',conflict:'Ta zapisana kwota używa innej waluty. Oryginalna kwota i waluta pozostają zachowane.'},
    pt:{mixed:'Os custos em moedas diferentes permanecem separados; não é apresentado um total convertido.',conflict:'Este valor guardado usa outra moeda. O valor e a moeda originais são mantidos.'},
    ro:{mixed:'Costurile în monede diferite rămân separate; nu este afișat un total convertit.',conflict:'Această sumă salvată folosește altă monedă. Suma și moneda originale sunt păstrate.'}
  };return (copy[lang]||copy.en)[kind];}
  historyCurrencyWarning(warning){
    if(warning?.code!=='history_currency_assumed')return '';
    const lang=(this.displayLocale||'en').toLowerCase().split(/[-_]/)[0],copy={
      en:'Check history currency. {source} does not declare its currency. New costs use {current}; earlier imported records use {previous}. Declare the source’s actual currency before relying on these amounts.',
      nl:'Controleer de historiekvaluta. {source} vermeldt geen valuta. Nieuwe kosten gebruiken {current}; eerder geïmporteerde records gebruiken {previous}. Stel de werkelijke valuta van de bron in voordat je op deze bedragen vertrouwt.',
      fr:'Vérifiez la devise de l’historique. {source} ne déclare aucune devise. Les nouveaux coûts utilisent {current} ; les anciens enregistrements importés utilisent {previous}. Déclarez la devise réelle de la source avant de vous fier à ces montants.',
      de:'Prüfen Sie die Währung des Verlaufs. {source} gibt keine Währung an. Neue Kosten verwenden {current}; ältere importierte Einträge verwenden {previous}. Legen Sie die tatsächliche Währung der Quelle fest, bevor Sie sich auf diese Beträge verlassen.',
      nb:'Kontroller valutaen i historikken. {source} oppgir ikke valuta. Nye kostnader bruker {current}; eldre importerte oppføringer bruker {previous}. Angi kildens faktiske valuta før du stoler på beløpene.',
      sv:'Kontrollera historikens valuta. {source} anger ingen valuta. Nya kostnader använder {current}; äldre importerade poster använder {previous}. Ange källans faktiska valuta innan du förlitar dig på beloppen.',
      da:'Kontrollér historikkens valuta. {source} angiver ingen valuta. Nye omkostninger bruger {current}; ældre importerede poster bruger {previous}. Angiv kildens faktiske valuta, før du stoler på beløbene.',
      cs:'Zkontrolujte měnu historie. {source} měnu neuvádí. Nové náklady používají {current}; starší importované záznamy používají {previous}. Před spoléháním na tyto částky nastavte skutečnou měnu zdroje.',
      el:'Ελέγξτε το νόμισμα του ιστορικού. Το {source} δεν δηλώνει νόμισμα. Τα νέα κόστη χρησιμοποιούν {current}· οι παλαιότερες εισαγόμενες εγγραφές χρησιμοποιούν {previous}. Δηλώστε το πραγματικό νόμισμα της πηγής πριν βασιστείτε σε αυτά τα ποσά.',
      hu:'Ellenőrizze az előzmények pénznemét. A(z) {source} nem ad meg pénznemet. Az új költségek pénzneme {current}; a korábban importált bejegyzéseké {previous}. Az összegek használata előtt adja meg a forrás tényleges pénznemét.',
      lb:'Kontrolléiert d’Währung vun der Historik. {source} gëtt keng Währung un. Nei Käschte benotzen {current}; méi al importéiert Entréeë benotzen {previous}. Gitt déi tatsächlech Währung vun der Quell un, ier Dir Iech op dës Beträg verloosst.',
      pl:'Sprawdź walutę historii. {source} nie określa waluty. Nowe koszty używają {current}; starsze zaimportowane wpisy używają {previous}. Podaj rzeczywistą walutę źródła, zanim oprzesz się na tych kwotach.',
      pt:'Verifique a moeda do histórico. {source} não declara uma moeda. Os novos custos usam {current}; os registos importados mais antigos usam {previous}. Indique a moeda real da origem antes de confiar nestes valores.',
      ro:'Verificați moneda istoricului. {source} nu declară moneda. Costurile noi folosesc {current}; înregistrările importate mai vechi folosesc {previous}. Declarați moneda reală a sursei înainte de a vă baza pe aceste sume.'
    };
    const values={source:String(warning.source||''),current:String(warning.currency||''),previous:Array.isArray(warning.previous_currencies)?warning.previous_currencies.join(', '):''};
    return (copy[lang]||copy.en).replace(/\{(source|current|previous)\}/g,(_match,key)=>values[key]);
  }
  gapCopy(key){const lang=(this.displayLocale||'en').toLowerCase().split(/[-_]/)[0],base=(LEDGER_GAP_COPY[lang]||LEDGER_GAP_COPY.en)[key];return base??(LEDGER_GAP_EXTRA[lang]||LEDGER_GAP_EXTRA.en)[key];}
  savedRefreshCopy(){const lang=(this.displayLocale||'en').toLowerCase().split(/[-_]/)[0];return ({en:'Saved. Refresh history to see the update.',nl:'Opgeslagen. Vernieuw de historiek om de wijziging te zien.',fr:'Enregistré. Actualisez l’historique pour voir la modification.',de:'Gespeichert. Aktualisieren Sie den Verlauf, um die Änderung zu sehen.',nb:'Lagret. Oppdater historikken for å se endringen.',sv:'Sparat. Uppdatera historiken för att se ändringen.',da:'Gemt. Opdater historikken for at se ændringen.',cs:'Uloženo. Aktualizujte historii, abyste viděli změnu.',el:'Αποθηκεύτηκε. Ανανεώστε το ιστορικό για να δείτε την αλλαγή.',hu:'Mentve. Frissítse az előzményeket a módosítás megtekintéséhez.',lb:'Gespäichert. Erfrëscht d’Historik fir d’Ännerung ze gesinn.',pl:'Zapisano. Odśwież historię, aby zobaczyć zmianę.',pt:'Guardado. Atualize o histórico para ver a alteração.',ro:'Salvat. Reîmprospătați istoricul pentru a vedea modificarea.'})[lang]||'Saved. Refresh history to see the update.';}
  tripCopy(){const lang=(this.displayLocale||'en').toLowerCase().split(/[-_]/)[0];return (LEDGER_TRIP_COPY[lang]||LEDGER_TRIP_COPY.en);}
  gapIntervals(){const rows=this.snapshot?.unaccounted_intervals||[],period=this.snapshot?.selected_period;if(!Number.isFinite(period?.start)||!Number.isFinite(period?.end))return rows;return rows.filter(g=>Number.isFinite(g.end)&&g.end>=period.start&&g.end<period.end&&g.end<=period.effective_end);}
  gapsForTrip(trip,allHistory=false){const segments=trip?.segments||[],rows=allHistory?(this.fullSnapshot?.unaccounted_intervals||this.snapshot?.unaccounted_intervals||[]):this.gapIntervals();return rows.filter(g=>g.trip_id===trip?.id||segments.some(s=>s.gap_id===g.id||s.gap_fingerprint===g.fingerprint));}
  gapStatusText(status){return this.gapCopy(({open:'open',ignored:'ignored',manual:'manual',stale:'stale'})[status]||'open');}
  gapEntry(g){
    const status=['open','ignored','manual','stale'].includes(g.resolution)?g.resolution:'open',identity=`data-gap-ident="${this.esc(g.id)}" data-gap-fingerprint="${this.esc(g.fingerprint)}"`;
    const time=Number.isFinite(g.start)&&Number.isFinite(g.end)?`${this.date(g.start)} → ${this.date(g.end)}`:'';
    const observed=`${this.gapCopy('observed')}: ${this.n(g.km,1)} km · ${this.gapCopy('battery')}: ${this.n(g.battery_change_kwh,2)} kWh`;
    let detail='';
    if(status==='manual')detail=`<p class="muted">${this.gapCopy('energy')}: ${this.n(g.energy_kwh,2)} kWh${g.cost==null?'':` · ${this.gapCopy('cost')}: ${this.money(g.cost,this.currencyCode(g.currency||this.snapshot.currency||'EUR'))}`}</p><button type="button" class="text" ${identity} data-gap-status="open">${this.gapCopy('undo')}</button>`;
    else if(status==='ignored')detail=`<button type="button" class="text" ${identity} data-gap-status="open">${this.gapCopy('undo')}</button>`;
    else if(status==='stale')detail=`<p class="muted">${this.gapCopy('staleHelp')}</p><button type="button" class="text" ${identity} data-gap-status="open">${this.gapCopy('undo')}</button><button type="button" class="text" data-action="refresh">${this.translate('Vernieuwen')}</button>`;
    else{
      const currency=this.currencyCode(g.currency||this.snapshot.currency||'EUR'),options=this.currencyChoices(g.currency);
      detail=`<details class="gap-details"><summary>${this.gapCopy('complete')}</summary><form class="gap-form" ${identity} data-currency="${currency}"><label>${this.gapCopy('energy')} (kWh)<input name="energy_kwh" type="number" min="0" step="0.01" inputmode="decimal" required></label><label>${this.gapCopy('cost')}<input name="cost" type="number" step="0.01" inputmode="decimal"></label><label>${this.gapCopy('currency')}<select name="currency">${options.map(code=>`<option value="${code}" ${currency===code?'selected':''}>${code}</option>`).join('')}</select></label><p class="muted">${this.gapCopy('usageHelp')}</p><p class="muted">${this.gapCopy('noConvert')}</p><p class="form-saved muted" role="status"></p><p class="form-error" role="alert"></p><button type="submit" class="save">${this.gapCopy('save')}</button></form></details><button type="button" class="text" ${identity} data-gap-status="ignored">${this.gapCopy('ignore')}</button>`;
    }
    return `<article class="panel gap-entry"><div class="row"><strong>${this.gapStatusText(status)}</strong><span class="muted">${this.esc(time)}</span></div><p class="muted">${observed}</p>${detail}</article>`;
  }
  unaccountedUsage(stat){
    const intervals=this.gapIntervals();if(!intervals.length)return '';
    const summary=this.snapshot.statistics?.selected||stat,unresolved=intervals.filter(g=>g.resolution!=='manual'),distance=summary?.unaccounted_distance_km??null,battery=summary?.unaccounted_battery_change_kwh??null,count=summary?.unaccounted_intervals??unresolved.length;
    return `<section class="unaccounted-usage"><h3>${this.gapCopy('title')} <small>${this.n(count,0)}</small></h3><div class="metrics two"><div class="metric"><span>${this.gapCopy('distance')}</span><strong>${this.n(distance)}<small>${this.distanceUnit()}</small></strong></div><div class="metric"><span>${this.gapCopy('battery')}</span><strong>${this.n(battery,2)}<small>kWh</small></strong></div></div>${intervals.map(g=>this.gapEntry(g)).join('')}</section>`;
  }
  distanceUnit(){return 'km';}
  async submitGap(e){
    const form=e.target.closest?.('form.gap-form');if(!form)return;e.preventDefault();const energy=form.elements.energy_kwh.value,cost=form.elements.cost.value,currency=this.currencyCode(form.elements.currency.value);
    try{const result=await this.update('resolve_gap',{ident:form.dataset.gapIdent,fingerprint:form.dataset.gapFingerprint,status:'manual',energy_kwh:Number(energy),cost:cost===''?null:Number(cost),currency});if(result?.saved){for(const control of form.querySelectorAll('input,select,button'))control.disabled=true;const status=form.querySelector('.form-saved');if(status)status.textContent=result.refreshed===false?this.savedRefreshCopy():this.gapCopy('manual');const ignore=form.parentElement?.querySelector('button[data-gap-status="ignored"]');if(ignore)ignore.disabled=true;}}
    catch(error){const message=form.querySelector('.form-error');if(message)message.textContent=this.translate(this.localizeError(error));}
  }
  change(e){const select=e.target.closest?.('form.gap-form select[name="currency"]');if(!select)return;const form=select.closest('form.gap-form');if(form.dataset.currency&&form.dataset.currency!==select.value)form.elements.cost.value='';form.dataset.currency=select.value;}
  async setGapResolution(button){
    const dialog=button.closest?.('dialog'),target=button.closest?.('.gap-entry')||dialog;
    let errorNode=target?.querySelector('.gap-action-error');
    if(errorNode)errorNode.textContent='';
    button.disabled=true;
    try{await this.update('resolve_gap',{ident:button.dataset.gapIdent,fingerprint:button.dataset.gapFingerprint,status:button.dataset.gapStatus});dialog?.close();}
    catch(error){button.disabled=false;if(target){if(!errorNode){errorNode=document.createElement('p');errorNode.className='gap-action-error form-error';errorNode.setAttribute('role','alert');target.append(errorNode);}errorNode.textContent=this.localizeError(error);}else{this.error=this.localizeError(error);this.render();}}
  }
  currencyChoices(...currencies){const fallback=['EUR','USD','GBP','DKK','SEK','NOK','CHF','PLN','CZK','HUF','RON','BGN','ISK','AUD','CAD','JPY','CNY'];let supported=[];try{supported=Intl.supportedValuesOf?.('currency')||[];}catch{}return [...new Set([...supported,...fallback,this.accountingCurrency(),this.snapshot?.preferences?.currency,...(this.snapshot?.charges||[]).map(c=>c.currency),...currencies].filter(Boolean).map(c=>this.currencyCode(c)))].sort((a,b)=>a==='EUR'?-1:b==='EUR'?1:a.localeCompare(b));}
  date(t,opts){return new Date(t*1000).toLocaleString(this.displayLocale,opts||{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});}
  value(label,v,unit='',d=1){return `<div class="metric"><span>${label}</span><strong>${this.n(v,d)}${unit?`<small>${unit}</small>`:''}</strong></div>`;}
  category(c){return {home:'Thuis',work:'Werk',supercharger:'Snellader',other:'Onderweg'}[c]||'Onderweg';}
  knownDriving(rows,limit=Infinity){
    const seen=new Set(),result=[];let remaining=limit;
    for(const row of [...(rows||[])].sort((a,b)=>b.end-a.end||b.start-a.start)){
      if(row.complete===false||(row.invalid_reason&&!row.native_correction_resolved&&!row.manual_gap_reconciled)||!Number.isFinite(row.km)||row.km<=0||!Number.isFinite(row.kwh)||row.kwh<0||!Number.isFinite(row.start)||!Number.isFinite(row.end)||row.end<row.start)continue;
      const key=`${row.start}|${row.end}|${row.km}`;if(seen.has(key))continue;seen.add(key);
      if(remaining<=0)break;const km=Math.min(row.km,remaining),scale=km/row.km;
      result.push({...row,km,kwh:row.kwh*scale,cost_eur:Number.isFinite(row.cost_eur)?row.cost_eur*scale:null});remaining-=km;
    }
    return result.reverse();
  }
  drivingStats(rows,capacity=this.snapshot?.settings?.capacity_kwh){
    const known=this.knownDriving(rows),km=known.reduce((sum,s)=>sum+s.km,0),energy=known.length?known.reduce((sum,s)=>sum+s.kwh,0):null;
    const priced=known.filter(s=>Number.isFinite(s.cost_eur)),pricedKm=priced.reduce((sum,s)=>sum+s.km,0),cost=priced.length?priced.reduce((sum,s)=>sum+s.cost_eur,0):null;
    return {used_kwh:energy,consumption_distance_km:km,consumption_kwh_100km:km>0?energy/km*100:null,driving_cost_eur:cost,cost_distance_km:pricedKm,cost_eur_100km:pricedKm>0?cost/pricedKm*100:null,soc_used_pct:energy!=null&&capacity>0?energy/capacity*100:null};
  }
  tripEnergy(t){return this.drivingStats(t.segments).used_kwh;}
  tripAverage(t){return this.drivingStats(t.segments).consumption_kwh_100km;}
  prepareSnapshot(raw){
    const data=JSON.parse(JSON.stringify(raw)),cap=data.settings.capacity_kwh;
    const rangeStat=Object.values(raw.statistics).find(s=>s.projected_range_km!=null&&s.consumption_kwh_100km>0);
    const remainingEnergy=Number.isFinite(raw.statistics.last_100km?.remaining_kwh)?raw.statistics.last_100km.remaining_kwh:rangeStat?rangeStat.projected_range_km*rangeStat.consumption_kwh_100km/100:null;
    const chargedBetween=(a,b)=>data.charges.some(c=>c.kind!=='dismissed'&&c.start<b&&c.end>a);
    const trips=data.trips.sort((a,b)=>a.start-b.start);
    for(const trip of trips)trip.source_ids=[trip.id];
    const costs=new Map((data.driving_segments||Object.values(data.statistics).flatMap(s=>s.segments||[])).map(s=>[`${s.start}/${s.end}`,s]));
    const recalculate=stat=>{
      stat.distance_km=stat.segments.reduce((sum,s)=>sum+s.km,0);
      Object.assign(stat,this.drivingStats(stat.segments,cap));
      stat.cost_complete=stat.segments.length>0&&stat.cost_distance_km===stat.distance_km;
      stat.projected_range_km=remainingEnergy!=null&&stat.consumption_kwh_100km>0?remainingEnergy/stat.consumption_kwh_100km*100:null;
      const petrol=data.preferences.petrol_l_100km,price=data.preferences.petrol_eur_l;
      const priceCurrency=this.currencyCode(data.preferences.currency||'EUR'),accountingCurrency=this.currencyCode(data.currency||'EUR');
      stat.petrol_comparison_eur=priceCurrency===accountingCurrency&&petrol!=null&&price!=null?stat.distance_km/100*petrol*price:null;
      stat.petrol_saving_eur=stat.cost_complete&&stat.petrol_comparison_eur!=null&&stat.driving_cost_eur!=null?stat.petrol_comparison_eur-stat.driving_cost_eur:null;
      return stat;
    };
    for(const stat of Object.values(data.statistics))recalculate(stat);
    for(const counter of data.counters)recalculate(counter.statistics);
    if(data.statistics.last_100km){
      const native=trips.filter(t=>t.native_alignment_version>=1||['native_source_replay','native_soc'].includes(t.source)).flatMap(t=>t.segments.filter(s=>!s.manual_gap_reconciled).map(s=>({...s,cost_eur:costs.get(`${s.start}/${s.end}`)?.cost_eur??null})));
      const rolling=data.statistics.last_100km;
      rolling.segments=this.knownDriving(native,100);
      recalculate(rolling);
    }
    const groups=[];let pending=null;
    for(const trip of trips){
      if(pending&&pending.distance_km<5&&!chargedBetween(pending.end,trip.start)&&pending.end_odo===trip.start_odo){
        pending.end=trip.end;pending.end_odo=trip.end_odo;pending.end_energy=trip.end_energy;
        pending.distance_km+=trip.distance_km;pending.segments.push(...trip.segments);
        pending.source_ids.push(trip.id);pending.complete&&=trip.complete;
      }else{pending=trip;groups.push(pending);}
    }
    const active=groups.find(t=>t.source_ids.includes(data.active_trip_id));
    if(active)data.active_trip_id=active.id;
    const last=[...groups].reverse().find(t=>t.id!==data.active_trip_id&&(t.distance_km>=5||chargedBetween(t.end,Date.now()/1000)));
    const tripStat=t=>{
      const stat=JSON.parse(JSON.stringify(raw.statistics.last_trip));
      stat.segments=t.segments.map(s=>({...s,cost_eur:costs.get(`${s.start}/${s.end}`)?.cost_eur??null}));
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
    const needs=!c.ongoing&&(c.cost_eur==null||!c.confirmed);
    const currency=this.currencyCode(c.currency||'EUR');
    const time=c.ongoing?`${this.date(c.start)} · Lopende sessie`:`${this.date(c.start)} → ${this.endDate(c)}`;
    return `<button class="session ${c.ongoing?'active':''}" data-charge="${this.esc(c.id)}"><div class="row session-head"><span>${time}</span><span class="place">${c.kind==='candidate'?'Lading controleren':this.category(c.category)}${needs?' <span class="receipt" aria-label="Prijs aanvullen">＋</span>':''}</span></div><div class="metrics three">${this.value('Geladen',c.kwh,'kWh',2)}${this.value('Laadkosten',c.cost_eur,this.moneyUnit(currency),2)}${this.value(c.category==='home'?'Laadvoordeel':'Tarief',c.category==='home'?c.benefit_eur:(c.cost_eur!=null&&c.kwh?c.cost_eur/c.kwh:null),c.category==='home'?this.moneyUnit(currency):this.moneyRateUnit(currency),2)}</div><div class="muted">${c.category==='home'?`${c.reimbursement_eur==null?'':`Vergoeding ${this.money(c.reimbursement_eur,currency,2)}`}${c.solar_pct==null?'':` · ${this.n(c.solar_pct,0)}% zon`}`:c.energy_basis==='range_estimate'?this.translate('Berekende energie'):''}${c.cost_currency_conflict?` · ${this.currencyNotice('conflict')}`:''}</div></button>`;
  }
  tripCard(t){
    const gaps=this.gapsForTrip(t),energy=this.tripEnergy(t),average=this.tripAverage(t),gapLabel=gaps.length?this.gapStatusText(gaps.some(g=>g.resolution==='stale')?'stale':gaps.some(g=>g.resolution==='ignored')?'ignored':gaps.some(g=>g.resolution==='manual')?'manual':'open'):'';
    const cap=this.snapshot.settings.capacity_kwh;
    return `<button class="session ${this.snapshot.active_trip_id===t.id?'active':''}" data-trip="${this.esc(t.id)}"><div class="row session-head"><span>${this.date(t.start)} → ${this.date(t.end,{hour:'2-digit',minute:'2-digit'})}</span>${this.snapshot.active_trip_id===t.id?'<span class="place">Rit bezig</span>':''}${gapLabel?`<span class="place gap-status">${this.esc(gapLabel)}</span>`:''}</div><div class="metrics three">${this.value('Afstand',t.distance_km,'km')}${this.value('Gem. verbruik',average,'kWh/100 km')}${this.value('Batterij gebruikt',energy!=null?energy/cap*100:null,'%')}</div><div class="muted">${this.n(t.start_energy/cap*100,0)}% → ${this.n(t.end_energy/cap*100,0)}%${energy==null?(gaps.length?` · ${this.esc(gapLabel)}`:' · Meting ontbreekt'):` · ${this.n(energy,2)} kWh`}</div></button>`;
  }
  history(){
    const charging=this.tab==='charging', all=charging?this.snapshot.charges:this.snapshot.trips;
    const rows=all.slice(0,this.full?this.pageSize:3);
    let html=`<div class="row heading"><h2>${this.full?(charging?'Alle laadsessies':'Alle ritten'):(charging?'Laatste laadsessies':'Laatste ritten')}</h2>${charging?'<button class="icon" data-action="add" title="Laadsessie toevoegen" aria-label="Laadsessie toevoegen">＋</button>':''}</div>`;
    if(!rows.length)html+=`<div class="empty">${charging?'Nog geen laadsessies':'De eerste rit verschijnt zodra de auto nieuwe metingen doorgeeft.'}</div>`;
    let month='';
    for(const item of rows){
      const key=this.monthKey(charging?item.start:item.end);
      if(this.full&&month!==key){month=key;const group=all.filter(r=>this.monthKey(charging?r.start:r.end)===key);let summaryNotice='';
        const label=this.date(charging?item.start:item.end,{month:'long',year:'numeric'});
        let totals='';
        if(charging){const sum=k=>group.every(c=>c[k]!=null&&c.confirmed)?group.reduce((s,c)=>s+c[k],0):null;
          const currencies=new Set(group.filter(c=>c.cost_eur!=null).map(c=>this.currencyCode(c.currency||'EUR'))),currency=currencies.size===1?[...currencies][0]:this.accountingCurrency(),knownTotal=currencies.size<=1?sum('cost_eur'):null;
          const home=group.filter(c=>c.category==='home'),homeCurrencies=new Set(home.map(c=>this.currencyCode(c.currency||'EUR'))),homeCurrency=homeCurrencies.size===1?[...homeCurrencies][0]:currency;
          totals=`${this.n(group.filter(c=>c.confirmed).reduce((s,c)=>s+c.kwh,0),2)} kWh · ${this.money(knownTotal,currency)} laadkosten${home.length?` · ${this.money(homeCurrencies.size>1?null:home.every(c=>c.reimbursement_eur!=null)?home.reduce((s,c)=>s+c.reimbursement_eur,0):null,homeCurrency)} vergoeding · ${this.money(homeCurrencies.size>1?null:home.every(c=>c.benefit_eur!=null)?home.reduce((s,c)=>s+c.benefit_eur,0):null,homeCurrency)} laadvoordeel`:''}`;
          if(currencies.size>1||homeCurrencies.size>1)summaryNotice=`<p class="notice currency-notice">${this.currencyNotice('mixed')}</p>`;
        }else{const km=group.reduce((s,t)=>s+t.distance_km,0),consumption=this.drivingStats(group.flatMap(t=>t.segments)).consumption_kwh_100km;totals=`${this.n(km)} km · ${this.n(consumption)} kWh/100 km · ${group.length} ritten`;}
        html+=`<div class="month"><h3>${label}</h3><p>${totals}</p>${summaryNotice}</div>`;
      }
      html+=charging?this.chargeCard(item):this.tripCard(item);
    }
    if(this.full&&all.length>this.pageSize)html+=`<button class="more" data-action="more">Meer tonen (${all.length-this.pageSize})</button>`;
    html+=`<button class="more" data-action="full">${this.full?'Terug naar de laatste drie':charging?'Alle laadsessies':'Alle ritten'} <span>›</span></button>`;
    return html;
  }
  missingNoticeText(stat){
    if(!stat.missing_prices&&!stat.unconfirmed_charges)return '';
    const missing=Number(stat.missing_prices)||0,unconfirmed=Number(stat.unconfirmed_charges)||0;
    const prefix=missing?`Ontbrekende prijzen: ${missing}`:'';
    const pending=unconfirmed?`Niet-bevestigde sessies: ${unconfirmed}`:'';
    const mixed=Number(stat.currency_mismatch_count)>0;
    return `${prefix}${prefix&&pending?' · ':''}${pending} · Bekende kosten: ${this.money(mixed?null:stat.known_spend_eur,this.currencyCode(stat.currency||this.snapshot?.currency||'EUR'))}${mixed?` · ${this.currencyNotice('mixed')}`:''}`;
  }
  graph(segments,mean){
    if(!segments.length)return '';
    const seen=new Set(),unique=segments.filter(r=>{const key=`${r.start}|${r.end}|${r.km}`;if(seen.has(key))return false;seen.add(key);return Number.isFinite(r.km)&&r.km>0;});
    const good=this.knownDriving(unique);if(!good.length)return '';
    const max=Math.max(1,mean||0,...good.map(s=>s.kwh/s.km*100))*1.2;
    const distance=unique.reduce((s,r)=>s+r.km,0);let x=0;
    const valid=new Set(good.map(r=>`${r.start}|${r.end}|${r.km}`));
    const bars=unique.map(r=>{const width=r.km/distance*300;const left=x;x+=width;if(!valid.has(`${r.start}|${r.end}|${r.km}`))return '';const value=r.kwh/r.km*100;return `<rect x="${left}" y="${100-value/max*85}" width="${Math.max(.5,width-1)}" height="${value/max*85}" rx="2"><title>${this.n(r.km)} km · ${this.n(value)} kWh/100 km</title></rect>`;}).join('');
    return `<div class="chart"><svg viewBox="0 0 300 110" role="img" aria-label="Verbruik per gemeten rijsegment"><g fill="var(--car-accent)">${bars}</g>${mean!=null?`<path d="M0 ${100-mean/max*85} H300" class="mean"/>`:''}</svg><div class="row muted"><span>0 km</span><span>Gem. ${this.n(mean)} kWh/100 km</span><span>${this.n(distance,0)} km</span></div></div>`;
  }
  chartDate(date){return new Date(`${date}T12:00:00Z`).toLocaleDateString(this.displayLocale,{day:'numeric',month:'short',timeZone:'UTC'});}
  chargingGraph(){
    let rows=this.snapshot.charging_daily;
    const now=new Date();rows=rows.filter(r=>this.period==='day'?r.date===this.localISO(now):this.period==='year'?r.date.startsWith(String(now.getFullYear())):r.date.startsWith(this.localISO(now).slice(0,7)));
    if(!rows.length)return '';
    const cost=this.graphUnit==='eur',currency=this.currencyCode(this.snapshot.currency||'EUR'),mismatch=Number(this.snapshot.statistics?.[this.period]?.currency_mismatch_count)>0,max=Math.max(1,...rows.map(r=>cost?r.known_cost_eur:r.kwh));
    const bars=rows.map((r,i)=>{const w=300/rows.length,v=cost?(mismatch||Number(r.currency_mismatch_count)>0?null:r.known_cost_eur):r.kwh;return `<rect x="${i*w}" y="${95-(v||0)/max*80}" width="${Math.max(1,w-3)}" height="${(v||0)/max*80}" rx="2" opacity="${cost&&r.missing?.4:.9}"><title>${this.chartDate(r.date)}: ${cost?this.money(v,currency):`${this.n(v,2)} kWh`}${r.missing?` · ${this.translate('prijs ontbreekt')}`:''}</title></rect>`;}).join('');
    return `<div class="panel"><div class="row"><h3>${this.translate('Laden')}</h3><div class="segmented compact"><button data-unit="kwh" class="${cost?'':'selected'}">kWh</button><button data-unit="eur" class="${cost?'selected':''}">${this.esc(this.moneyUnit(currency))}</button></div></div>${cost&&mismatch?`<p class="muted">${this.currencyNotice('mixed')}</p>`:''}<div class="chart"><svg viewBox="0 0 300 100" role="img" aria-label="${this.esc(this.translate('Laadenergie per dag'))}"><g fill="var(--car-accent)">${bars}</g></svg><div class="row muted"><span>${this.esc(this.chartDate(rows[0].date))}</span><span>${this.esc(this.chartDate(rows.at(-1).date))}</span></div></div></div>`;
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
    const statCurrency=this.currencyCode(stat.currency||this.snapshot.currency||'EUR'),mixed=Number(stat.currency_mismatch_count)>0;
    html+=`<div class="panel"><div class="metrics ${stat.cost_eur_100km!=null?'two':''} hero">${this.value('Gemiddeld verbruik',stat.consumption_kwh_100km,'kWh/100 km')}${stat.cost_eur_100km!=null?this.value('Rijkosten',stat.cost_eur_100km,`${this.moneyUnit(statCurrency)}/100 km`,2):''}</div><div class="metrics three secondary">${this.value('Afstand',stat.distance_km,'km')}${this.value('Gebruikt',stat.used_kwh,'kWh')}${this.value('Batterij',stat.soc_used_pct,'%')}</div>${mixed?`<p class="muted">${this.currencyNotice('mixed')}</p>`:''}${!stat.distance_km?'<p class="muted">Verbruik wordt zichtbaar na de eerste gemeten rit.</p>':''}</div>`;
    if(this.period!=='last_100km')html+=this.unaccountedUsage(stat);
    if(!['last_100km','last_trip','current_trip'].includes(this.period))html+=this.parkedSummary(stat);
        html+=`<div class="panel"><h3>Laadkosten</h3><div class="metrics three">${this.value('Totaal',mixed?null:stat.spend_eur,this.moneyUnit(statCurrency),2)}${this.value('Geladen',stat.charged_kwh,'kWh')}${this.value('Gem. tarief',mixed?null:stat.price_eur_kwh,this.moneyRateUnit(statCurrency),2)}</div><div class="metrics two secondary">${this.value('Gem. verbruik',stat.consumption_kwh_100km,'kWh/100 km')}${this.value('Rijkosten',stat.cost_eur_100km,`${this.moneyUnit(statCurrency)}/100 km`,2)}</div>${mixed?`<p class="muted">${this.currencyNotice('mixed')}</p>`:''}${stat.missing_prices||stat.unconfirmed_charges?`<button class="notice" data-action="missing">${this.missingNoticeText(stat)} <span>›</span></button>`:''}<div class="categories">${Object.entries(stat.categories).map(([k,r])=>`<div class="row"><span>${this.category(k)}</span><span>${this.n(r.kwh)} kWh · ${this.money(mixed||Number(r.currency_mismatch_count)>0?null:r.cost_eur,this.currencyCode(r.currency||statCurrency))}</span></div>`).join('')}</div></div>`;
    if(stat.segments.length||['day','month','year'].includes(this.period))html+=`<details class="details"><summary>Grafieken & actieradius</summary>${this.graph(stat.segments,stat.consumption_kwh_100km)}${stat.projected_range_km!=null?`<div class="row range"><span>Actieradius bij dit verbruik</span><strong>${this.n(stat.projected_range_km,0)} km</strong></div>`:''}${['day','month','year'].includes(this.period)?this.chargingGraph():''}</details>`;
    const rated=this.snapshot.preferences.rated_kwh_100km;
    if(rated>0&&stat.consumption_kwh_100km!=null)html+=`<div class="panel row"><span>Verbruik t.o.v. referentie<br><small>${this.n(rated)} kWh/100 km</small></span><strong>${this.n((stat.consumption_kwh_100km/rated-1)*100,0)}%</strong></div>`;
    if(stat.petrol_comparison_eur!=null)html+=`<div class="panel"><h3>Vergelijking benzine</h3><div class="metrics two">${this.value('Benzine voor deze afstand',stat.petrol_comparison_eur,this.moneyUnit(this.currencyCode(this.snapshot.preferences.currency||'EUR')),2)}${this.value('Besparing',mixed?null:stat.petrol_saving_eur,this.moneyUnit(statCurrency),2)}</div></div>`;
    html+=`<details class="details"><summary>Rittellers & instellingen</summary>${this.snapshot.counters.map(c=>{const s=c.statistics,unit=this.currencyCode(s.currency||this.snapshot.currency||'EUR'),mixed=Number(s.currency_mismatch_count)>0;return `<div class="counter"><div class="row"><strong><span data-user-content translate="no">${this.esc(c.name)}</span></strong><button class="text" data-reset="${c.id}">Reset</button></div><div class="metrics three">${this.value('Afstand',s.distance_km,'km')}${this.value('Verbruik',s.consumption_kwh_100km,'kWh/100 km')}${this.value('Kosten',mixed?null:s.cost_eur_100km,`${this.moneyUnit(unit)}/100 km`,2)}</div>${mixed?`<p class="muted">${this.currencyNotice('mixed')}</p>`:''}</div>`;}).join('')}<button class="more" data-action="counter">＋ ${this.translate('Nieuwe ritteller')}</button><button class="more" data-action="settings">${this.translate('Rekeninstellingen')} ›</button><p class="muted">Verbruik: ${this.snapshot.settings.capacity_kwh} kWh × verschil in berekende SoC. Rijkosten gebruiken de gemiddelde prijs van de energie in de batterij. Thuis telt de EVCC-waarde mee, inclusief misgelopen teruglevering. Laadverliezen zijn niet afzonderlijk gemeten.</p>${this.snapshot.source_status!=='fresh'?'<p class="muted">Wacht op een nieuwe meting van de auto; bewaarde waarden maken geen nieuwe rit.</p>':''}</details>`;
    return `<div class="insight">${html}</div>`;
  }
  parkedHistory(){
    const all=this.snapshot.parked_periods||[],rows=all.slice(0,this.full?this.pageSize:3);
    let html=`<div class="row heading"><h2>${this.full?'Alle stilstandperiodes':'Laatste stilstandperiodes'}</h2></div>`;
    if(!rows.length)html+='<div class="empty">Nog geen geregistreerde bereikafname bij stilstand.</div>';
    const total=group=>{const energy=group.reduce((sum,p)=>sum+p.kwh,0);return `${this.n(energy,2)} kWh · ${this.n(this.parkedEquivalent(energy),this.parkedEquivalentPrecision(energy))}×`;};
    let month='';
    for(const p of rows){
      const key=this.monthKey(p.end);
      if(this.full&&month!==key){month=key;html+=`<div class="month parked-month"><h3>${this.date(p.end,{month:'long',year:'numeric'})}</h3><p>${total(all.filter(r=>this.monthKey(r.end)===key))}</p></div>`;}
      html+=`<button class="session" data-parked="${this.esc(p.id)}"><div class="row session-head"><span>${this.date(p.start)} → ${this.date(p.end)}</span></div><div class="metrics three">${this.value('Duur',(p.end-p.start)/60,'min',0)}${this.value(this.parkedEnergyLabel(),p.kwh,'kWh',2)}${this.value(this.parkedEquivalentLabel(),this.parkedEquivalent(p.kwh),'×',this.parkedEquivalentPrecision(p.kwh))}</div><div class="muted">Geschat uit batterijafname</div></button>`;
    }
    if(this.full&&all.length>this.pageSize)html+=`<button class="more" data-action="more">Meer tonen (${all.length-this.pageSize})</button>`;
    html+=`<button class="more" data-action="full">${this.full?'Terug naar de laatste drie':'Alle stilstandperiodes'} <span>›</span></button>`;
    if(!this.full&&all.length){const key=this.monthKey(all[0].end);html+=`<div class="month parked-month"><h3>${this.date(all[0].end,{month:'long',year:'numeric'})}</h3><p>${total(all.filter(p=>this.monthKey(p.end)===key))}</p></div>`;}
    return html;
  }
  parkedEnergyLabel(){return 'Verbruikt';}
  parkedEquivalentLabel(){return 'Batterijequivalent';}
  parkedEquivalent(kwh){return kwh/this.snapshot.settings.capacity_kwh;}
  parkedEquivalentPrecision(kwh){const equivalent=Math.abs(this.parkedEquivalent(kwh));return equivalent>0&&equivalent<0.01?Math.min(6,Math.max(3,Math.ceil(-Math.log10(equivalent)))):2;}
  parkedSummary(stat){const kwh=stat.parked_loss_estimate_kwh;return `<button class="parked-summary row" data-tab="parked"><span>Stilstand</span><strong>${this.n(kwh,2)} kWh · ${this.parkedEquivalentLabel()} ${this.n(this.parkedEquivalent(kwh),this.parkedEquivalentPrecision(kwh))}×</strong><span aria-hidden="true">›</span></button>`;}
  render(){
    if(!this.config)return;
    this.shadowRoot.innerHTML=`<style>${CarLedgerCard.styles}</style><ha-card><div class="row top"><nav class="segmented main-tabs" aria-label="Autohistoriek">${[['charging','Laden'],['trips','Ritten'],['insight','Verbruik'],['parked','Stilstand']].map(([key,label])=>`<button data-tab="${key}" aria-pressed="${this.tab===key}" class="${this.tab===key?'selected':''}">${label}</button>`).join('')}</nav><button class="icon refresh" data-action="refresh" title="Vernieuwen" aria-label="Vernieuwen"><svg viewBox="0 0 24 24"><path d="M20 7v5h-5M20 12a8 8 0 1 0-2.4 5.7"/></svg></button></div><div class="error" role="status">${this.esc(this.error)}</div>${this.snapshot?(this.tab==='insight'?this.insight():this.tab==='parked'?this.parkedHistory():this.history()):'<div class="empty">Ritten en laadkosten laden…</div>'}</ha-card>`;
    this.localize();
    this.shadowRoot.addEventListener('click',this._clickHandler ||= e=>this.click(e));
    this.shadowRoot.addEventListener('submit',this._submitHandler ||= e=>this.submitGap(e));
    this.shadowRoot.addEventListener('change',this._changeHandler ||= e=>this.change(e));
    this.refreshState();
  }
  async click(e){
    const b=e.target.closest('button');if(!b)return;
    if(b.dataset.gapStatus){await this.setGapResolution(b);return;}
    if(b.dataset.tab){this.tab=b.dataset.tab;this.full=false;this.pageSize=36;this.render();await this.refresh();return;}
    if(b.dataset.period){this.period=b.dataset.period;this.render();return;}
    if(b.dataset.unit){this.graphUnit=b.dataset.unit;this.render();return;}
    if(b.dataset.charge){const charge=this.snapshot.charges.find(c=>c.id===b.dataset.charge);if(charge?.ongoing)return;this.chargeDialog(charge);return;}
    if(b.dataset.trip){this.tripDialog(this.snapshot.trips.find(t=>t.id===b.dataset.trip));return;}
    if(b.dataset.parked){const p=this.snapshot.parked_periods.find(r=>r.id===b.dataset.parked);this.parkedDialog(p);return;}
    if(b.dataset.reset){const c=this.snapshot.counters.find(c=>c.id===b.dataset.reset);this.dialog('Ritteller opnieuw starten',`<p>${this.counterResetPrompt(c.name)}</p>`,async()=>this.update('counter',{ident:c.id,name:c.name}));return;}
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
  parkedDialog(p){this.dialog('Stilstand',`<p>${this.date(p.start)} → ${this.date(p.end)}</p><div class="metrics three">${this.value('Duur',(p.end-p.start)/60,'min',0)}${this.value(this.parkedEnergyLabel(),p.kwh,'kWh',2)}${this.value(this.parkedEquivalentLabel(),this.parkedEquivalent(p.kwh),'×',this.parkedEquivalentPrecision(p.kwh))}</div><p class="muted">Geschatte energieafname tussen metingen met dezelfde kilometerstand. Los van rijverbruik; oorzaken zijn niet gemeten.</p>`);}
  localISO(d){const local=new Date(d.getTime()-d.getTimezoneOffset()*60000);return local.toISOString().slice(0,10);}
  inputDate(t){const d=new Date(t*1000);return new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,16);}
  chargeDialog(c){
    const now=Date.now()/1000;const isNew=!c;
    const originalCurrency=this.currencyCode(c?(c.currency||'EUR'):(this.snapshot.currency||'EUR')),currencies=this.currencyChoices(c?.currency);
    const form=`${c?`<p class="muted">${this.date(c.start)} · ${this.n(c.kwh,2)} kWh${c.energy_basis==='range_estimate'?` · ${this.translate('Berekende energie')}`:''}</p>`:`<div class="form-two"><label>Start<input type="datetime-local" name="start" required value="${this.inputDate(now-1800)}"></label><label>Einde<input type="datetime-local" name="end" required value="${this.inputDate(now)}"></label></div>`}<label data-charge-price-label>${this.translate('Prijs per kWh')} (${this.moneyRateUnit(originalCurrency)})<input type="number" name="price" step="0.001" min="0" inputmode="decimal" placeholder="${this.moneyRateUnit(originalCurrency)}" value="${c?.price_eur_kwh??''}"></label><label>${this.currencyLabel()}<select name="currency">${currencies.map(code=>`<option value="${code}" ${code===originalCurrency?'selected':''}>${code}</option>`).join('')}</select></label><p class="muted currency-help">${this.currencyHelp()}</p><label>Locatie<select name="category">${(c?.kind==='home'?['home']:['other','supercharger','work']).map(k=>`<option value="${k}" ${(c?.category||'other')===k?'selected':''}>${this.category(k)}</option>`).join('')}</select></label><details ${isNew?'open':''}><summary>${this.translate('Bon & energie')}</summary><label>Geladen kWh<input type="number" name="kwh" step="0.01" min="0.01" inputmode="decimal" ${isNew?'required':''} value="${c?.kwh??''}"></label><label data-charge-receipt-label>${this.translate('Totaal op bon (optioneel)')} (${this.moneyUnit(originalCurrency)})<input type="number" name="receipt" step="0.01" min="0" inputmode="decimal" placeholder="${this.moneyUnit(originalCurrency)}"></label></details>${c?.cost_currency_conflict?`<p class="notice">${this.currencyNotice('conflict')}</p>`:''}${c?.kind==='candidate'?'<p class="muted">De auto meldde meer bereik. Bevestig alleen als dit een echte lading was.</p><button type="button" class="more" data-dismiss="true">Dit was geen lading</button>':''}`;
    this.dialog(isNew?'Laadsessie toevoegen':c.kind==='candidate'?'Lading bevestigen':'Laadprijs',form,async f=>{
      const selectedCurrency=this.currencyCode(f.get('currency')),values={category:f.get('category')};for(const key of ['price','receipt','kwh'])if(f.get(key)!==''&&f.get(key)!=null&&(key!=='kwh'||isNew||Number(f.get(key))!==c.kwh||f.get('receipt')!==''))values[key]=Number(f.get(key));
      if(selectedCurrency!==originalCurrency){if(values.price==null&&values.receipt==null)throw new Error('Enter the amount again in the selected currency.');values.currency=selectedCurrency;}
      if(values.price==null&&values.receipt==null&&!c?.confirmed)throw new Error('Vul de prijs per kWh of het bedrag op de bon in.');
      if(isNew){values.start=new Date(f.get('start')).getTime()/1000;values.end=new Date(f.get('end')).getTime()/1000;await this.update('add_charge',values);}
      else await this.update('edit_charge',{ident:c.id,...values});
    },c);
    const modal=this.shadowRoot.querySelector('dialog[open]'),select=modal?.querySelector('[name="currency"]');select?.addEventListener('change',()=>{const next=this.currencyCode(select.value);if(next===originalCurrency)return;for(const key of ['price','receipt']){const input=modal.querySelector(`[name="${key}"]`);if(input)input.value='';}const price=modal.querySelector('[name="price"]'),receipt=modal.querySelector('[name="receipt"]'),priceLabel=modal.querySelector('[data-charge-price-label]'),receiptLabel=modal.querySelector('[data-charge-receipt-label]');if(price)price.placeholder=this.moneyRateUnit(next);if(receipt)receipt.placeholder=this.moneyUnit(next);if(priceLabel)priceLabel.firstChild.textContent=`${this.translate('Prijs per kWh')} (${this.moneyRateUnit(next)})`;if(receiptLabel)receiptLabel.firstChild.textContent=`${this.translate('Totaal op bon (optioneel)')} (${this.moneyUnit(next)})`;});
  }
  tripDialog(t){
    const cap=this.snapshot.settings.capacity_kwh,gaps=this.gapsForTrip(t,true),energy=this.tripEnergy(t),copy=this.tripCopy();
    const fill=(text)=>text.replace('{start}',this.n(t.start_odo,0)).replace('{end}',this.n(t.end_odo,0)).replace('{capacity}',this.n(cap,0));
    let explanation=`${fill(copy.odometer)} ${gaps.length?copy.gap:fill(copy.measured)}`;
    if(energy==null&&!gaps.length)explanation+=copy.missing;
    explanation+=` ${copy.parked}`;
    this.dialog('Ritdetails',`<p>${this.date(t.start)} → ${this.date(t.end)}</p><div class="metrics two">${this.value('Afstand',t.distance_km,'km')}${this.value('Energie gebruikt',energy,'kWh',2)}${this.value('Batterij bij vertrek',t.start_energy/cap*100,'%')}${this.value('Batterij bij aankomst',t.end_energy/cap*100,'%')}</div><p class="muted">${explanation}</p>${gaps.length?`<section class="gap-trip-details"><h3>${this.gapCopy('title')}</h3>${gaps.map(g=>this.gapEntry(g)).join('')}</section>`:''}`,null);
  }
  settingsDialog(){
    const p=this.snapshot.preferences;
    const currency=this.currencyCode(p.currency||'EUR'),currencyOptions=this.currencyChoices(p.currency),fields=[['opening_price_eur_kwh',this.translate(`Prijs energie bij start van registratie (€/kWh)`).replace('€/kWh',this.moneyRateUnit(currency))],['rated_kwh_100km','Referentieverbruik (kWh/100 km)'],['petrol_l_100km','Vorige auto (l/100 km)'],['petrol_eur_l',this.translate('Benzineprijs (€/l)').replace('€/l',`${this.moneyUnit(currency)}/l`)]];
    this.dialog('Rekeninstellingen',`<p class="muted">De prijs van de al aanwezige batterij is nodig om rijkosten vanaf de start te berekenen. Laat leeg als die onbekend is.</p><label>${this.currencyLabel()}<select name="currency">${currencyOptions.map(code=>`<option value="${code}" ${code===currency?'selected':''}>${code}</option>`).join('')}</select></label><p class="muted currency-help">${this.currencyHelp()}</p>${fields.map(([key,label])=>`<label data-money-pref="${key}">${label}<input type="number" name="${key}" min="0" step="0.001" value="${p[key]??''}" inputmode="decimal"></label>`).join('')}`,async f=>{const values={};for(const [key]of fields)values[key]=f.get(key)===''?null:Number(f.get(key));const selected=this.currencyCode(f.get('currency'));if(selected!==currency){values.currency=selected;values.opening_price_eur_kwh=f.get('opening_price_eur_kwh')===''?null:Number(f.get('opening_price_eur_kwh'));values.petrol_eur_l=f.get('petrol_eur_l')===''?null:Number(f.get('petrol_eur_l'));}await this.update('preferences',values);});
    const modal=this.shadowRoot.querySelector('dialog[open]'),select=modal?.querySelector('[name="currency"]');select?.addEventListener('change',()=>{if(this.currencyCode(select.value)===currency)return;for(const key of ['opening_price_eur_kwh','petrol_eur_l']){const input=modal.querySelector(`[name="${key}"]`);if(input)input.value='';}const opening=modal.querySelector('[data-money-pref="opening_price_eur_kwh"]'),petrol=modal.querySelector('[data-money-pref="petrol_eur_l"]');if(opening)opening.firstChild.textContent=this.translate('Prijs energie bij start van registratie (€/kWh)').replace('€/kWh',this.moneyRateUnit(select.value));if(petrol)petrol.firstChild.textContent=this.translate('Benzineprijs (€/l)').replace('€/l',`${this.moneyUnit(select.value)}/l`);});
  }
  dialog(title,content,save,c){
    const el=document.createElement('dialog'),wrapper=save?`<form data-dialog-save>`:'<div>';el.className='modal';el.innerHTML=`${wrapper}<div class="row"><h2>${this.esc(title)}</h2><button type="button" class="icon" data-close aria-label="Sluiten">×</button></div>${content}<p class="form-error" role="alert"></p>${save?'<button class="save" type="submit">Opslaan</button>':''}${save?'</form>':'</div>'}`;
    this.shadowRoot.append(el);el.addEventListener('close',()=>el.remove());el.querySelector('[data-close]').onclick=()=>el.close();
    this.localize(el);
    el.addEventListener('click',async e=>{if(e.target===el)el.close();if(e.target.closest('[data-dismiss]')){try{await this.update('dismiss_candidate',{ident:c.id});el.close();}catch(err){el.querySelector('.form-error').textContent=this.translate(this.localizeError(err));}}});
    const saveForm=el.querySelector('[data-dialog-save]');if(saveForm)saveForm.onsubmit=async e=>{e.preventDefault();const button=el.querySelector('.save');button.disabled=true;try{const result=await save(new FormData(e.target));if(result===false)return;el.close();}catch(err){el.querySelector('.form-error').textContent=this.translate(this.localizeError(err));button.disabled=false;}};el.showModal();return el;
  }
  async update(action,values){this.snapshot=this.prepareSnapshot(await this._hass.callWS({type:'nio_telematics/car_dashboard/update',entry_id:this.config.entry_id,action,values}));this.render();}
  static styles=`
    :host{--car-accent:#47776e;--car-surface:var(--card-background-color,#fff);--car-text:var(--primary-text-color,#18211f);--car-muted:var(--secondary-text-color,#777e7b);display:block;color:var(--car-text);font-family:var(--paper-font-body1_-_font-family,Arial,sans-serif)}
    *{box-sizing:border-box}ha-card{background:transparent;border:0;box-shadow:none;padding:4px 0 16px}button,input,select{font:inherit;color:inherit}button{cursor:pointer}button:focus-visible,summary:focus-visible{outline:2px solid var(--car-accent);outline-offset:3px}button:disabled{opacity:.45;cursor:wait}h2,h3,p{margin:0}h2{font-size:16px;font-weight:600}h3{font-size:14px;font-weight:600}.row{display:flex;align-items:center;justify-content:space-between;gap:12px}.top{gap:10px;margin-bottom:18px}.segmented{display:flex;background:rgba(128,128,128,.075);border-radius:13px;padding:4px;gap:3px;flex:1}.segmented button{flex:1;border:0;background:transparent;padding:10px 7px;border-radius:10px;font-size:14px;color:var(--car-muted)}.segmented button.selected{background:var(--car-surface);color:var(--car-text);box-shadow:0 1px 4px #0000000a;font-weight:600}.icon{background:transparent;border:0;width:34px;height:34px;padding:7px;font-size:22px;border-radius:50%;display:grid;place-items:center}.refresh svg{width:21px;height:21px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}.heading{margin:0 3px 11px}.session,.panel{width:100%;text-align:left;background:var(--car-surface);border:1px solid rgba(128,128,128,.18);border-radius:20px;padding:18px;margin:0 0 9px}.session-head{font-size:11px;margin-bottom:17px;color:var(--car-muted)}.place{white-space:nowrap;font-size:10px}.receipt{color:var(--car-accent);font-size:13px;margin-left:4px}.metrics{display:grid;gap:12px}.three{grid-template-columns:repeat(3,minmax(0,1fr))}.two{grid-template-columns:repeat(2,minmax(0,1fr))}.metric span{display:block;color:var(--car-muted);font-size:10px;margin-bottom:6px}.metric strong{font-size:21px;line-height:1.15;font-weight:500;letter-spacing:-.6px;white-space:nowrap}.metric small{font-size:11px;margin-left:4px;letter-spacing:0;font-weight:400}.muted{font-size:11px;color:var(--car-muted);line-height:1.5}.session>.muted{margin-top:14px;min-height:0}.session.active{background:color-mix(in srgb,var(--car-accent) 5%,var(--car-surface))}.more,.text{background:none;border:0;padding:13px 3px;font-size:12px}.more{width:100%;display:flex;justify-content:space-between;align-items:center}.month{margin:23px 3px 12px}.month h3{font-size:13px;text-transform:capitalize}.month p{font-size:10px;color:var(--car-muted);margin-top:6px;line-height:1.5}.periods{display:grid;grid-template-columns:repeat(var(--period-count,3),minmax(0,1fr));gap:3px;margin:0 0 7px;padding:0;background:transparent;border-bottom:1px solid #8882}.periods+ .panel{margin-top:16px}.periods button{display:flex;align-items:center;justify-content:center;gap:6px;min-width:0;min-height:40px;white-space:nowrap;border:0;background:transparent;border-radius:0;padding:12px 0;font-size:12px;color:var(--car-muted);border-bottom:2px solid transparent}.periods .selected{background:transparent;border-bottom-color:var(--car-text);color:var(--car-text);font-weight:600}.periods:has([data-period="current_trip"]) button{font-size:10px}.panel>h3{margin-bottom:18px}.hero .metric strong{font-size:30px}.hero .metric small{display:block;margin:7px 0 0;font-size:11px}.secondary{margin-top:23px}.secondary .metric strong{font-size:18px}.chart{margin-top:24px}.chart svg{display:block;width:100%;height:auto;max-height:150px}.chart .muted{font-size:9px}.mean{stroke:var(--car-text);stroke-width:1;stroke-dasharray:3 3;fill:none;opacity:.6}.range{font-size:12px;border-top:1px solid #8882;margin-top:18px;padding-top:14px}.range strong{font-size:18px;font-weight:500}.notice{background:rgba(128,128,128,.05);border:0;padding:10px;border-radius:9px;font-size:11px;width:100%;text-align:left;margin-top:18px;display:flex;justify-content:space-between}.categories .row{font-size:11px;margin-top:14px;color:var(--car-muted)}.compact{flex:none;width:85px;padding:2px}.compact button{padding:5px;font-size:11px}.details{margin:17px 3px;font-size:12px}.details summary{cursor:pointer;padding:10px 0}.details p{margin:13px 0}.counter{padding:15px 0;border-bottom:1px solid #8882}.counter .metrics{margin-top:10px}.counter strong{font-size:13px}.counter .metric strong{font-size:16px}.empty{padding:30px 12px;font-size:13px;color:var(--car-muted);line-height:1.6}.error:empty{display:none}.error{font-size:12px;padding:8px;color:var(--error-color,#ac594d)}.modal{background:var(--car-surface);color:var(--car-text);border:1px solid #8882;border-radius:22px;padding:24px;width:min(92vw,440px);max-height:90dvh;box-shadow:0 12px 60px #0003}.modal::backdrop{background:#0006;backdrop-filter:blur(3px)}.modal h2{font-size:19px}.modal p{margin:15px 0}.modal label{display:block;font-size:11px;color:var(--car-muted);margin:18px 0}.modal input,.modal select{display:block;width:100%;margin-top:7px;padding:12px;border-radius:10px;border:1px solid #8883;background:transparent;color:var(--car-text);font-size:16px}.modal summary{font-size:12px;cursor:pointer;padding-top:14px}.save{border:0;background:var(--car-accent);color:white;border-radius:12px;width:100%;padding:13px;margin-top:12px}.form-two{display:grid;grid-template-columns:1fr 1fr;gap:10px}.form-error{color:var(--error-color,#a44);font-size:12px}@media(max-width:380px){.session,.panel{padding:15px}.metric strong{font-size:18px}.metric small{font-size:9px}.hero .metric strong{font-size:27px}.session-head{font-size:10px}.metrics{gap:8px}.form-two{grid-template-columns:1fr}}
    .modal input,.modal select{min-width:0;max-width:100%}.form-two{grid-template-columns:repeat(2,minmax(0,1fr))}@media(max-width:440px){.form-two{grid-template-columns:1fr;gap:0}}
    .main-tabs{background:transparent;border-radius:0;padding:0;gap:0;border-bottom:1px solid #8882}.main-tabs button{min-width:0;border-radius:0;padding:13px 2px;font-size:13px;border-bottom:2px solid transparent;white-space:nowrap}.main-tabs button.selected{background:transparent;box-shadow:none;border-bottom-color:var(--car-accent);color:var(--car-text)}.top{gap:6px;margin-bottom:19px}.refresh{flex:none;width:30px;height:30px;padding:5px}.insight .panel{background:transparent;border:0;border-bottom:1px solid #8882;border-radius:0;padding:20px 3px;margin:0}.insight .hero .metric strong{font-size:38px}.insight .hero .metric small{display:inline;margin-left:6px;font-size:12px}.insight .metrics.two.hero .metric strong{font-size:30px}.parked-summary{width:100%;background:transparent;border:0;border-bottom:1px solid #8882;padding:18px 3px;font-size:13px;text-align:left}.parked-summary strong{font-size:13px;font-weight:500}.parked-month{border-top:1px solid #8882;padding-top:16px;margin:14px 3px}.parked-month p{font-size:15px;color:var(--car-text)}
  `;
}
CarLedgerCard.styles+=`.unaccounted-usage{margin:0 0 24px}.unaccounted-usage>h3{font:400 17px/1.4 "Segoe UI",sans-serif;margin:0 0 12px}.unaccounted-usage>.metrics{margin:0 0 12px}.gap-entry{margin:0 0 10px}.gap-entry>.row{margin-bottom:8px}.gap-entry>.row strong{font:400 13px/1.4 "Segoe UI",sans-serif}.gap-details>summary{min-height:44px;padding:10px 0;font:400 13px/1.5 "Segoe UI",sans-serif;cursor:pointer}.gap-form{padding:4px 0 12px}.gap-form label{display:block;margin:12px 0;font:400 12px/1.5 "Segoe UI",sans-serif;color:var(--car-muted)}.gap-form input,.gap-form select{display:block;width:100%;min-height:44px;margin-top:6px;padding:10px;border:1px solid var(--divider-color,#8885);border-radius:8px;background:var(--card-background-color,#fff);color:var(--primary-text-color);font:400 14px/1.5 "Segoe UI",sans-serif}.gap-form .save{min-height:44px}.gap-form .form-error:empty,.gap-form .form-saved:empty{display:none}`;
// Keep the legacy registration/hot-refresh behavior only for legacy consumers.
// The managed NIO view imports the same base privately; it never mutates Car.
if(!new URL(import.meta.url).searchParams.has('nio_owned')){
  const registeredCarLedger=customElements.get('car-ledger-card');
  if(registeredCarLedger){
    for(const key of Object.getOwnPropertyNames(CarLedgerCard.prototype)){
      if(key!=='constructor')Object.defineProperty(registeredCarLedger.prototype,key,Object.getOwnPropertyDescriptor(CarLedgerCard.prototype,key));
    }
    registeredCarLedger.styles=CarLedgerCard.styles;
  }else customElements.define('car-ledger-card',CarLedgerCard);
  window.customCards=window.customCards||[];window.customCards.push({type:'car-ledger-card',name:'Car Ledger',description:'Charging, trips and consumption in one snapshot dashboard'});
}
export { CarLedgerCard };
