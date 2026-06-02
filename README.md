# World Cup 2026 Office Pool

A shareable Streamlit app for running a FIFA World Cup 2026 office pool. Participants enter a display name, submit picks, and compete on a live leaderboard.

## Features

- Pick champion, runner-up, 4 semi-finalists, 12 group winners, and 3 bonus questions
- One entry per display name (case-insensitive)
- Picks lock at first kickoff (June 11, 2026, 15:00 UTC)
- Password-protected admin page to enter results and recalculate scores
- SQLite for local development; Supabase for shared cloud deployment

## Scoring

| Pick | Points |
|------|--------|
| Champion | 25 |
| Runner-up | 15 |
| Each semi-finalist | 10 |
| Each group winner | 3 |
| Each bonus question | 5 |

Edit scoring values in [`src/config.py`](src/config.py).

## Local development

```bash
cd "World Cup Pool"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set admin password (required for Admin page)
export ADMIN_PASSWORD=your-secret-password

streamlit run app.py
```

Open http://localhost:8501. Data is stored in `data/pool.sqlite`.

## Deploy to Streamlit Community Cloud

Streamlit Cloud resets local disk on redeploy, so use Supabase for persistent storage.

### 1. Create a Supabase project

1. Sign up at [supabase.com](https://supabase.com) and create a free project.
2. In the SQL Editor, run:

```sql
CREATE TABLE entries (
    id BIGSERIAL PRIMARY KEY,
    display_name TEXT NOT NULL,
    picks JSONB NOT NULL DEFAULT '{}',
    total_points INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX entries_display_name_lower_idx ON entries (LOWER(display_name));

CREATE TABLE results (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ
);

INSERT INTO results (id, data) VALUES (1, '{}');

ALTER TABLE entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read entries" ON entries FOR SELECT USING (true);
CREATE POLICY "Allow public insert entries" ON entries FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update entries" ON entries FOR UPDATE USING (true);

CREATE POLICY "Allow public read results" ON results FOR SELECT USING (true);
CREATE POLICY "Allow public upsert results" ON results FOR ALL USING (true);
```

3. Copy your project URL and anon/public API key from **Project Settings → API**.

### 2. Push to GitHub

Push this repo to a GitHub repository.

### 3. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub repo.
2. Set the main file path to `app.py`.
3. Add secrets ( **Advanced settings → Secrets** ):

```toml
ADMIN_PASSWORD = "your-secret-password"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

4. Deploy and share the public URL with your office.

## Project structure

```
app.py                  Home page — join with display name
pages/
  1_Make_Picks.py       Submit / edit picks
  2_Leaderboard.py      Rankings
  3_Admin.py            Enter results (password protected)
src/
  config.py             Scoring, deadline, settings
  database.py           SQLite + Supabase storage
  models.py             Data classes
  scoring.py            Point calculation
  validation.py         Pick validation and deadline lock
data/
  teams_2026.json       48 teams by group
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ADMIN_PASSWORD` | Yes (Admin page) | Password for admin login |
| `SUPABASE_URL` | Cloud deploy | Supabase project URL |
| `SUPABASE_KEY` | Cloud deploy | Supabase anon/public key |

If Supabase credentials are not set, the app uses local SQLite automatically.
