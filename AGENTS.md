## Learned User Preferences

- Apply IQVIA Digital brand guidelines when styling the app (`src/branding.py`, `.streamlit/config.toml`).
- Home **Continue** should navigate directly to **Make Picks** (`st.switch_page`), not stay on Home.
- Sidebar home page should be labeled **Home** (not `app`) via `st.navigation` in `app.py`.
- Dark horse bonus: exclude the nine seeded teams and show the eligibility note; other pick sections keep the full team list.
- Office announcements should not mention a pool passcode — this pool does not use one.
- `ADMIN_PASSWORD` is a separate app secret; it is not the Supabase database password.

## Learned Workspace Facts

- Streamlit app for the FIFA World Cup 2026 office pool (IQVIA Digital).
- Live deployment is on Replit: https://world-cup-pool-iqviadigital.replit.app (not Streamlit Cloud).
- GitHub repo: https://github.com/sckriegs/world-cup-pool
- Supabase stores `entries` and `results`; SQLite is used locally when `SUPABASE_URL` / `SUPABASE_KEY` are unset.
- Replit deployment secrets must include `SUPABASE_URL`, `SUPABASE_KEY` (anon public key), and `ADMIN_PASSWORD`.
- No `POOL_PASSCODE` is configured for this office pool.
- Picks lock at first kickoff (June 11, 2026, 15:00 UTC); scoring values live in `src/config.py`.
- Leaderboard partial scoring uses `has_scoring_data()`; `results_are_set()` is only for tournament-complete messaging.
- An older Replit deploy showed leaderboard dashes until republished with the `has_scoring_data` fix.
- Seeded teams excluded from the dark horse pick are defined in `SEEDED_TEAMS` in `src/config.py`.
