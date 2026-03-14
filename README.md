# BIS Portal v4

## Setup
1. Place your JSON files in the `json/` folder:
   - `json/bis_data.json`
   - `json/lims_data.json`
   - `json/crs_data.json`

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run:
   ```
   python app.py
   ```

4. Open http://127.0.0.1:5000

## 🎨 How to Change Colors

All color customization is in `static/css/main.css`:

- **Dark theme colors**: Section 1 (`:root { ... }`)
- **Light theme colors**: Section 2 (`body.theme-light { ... }`)
- **Header background**: Section 4 (`header { background: ... }`)
- **Footer**: Section 5 (`footer { ... }`)

Key variables:
- `--bg` — page background
- `--accent` / `--accent-light` — blue accent
- `--gold` / `--gold-light` — gold accent
- `--text`, `--muted` — text colors
- `--nav-*-active` — nav item highlight colors

## Changes in v4
- Light theme: very light blue background (was yellowish)
- Header: always dark navy blue (both themes)
- Larger fonts in header and footer
- Fee Calculator: shows ALL columns from govt website (Component Name, all slabs, full column names)
- PDF Export on all search pages
- More formal government aesthetic
- Government identity bar
- Official disclaimer in footer
