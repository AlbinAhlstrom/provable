# 🏨 Provable Semiautomatiserat Acceptanstest: Hotellbokningssystem

Detta test är optimerat för **maximal bekvämlighet och minimal datainmatning**. Du slipper mata in fält manuellt tack vare inbyggda **`✨ Auto-fill Exempel`**- och **`🌱 Seed Demo Data`**-funktioner i gränssnittet, samt ett valfritt Python-skript som kan köra dataflödet åt dig medan du tittar i webbläsaren.

---

## 📋 Förutsättningar
- [ ] PM Studio körs på: `http://localhost:5173`
- [ ] Workspace API körs på: `http://localhost:8001` (Swagger: `http://localhost:8001/docs`)

---

## 📍 STEG 1: Snabbstart av Hotellarkitekturen (1 Klick)

1. Öppna **`http://localhost:5173`**.
2. Klicka på **`🗑️ Reset Workspace`** uppe till höger.
3. Klistra in prompten:
   ```text
   Hotellbokningssystem för ett boutiquehotell med rumshantering, gäster, städstatus och rumsbokningar.
   ```
4. Klicka på **`⚡ Snabbstart`**.

---

## 📍 STEG 2: Semiautomatiskt Dataskapande i Live Preview (1 Klick)

1. Gå till fliken **`📱 Preview`** längst upp.
2. **Alternativ 1 (Magiska Seed-knappen i UI)**:
   - Klicka på den gröna knappen **`🌱 Seed Demo Data (:8001)`** uppe till höger i tabellen.
   - *Resultat*: Systemet skapar automatiskt 2 gäster, 2 rum (ett `CLEAN` och ett `DIRTY`) och provbokningar direkt i den körande appen på port 8001!
   - Byt mellan **Guest**, **Room** och **Booking** i aggregatväljaren för att se all data listad i realtidstabellen.

3. **Alternativ 2 (Auto-fill för enskilda formulär)**:
   - Välj t.ex. **Room** i väljaren.
   - Klicka på knappen **`✨ Auto-fill Exempel`** ovanför formuläret.
   - Formuläret fylls direkt i med giltiga värden (`ROOM-...`, `Deluxe Suite`, `DIRTY`).
   - Klicka på **`🚀 Skapa Room`**.

---

## 📍 STEG 3: Injicera Städspärren i Domain Engine (1 Klick)

1. Klicka på fliken **`🧬 Domain Engine`** längst upp.
2. Expandera aggregatet **`Room`**.
3. Klicka på knappen **`➕ Add BDD Spec for Room`**.
4. Klicka på knappen **`✨ Auto-fill Exempel`** i det öppnade formuläret!
   - *Resultat*: Hela specifikationen (Titel, Given, When, Then för städspärren) fylls i automatiskt!
5. Klicka på **`💾 Register BDD Specification`**.
   - *Verifiering*: TDD-motorn körs synkront och specifikationen blir **`🟢 FULFILLED`**.

---

## 📍 STEG 4: Verifiera i Live Preview & Swagger

1. Klicka tillbaka till **`📱 Preview`**.
2. Välj **Room** $\rightarrow$ Verifiera att alla dina rum listas med deras städstatus.
3. Klicka på fliken **`⚡ API (Swagger)`** $\rightarrow$ Kör `GET /api/rooms` för att se att exakt samma data finns i det råa API:et.

---

## ⚡ Valfritt: Kör Skriptassistenten via Terminalen
Om du hellre vill att Python skickar in all data till port 8001 medan du har webbläsaren öppen:
```powershell
python scripts/run_hotel_demo_scenario.py --step all
```
Sedan klickar du bara på **`🔄 Ladda om (:8001)`** i PM Studio för att se allt dyka upp direkt!
