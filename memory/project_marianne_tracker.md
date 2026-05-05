---
name: Marianne Tracker — project context
description: Campaign tracker web app for content creators, feminine redesign done 2026-05-05
type: project
---

Flask-based campaign tracker at `/Users/Hendri/Documents/ray/daily-task/app/`.

**Why:** A personal creator workspace for tracking brand campaigns/deadlines.

**How to apply:** Any changes to the app should keep the feminine aesthetic (rose/lavender palette, Nunito font), mobile-responsive layout, and the custom category picker pattern.

**Stack:** Flask 3.0, SQLite (konten.db), Flatpickr (date picker CDN), Nunito (Google Fonts).

**Key design decisions (2026-05-05 redesign):**
- Color palette: rose `#C2386B` + lavender `#9B5FC9` + blush background `#FDF5F8`
- Font: Nunito (Google Fonts)
- Date picker: Flatpickr (replaces browser default `<input type="date">`)
- Category field: custom select + hidden text input; "Tulis nama sendiri" option reveals text input
- Platform field: changed from datalist → styled `<select>` 
- Table rows: left border accent — amber for H-5, red for overdue, green for done
- Status badges: color-coded per status via CSS class `status-{{ status_slug }}`
- Mobile: bottom tab bar on <768px, cards instead of table rows
- Gradient stat cards: 3 cards (total/H-5/done) with gradient backgrounds
- Sort: backend always orders by nearest deadline (already in `ordered_tracker_query()`)

**Run:** `source venv/bin/activate && python3 app/app.py` from project root.
