import streamlit as st

# Sidebar labels are set here (change "Home" to any title you prefer).
pg = st.navigation(
    [
        st.Page("pages/0_Home.py", title="Home", icon="🏠"),
        st.Page("pages/1_Make_Picks.py", title="Make Picks", icon="⚽"),
        st.Page("pages/2_Leaderboard.py", title="Leaderboard", icon="🏆"),
        st.Page("pages/3_Admin.py", title="Admin", icon="🔒"),
    ]
)
pg.run()
