# Eastern Catholic Readings

A web application that displays Byzantine and Maronite liturgical readings.

- **Live Website:** [https://www.ebrahimkaram.com/EasternCatholicReadings/](https://www.ebrahimkaram.com/EasternCatholicReadings/)
- **GitHub Repository:** [https://github.com/EbrahimKaram/ByzantineLiturgyReadings](https://github.com/EbrahimKaram/ByzantineLiturgyReadings)

Hopefully if you want a better reference
https://romaniancatholic.org/liturgical-calendar

## Data Sources
- **Byzantine calendar:** [Google Calendar](https://calendar.google.com/calendar/u/0/embed?src=9pp7p6nos1t3tca6sjo4g6hui0@group.calendar.google.com) (Derived from [St. George Cathedral](https://www.stgeorgeoh.org/calendar))
- **Maronite calendar:** computed in the browser from Easter, 14 September, 25 December, and 6 January, with a compact lectionary of references (`client/src/data/maroniteLectionary.json`)
- **Scripture Text:** [Bible-api.com](https://bible-api.com) (Douay-Rheims Version)


# Running
To debug and test. You need to make sure you cd into `client`
 `npm run dev `

To build the product which included minimization
 `npm run build `

 Github has an automated deploy that would create the build for me.

## Python scripts

Byzantine and Maronite calendar scripts share one virtual environment and one `requirements.txt` at the repo root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then run scripts from their folders, for example:

```powershell
python "byzantine-calendars\extract_readings.py"
python "Maronite Readings\distill_maronite_lectionary.py"
```

Maronite dates are predicted; the distiller rebuilds the compact lectionary from `Maronite Readings/maronite_calendar.json` if that source is ever refreshed. The scrape script `build_maronite_calendar.py` is unused by the site.

In `client`, run `npm test` to check Easter and season-anchor logic.

## Support
If you find this project useful, please consider supporting it!

<a href="https://www.buymeacoffee.com/bobKaram" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>