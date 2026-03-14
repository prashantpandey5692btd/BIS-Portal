from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# ── Resolve paths ──────────────────────────────────────────────────────────
BASE     = os.path.dirname(__file__)
JSON_DIR = os.path.join(BASE, 'json')   # all 3 JSON files live here

# ── Load BIS IS Number fee data ────────────────────────────────────────────
with open(os.path.join(JSON_DIR, 'bis_data.json'), 'r', encoding='utf-8') as f:
    BIS_DATA = json.load(f)

# ── Load LIMS lab data ─────────────────────────────────────────────────────
LIMS_DATA = {}
lims_path = os.path.join(JSON_DIR, 'lims_data.json')
if os.path.exists(lims_path):
    with open(lims_path, 'r', encoding='utf-8') as f:
        LIMS_DATA = json.load(f)

# ── Load CRS lab data ──────────────────────────────────────────────────────
CRS_DATA = {}
crs_path = os.path.join(JSON_DIR, 'crs_data.json')
if os.path.exists(crs_path):
    with open(crs_path, 'r', encoding='utf-8') as f:
        CRS_DATA = json.load(f)


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE ROUTES
#  Each route passes `active_page` so base.html can highlight the nav link.
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html', active_page='home')


@app.route('/fee-calculator')
def fee_calculator():
    return render_template('fee_calculator.html', active_page='fee')


@app.route('/lab-search')
def lab_search():
    return render_template('lab_search.html', active_page='lims')


@app.route('/crs-search')
def crs_search():
    return render_template('crs_search.html', active_page='crs')


# ═══════════════════════════════════════════════════════════════════════════
#  API — Fee Calculator  (bis_data.json)
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/search')
def search():
    """Autocomplete: returns up to 12 matches on is_no or is_title."""
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    results = []
    for item in BIS_DATA:
        if query in item['is_no'].lower() or query in item['is_title'].lower():
            results.append({
                'is_no':    item['is_no'],
                'is_title': item['is_title'][:90] + ('…' if len(item['is_title']) > 90 else '')
            })
        if len(results) >= 12:
            break
    return jsonify(results)


@app.route('/api/details')
def details():
    """Full record for a single IS number."""
    is_no = request.args.get('is_no', '').strip()
    for item in BIS_DATA:
        if item['is_no'].lower() == is_no.lower():
            return jsonify(item)
    return jsonify({'error': 'Not found'}), 404


# ═══════════════════════════════════════════════════════════════════════════
#  API — LIMS Lab Search  (lims_data.json)
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/lims/states')
def lims_states():
    """List of all states (id + name) for the dropdown."""
    states = []
    for key, val in LIMS_DATA.items():
        states.append({
            'id':   val.get('state_id', key),
            'name': val.get('state_name', key)
        })
    states.sort(key=lambda x: x['name'])
    return jsonify(states)


@app.route('/api/lims/search')
def lims_search():
    """Filter labs by state, lab_code, lab_name, or free-text query."""
    state    = request.args.get('state',    '').strip().lower()
    lab_code = request.args.get('lab_code', '').strip().lower()
    lab_name = request.args.get('lab_name', '').strip().lower()
    query    = request.args.get('q',        '').strip().lower()

    results = []
    for _, state_data in LIMS_DATA.items():
        sname = state_data.get('state_name', '').lower()
        if state and state not in sname:
            continue

        for lab in state_data.get('labs', []):
            lcode = str(lab.get('Lab Code', '')).lower()
            lname = lab.get('Lab Name',  '').lower()
            addr  = lab.get('Address',   '').lower()

            if lab_code and lab_code not in lcode:
                continue
            if lab_name and lab_name not in lname:
                continue
            if query and query not in lname and query not in lcode and query not in addr:
                continue

            results.append({
                'state':          state_data.get('state_name', ''),
                'lab_code':       lab.get('Lab Code',       ''),
                'lab_name':       lab.get('Lab Name',       ''),
                'address':        lab.get('Address',        ''),
                'contact_person': lab.get('Contact Person', ''),
                'contact_number': lab.get('Contact Number', ''),
                'email':          lab.get('Email',          ''),
                'validity_date':  lab.get('Validity Date',  ''),
                'scope_count':    len(lab.get('View Scope', []))
            })

    return jsonify(results[:200])


@app.route('/api/lims/lab/<lab_code>')
def lims_lab_detail(lab_code):
    """Full lab record including View Scope + Testing Charges Breakup."""
    for _, state_data in LIMS_DATA.items():
        for lab in state_data.get('labs', []):
            if str(lab.get('Lab Code', '')) == lab_code:
                return jsonify({'state': state_data.get('state_name', ''), **lab})
    return jsonify({'error': 'Not found'}), 404


# ═══════════════════════════════════════════════════════════════════════════
#  API — CRS Lab Search  (crs_data.json)
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/crs/search')
def crs_search_api():
    """Filter CRS records by osl_code, lab_name, is_no, or free-text query."""
    osl_code = request.args.get('osl_code', '').strip().lower()
    lab_name = request.args.get('lab_name', '').strip().lower()
    is_no    = request.args.get('is_no',    '').strip().lower()
    query    = request.args.get('q',        '').strip().lower()

    results = []
    seen    = set()

    for _, is_data in CRS_DATA.items():
        for rec in is_data.get('records', []):
            lname   = rec.get('Lab Name',             '').lower()
            osl     = str(rec.get('Osl Code',         '')).lower()
            is_num  = rec.get('Indian Standard No.',  '').lower()
            product = rec.get('Product',              '').lower()

            if osl_code and osl_code not in osl:
                continue
            if lab_name and lab_name not in lname:
                continue
            if is_no    and is_no    not in is_num:
                continue
            if query    and query not in lname and query not in osl and query not in product:
                continue

            key = (osl, lname, is_num)
            if key in seen:
                continue
            seen.add(key)

            results.append({
                'lab_name':        rec.get('Lab Name',                               ''),
                'osl_code':        rec.get('Osl Code',                              ''),
                'is_number':       rec.get('Indian Standard No.',                   ''),
                'product':         rec.get('Product',                               ''),
                'grade':           rec.get('Grade / Type / Size / Designation etc.',''),
                'testing_charges': rec.get('Testing Charges (Excl. Of Taxes)',      ''),
                'validity_date':   rec.get('Validity Date',                         ''),
                'remark':          rec.get('Remark',                                ''),
                'breakup':         rec.get('Testing Charges Breakup',               [])
            })

        if len(results) >= 500:
            break

    return jsonify(results[:500])


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True, port=5000)
