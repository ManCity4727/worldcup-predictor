import streamlit as st
import pandas as pd
import numpy as np
import itertools
from scipy.stats import poisson

st.set_page_config(
    page_title="Tournament Simulator",
    page_icon="🏆",
    layout="wide"
)

# ── Flag map ──────────────────────────────────────────────────
flag_map = {
    'Argentina': '🇦🇷', 'Spain': '🇪🇸', 'France': '🇫🇷',
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Portugal': '🇵🇹', 'Brazil': '🇧🇷',
    'Morocco': '🇲🇦', 'Netherlands': '🇳🇱', 'Belgium': '🇧🇪',
    'Germany': '🇩🇪', 'Croatia': '🇭🇷', 'Colombia': '🇨🇴',
    'Mexico': '🇲🇽', 'Senegal': '🇸🇳', 'Uruguay': '🇺🇾',
    'United States': '🇺🇸', 'Japan': '🇯🇵', 'Switzerland': '🇨🇭',
    'Iran': '🇮🇷', 'Turkey': '🇹🇷', 'Ecuador': '🇪🇨',
    'Austria': '🇦🇹', 'South Korea': '🇰🇷', 'Australia': '🇦🇺',
    'Algeria': '🇩🇿', 'Egypt': '🇪🇬', 'Canada': '🇨🇦',
    'Norway': '🇳🇴', 'Ivory Coast': '🇨🇮', 'Panama': '🇵🇦',
    'Sweden': '🇸🇪', 'Czechia': '🇨🇿', 'Paraguay': '🇵🇾',
    'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Tunisia': '🇹🇳', 'DR Congo': '🇨🇩',
    'Uzbekistan': '🇺🇿', 'Qatar': '🇶🇦', 'Iraq': '🇮🇶',
    'South Africa': '🇿🇦', 'Saudi Arabia': '🇸🇦', 'Jordan': '🇯🇴',
    'Bosnia and Herzegovina': '🇧🇦', 'Cape Verde': '🇨🇻',
    'Ghana': '🇬🇭', 'Curacao': '🇨🇼', 'Haiti': '🇭🇹',
    'New Zealand': '🇳🇿',
}

def get_flag(team):
    return flag_map.get(team, '🏳️')

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('results.csv')
    wc = df[df['tournament'] == 'FIFA World Cup'].copy()
    wc = wc.dropna(subset=['home_score', 'away_score'])
    wc['date'] = pd.to_datetime(wc['date'])
    home_attack = wc.groupby('home_team')['home_score'].mean()
    home_defense = wc.groupby('home_team')['away_score'].mean()
    away_attack = wc.groupby('away_team')['away_score'].mean()
    away_defense = wc.groupby('away_team')['home_score'].mean()
    attack = (home_attack + away_attack) / 2
    defense = (home_defense + away_defense) / 2
    avg_goals = wc['home_score'].mean()
    team_stats = pd.DataFrame({
        'attack': attack, 'defense': defense
    }).dropna()
    return team_stats, avg_goals

team_stats, avg_goals = load_data()

# ── Data ──────────────────────────────────────────────────────
fifa_rankings = {
    'Argentina': 1, 'Spain': 2, 'France': 3, 'England': 4,
    'Portugal': 5, 'Brazil': 6, 'Morocco': 7, 'Netherlands': 8,
    'Belgium': 9, 'Germany': 10, 'Croatia': 11, 'Colombia': 13,
    'Mexico': 14, 'Senegal': 15, 'Uruguay': 16, 'United States': 17,
    'Japan': 18, 'Switzerland': 19, 'Iran': 20, 'Turkey': 22,
    'Ecuador': 23, 'Austria': 24, 'South Korea': 25, 'Australia': 27,
    'Algeria': 28, 'Egypt': 29, 'Canada': 30, 'Norway': 31,
    'Ivory Coast': 33, 'Panama': 34, 'Sweden': 38, 'Czechia': 40,
    'Paraguay': 41, 'Scotland': 42, 'Tunisia': 45, 'DR Congo': 46,
    'Uzbekistan': 50, 'Qatar': 56, 'Iraq': 57, 'South Africa': 60,
    'Saudi Arabia': 61, 'Jordan': 63, 'Bosnia and Herzegovina': 64,
    'Cape Verde': 67, 'Ghana': 73, 'Curacao': 82, 'Haiti': 83,
    'New Zealand': 85
}

continent_map = {
    'Brazil': 'South America', 'Argentina': 'South America',
    'Uruguay': 'South America', 'Colombia': 'South America',
    'Ecuador': 'South America', 'Paraguay': 'South America',
    'France': 'Europe', 'Spain': 'Europe', 'England': 'Europe',
    'Germany': 'Europe', 'Portugal': 'Europe', 'Netherlands': 'Europe',
    'Belgium': 'Europe', 'Croatia': 'Europe', 'Switzerland': 'Europe',
    'Denmark': 'Europe', 'Norway': 'Europe', 'Austria': 'Europe',
    'Sweden': 'Europe', 'Scotland': 'Europe', 'Turkey': 'Europe',
    'Serbia': 'Europe', 'Czechia': 'Europe',
    'Bosnia and Herzegovina': 'Europe', 'Italy': 'Europe',
    'Morocco': 'Africa', 'Senegal': 'Africa', 'Ghana': 'Africa',
    'Cameroon': 'Africa', 'Ivory Coast': 'Africa', 'Tunisia': 'Africa',
    'Algeria': 'Africa', 'Egypt': 'Africa', 'South Africa': 'Africa',
    'DR Congo': 'Africa', 'Cape Verde': 'Africa',
    'Japan': 'Asia', 'South Korea': 'Asia', 'Iran': 'Asia',
    'Saudi Arabia': 'Asia', 'Australia': 'Asia', 'Qatar': 'Asia',
    'Iraq': 'Asia', 'Jordan': 'Asia', 'Uzbekistan': 'Asia',
    'United States': 'CONCACAF', 'Mexico': 'CONCACAF',
    'Canada': 'CONCACAF', 'Panama': 'CONCACAF',
    'Haiti': 'CONCACAF', 'Curacao': 'CONCACAF',
    'New Zealand': 'Oceania',
}

continent_advantage = {
    'Asia': 1.185, 'CONCACAF': 1.110,
    'South America': 1.098, 'Europe': 1.055,
    'Africa': 0.979, 'Oceania': 1.0,
}

squad_fatigue = {
    'France': 0.82, 'England': 0.79, 'Spain': 0.78,
    'Belgium': 0.76, 'Germany': 0.75, 'Netherlands': 0.73,
    'Portugal': 0.71, 'Morocco': 0.70, 'Denmark': 0.70,
    'Croatia': 0.69, 'Norway': 0.68, 'Argentina': 0.68,
    'Brazil': 0.65, 'Turkey': 0.65, 'Austria': 0.66,
    'Sweden': 0.64, 'Senegal': 0.63, 'Colombia': 0.60,
    'Uruguay': 0.61, 'Ivory Coast': 0.62, 'Japan': 0.58,
    'Bosnia and Herzegovina': 0.58, 'Ecuador': 0.57,
    'Australia': 0.54, 'Ghana': 0.55, 'South Korea': 0.55,
    'Mexico': 0.55, 'Algeria': 0.56, 'Uzbekistan': 0.47,
    'Canada': 0.52, 'Cape Verde': 0.52, 'Egypt': 0.53,
    'Tunisia': 0.54, 'Paraguay': 0.50, 'United States': 0.50,
    'Panama': 0.49, 'DR Congo': 0.49, 'Iran': 0.48,
    'Curacao': 0.48, 'Saudi Arabia': 0.46, 'Haiti': 0.46,
    'South Africa': 0.45, 'Iraq': 0.45, 'Qatar': 0.44,
    'Jordan': 0.44, 'New Zealand': 0.43, 'Scotland': 0.67,
    'Switzerland': 0.67,
}

groups = {
    'A': ['Mexico', 'South Africa', 'South Korea', 'Czechia'],
    'B': ['Canada', 'Switzerland', 'Bosnia and Herzegovina', 'Qatar'],
    'C': ['United States', 'Paraguay', 'Australia', 'Turkey'],
    'D': ['Germany', 'Curacao', 'Ivory Coast', 'Ecuador'],
    'E': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'F': ['Brazil', 'Morocco', 'Scotland', 'Haiti'],
    'G': ['Argentina', 'Jordan', 'Colombia', 'Portugal'],
    'H': ['France', 'Norway', 'Uruguay', 'Senegal'],
    'I': ['Spain', 'DR Congo', 'Algeria', 'Austria'],
    'J': ['England', 'Panama', 'Croatia', 'Ghana'],
    'K': ['Belgium', 'New Zealand', 'Cape Verde', 'Saudi Arabia'],
    'L': ['Egypt', 'Iran', 'Uzbekistan', 'Iraq'],
}

# ── Model functions ───────────────────────────────────────────
def get_lambda(team_a, team_b):
    if team_a in team_stats.index and team_b in team_stats.index:
        hist = (team_stats.loc[team_a, 'attack'] *
                (team_stats.loc[team_b, 'defense'] / avg_goals))
    else:
        hist = avg_goals
    rank_a = 1.4 - (fifa_rankings.get(team_a, 43) / 85) * 0.8
    rank_b = 1.4 - (fifa_rankings.get(team_b, 43) / 85) * 0.8
    rank_lambda = avg_goals * (rank_a / rank_b)
    return round(0.4 * hist + 0.6 * rank_lambda, 3)

def get_continent_boost(team):
    tc = continent_map.get(team, None)
    if tc == 'CONCACAF':
        return continent_advantage.get(tc, 1.0)
    return 1.0

def get_fatigue_mult(team):
    fatigue = squad_fatigue.get(team, 0.60)
    return round(1.05 - ((fatigue - 0.45) /
                         (0.82 - 0.45)) * 0.17, 3)

def dixon_coles(g_a, g_b, la, lb, rho=0.1):
    if g_a == 0 and g_b == 0:
        return 1 - la * lb * rho
    elif g_a == 0 and g_b == 1:
        return 1 + la * rho
    elif g_a == 1 and g_b == 0:
        return 1 + lb * rho
    elif g_a == 1 and g_b == 1:
        return 1 - rho
    return 1.0

def simulate_match(team_a, team_b):
    la = get_lambda(team_a, team_b)
    lb = get_lambda(team_b, team_a)
    la *= get_continent_boost(team_a)
    lb *= get_continent_boost(team_b)
    la *= get_fatigue_mult(team_a)
    lb *= get_fatigue_mult(team_b)
    la = max(la, 0.1)
    lb = max(lb, 0.1)
    ga = poisson.rvs(la)
    gb = poisson.rvs(lb)
    corr = dixon_coles(ga, gb, la, lb)
    if np.random.random() > corr:
        ga = poisson.rvs(la)
        gb = poisson.rvs(lb)
    if ga > gb:
        return team_a, ga, gb
    elif gb > ga:
        return team_b, ga, gb
    else:
        eta = poisson.rvs(la * 0.33)
        etb = poisson.rvs(lb * 0.33)
        if eta > etb:
            return team_a, ga, gb
        elif etb > eta:
            return team_b, ga, gb
        else:
            ra = fifa_rankings.get(team_a, 43)
            rb = fifa_rankings.get(team_b, 43)
            if np.random.random() < (0.52 if ra < rb else 0.48):
                return team_a, ga, gb
            return team_b, ga, gb

def simulate_group(teams):
    """Simulate a group and return full standings with stats."""
    points = {t: 0 for t in teams}
    gf = {t: 0 for t in teams}
    ga = {t: 0 for t in teams}
    w = {t: 0 for t in teams}
    d = {t: 0 for t in teams}
    l = {t: 0 for t in teams}
    results = []

    for team_a, team_b in itertools.combinations(teams, 2):
        winner, ga_goals, gb_goals = simulate_match(team_a, team_b)
        gf[team_a] += ga_goals
        ga[team_a] += gb_goals
        gf[team_b] += gb_goals
        ga[team_b] += ga_goals

        results.append({
            'home': team_a,
            'away': team_b,
            'home_score': ga_goals,
            'away_score': gb_goals
        })

        if ga_goals > gb_goals:
            points[team_a] += 3
            w[team_a] += 1
            l[team_b] += 1
        elif gb_goals > ga_goals:
            points[team_b] += 3
            w[team_b] += 1
            l[team_a] += 1
        else:
            points[team_a] += 1
            points[team_b] += 1
            d[team_a] += 1
            d[team_b] += 1

    standings = sorted(teams, key=lambda t: (
        points[t], gf[t] - ga[t], gf[t]
    ), reverse=True)

    table = []
    for i, team in enumerate(standings):
        table.append({
            'pos': i + 1,
            'team': team,
            'flag': get_flag(team),
            'w': w[team],
            'd': d[team],
            'l': l[team],
            'gf': gf[team],
            'ga': ga[team],
            'gd': gf[team] - ga[team],
            'pts': points[team],
            'advanced': i < 2
        })

    return table, results, standings

def simulate_full_tournament(groups):
    """Simulate one complete tournament, return all data."""
    all_group_tables = {}
    all_group_results = {}
    all_third_place = []
    group_winners = {}
    group_runners = {}

    for group_name, teams in groups.items():
        table, results, standings = simulate_group(teams)
        all_group_tables[group_name] = table
        all_group_results[group_name] = results
        group_winners[group_name] = standings[0]
        group_runners[group_name] = standings[1]
        third = standings[2]
        third_pts = next(r['pts'] for r in table if r['team'] == third)
        third_gd = next(r['gd'] for r in table if r['team'] == third)
        third_gf = next(r['gf'] for r in table if r['team'] == third)
        all_third_place.append({
            'team': third,
            'points': third_pts,
            'gd': third_gd,
            'gf': third_gf,
            'group': group_name
        })

    all_third_place.sort(key=lambda x: (
        x['points'], x['gd'], x['gf']
    ), reverse=True)
    best_thirds = [t['team'] for t in all_third_place[:8]]

    # Mark third place teams that advanced
    for group_name, table in all_group_tables.items():
        third_team = next(
            r['team'] for r in table if r['pos'] == 3)
        if third_team in best_thirds:
            for row in table:
                if row['team'] == third_team:
                    row['advanced'] = True
                    row['third_qualified'] = True

    wA=group_winners['A']; wB=group_winners['B']
    wC=group_winners['C']; wD=group_winners['D']
    wE=group_winners['E']; wF=group_winners['F']
    wG=group_winners['G']; wH=group_winners['H']
    wI=group_winners['I']; wJ=group_winners['J']
    wK=group_winners['K']; wL=group_winners['L']
    rA=group_runners['A']; rB=group_runners['B']
    rC=group_runners['C']; rD=group_runners['D']
    rF=group_runners['F']; rG=group_runners['G']
    rH=group_runners['H']; rI=group_runners['I']
    rJ=group_runners['J']; rK=group_runners['K']
    rL=group_runners['L']
    t = best_thirds

    r32_matches = [
        (rA, rB), (wF, rC), (wE, t[0]), (wC, rF),
        (wH, t[1]), (t[2], rI), (wA, rD), (wD, rB),
        (wK, rH), (wJ, t[3]), (wL, rJ), (wI, rJ),
        (wB, t[4]), (wG, t[5]), (t[6], rG), (rK, rL),
    ]

    def play(a, b):
        winner, gs, gc = simulate_match(a, b)
        return winner, a, b, gs, gc

    r32 = [play(a, b) for a, b in r32_matches]
    r32_w = [r[0] for r in r32]

    r16_matches = [
        (r32_w[0],r32_w[1]), (r32_w[2],r32_w[3]),
        (r32_w[4],r32_w[5]), (r32_w[6],r32_w[7]),
        (r32_w[8],r32_w[9]), (r32_w[10],r32_w[11]),
        (r32_w[12],r32_w[13]), (r32_w[14],r32_w[15]),
    ]
    r16 = [play(a, b) for a, b in r16_matches]
    r16_w = [r[0] for r in r16]

    qf_matches = [
        (r16_w[0],r16_w[1]), (r16_w[2],r16_w[3]),
        (r16_w[4],r16_w[5]), (r16_w[6],r16_w[7]),
    ]
    qf = [play(a, b) for a, b in qf_matches]
    qf_w = [r[0] for r in qf]

    sf_matches = [
        (qf_w[0],qf_w[1]), (qf_w[2],qf_w[3])
    ]
    sf = [play(a, b) for a, b in sf_matches]
    sf_w = [r[0] for r in sf]

    final_w, fa, fb, fgs, fgc = play(sf_w[0], sf_w[1])

    return {
        'group_tables': all_group_tables,
        'group_results': all_group_results,
        'best_thirds': best_thirds,
        'r32': r32,
        'r16': r16,
        'qf': qf,
        'sf': sf,
        'final': (final_w, fa, fb, fgs, fgc),
        'champion': final_w
    }

# ── UI ────────────────────────────────────────────────────────
st.title("🏆 World Cup 2026 Tournament Simulator")
st.caption("Simulates the full tournament using the "
           "official FIFA bracket — group stage to final")

st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### Run a single simulation")
    st.caption("See one complete tournament play out with "
               "group tables, results and full bracket")
with col2:
    simulate_btn = st.button(
        "🎲 Simulate One Tournament",
        type="primary",
        use_container_width=True
    )

if simulate_btn:
    with st.spinner("Simulating tournament..."):
        sim = simulate_full_tournament(groups)

    # ── Group stage tables ────────────────────────────────────
    st.divider()
    st.subheader("📊 Group Stage Results")

    group_names = list(groups.keys())
    for i in range(0, len(group_names), 3):
        row_groups = group_names[i:i+3]
        cols = st.columns(3)

        for col, gname in zip(cols, row_groups):
            with col:
                st.markdown(f"**Group {gname}**")
                table = sim['group_tables'][gname]

                for row in table:
                    if row.get('third_qualified'):
                        badge = "🟡"
                    elif row['advanced']:
                        badge = "🟢"
                    else:
                        badge = "🔴"

                    st.markdown(
                        f"{badge} {row['flag']} **{row['team']}** "
                        f"· {row['pts']}pts "
                        f"· {row['w']}W {row['d']}D {row['l']}L "
                        f"· GD {row['gd']:+d}",
                        unsafe_allow_html=False
                    )
                st.markdown("")

    st.caption("🟢 Qualified · 🟡 Qualified as best 3rd · "
               "🔴 Eliminated")

    # ── Best third place ──────────────────────────────────────
    st.divider()
    st.subheader("⭐ Best Third Place Teams")
    thirds_cols = st.columns(8)
    for i, team in enumerate(sim['best_thirds']):
        with thirds_cols[i]:
            st.markdown(
                f"**{get_flag(team)}**  \n{team}",
                unsafe_allow_html=False
            )

    # ── Knockout rounds ───────────────────────────────────────
    st.divider()
    st.subheader("🏆 Knockout Stage")

    def show_round(matches, title):
        st.markdown(f"**{title}**")
        cols = st.columns(min(len(matches), 4))
        for i, (winner, ta, tb, gs, gc) in enumerate(matches):
            with cols[i % len(cols)]:
                fa = get_flag(ta)
                fb = get_flag(tb)
                won_a = winner == ta
                st.markdown(
                    f"{'**' if won_a else ''}"
                    f"{fa} {ta}{'**' if won_a else ''} "
                    f"{gs}–{gc} "
                    f"{'**' if not won_a else ''}"
                    f"{fb} {tb}{'**' if not won_a else ''}"
                )

    show_round(sim['r32'], "Round of 32")
    st.markdown("")
    show_round(sim['r16'], "Round of 16")
    st.markdown("")
    show_round(sim['qf'], "Quarterfinals")
    st.markdown("")
    show_round(sim['sf'], "Semifinals")

    # ── Final ─────────────────────────────────────────────────
    st.divider()
    champion = sim['champion']
    _, fa, fb, fgs, fgc = sim['final']

    st.subheader("🏆 Final")
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown(
            f"## {get_flag(fa)} {fa}",
            unsafe_allow_html=False
        )
    with c2:
        st.markdown(
            f"## {fgs} – {fgc}",
            unsafe_allow_html=False
        )
    with c3:
        st.markdown(
            f"## {get_flag(fb)} {fb}",
            unsafe_allow_html=False
        )

    st.success(
        f"🏆 {get_flag(champion)} **{champion}** "
        f"wins the 2026 World Cup!"
    )

st.divider()

# ── Multi simulation ──────────────────────────────────────────
st.subheader("📈 Run multiple simulations")
st.caption("Simulate thousands of tournaments to get "
           "win probabilities for every team")

n_sims = st.select_slider(
    "Number of simulations",
    options=[1000, 5000, 10000],
    value=1000
)

if st.button("🔮 Calculate Win Probabilities",
             use_container_width=True):

    all_teams = [t for g in groups.values() for t in g]
    counts = {t: {'r32':0,'r16':0,'qf':0,
                  'sf':0,'final':0,'win':0}
              for t in all_teams}

    progress = st.progress(0)
    status = st.empty()

    for i in range(n_sims):
        result = simulate_full_tournament(groups)
        for team in [r[0] for r in result['r32']]:
            counts[team]['r32'] += 1
        for team in [r[0] for r in result['r16']]:
            counts[team]['r16'] += 1
        for team in [r[0] for r in result['qf']]:
            counts[team]['qf'] += 1
        for team in [r[0] for r in result['sf']]:
            counts[team]['sf'] += 1
        for team in result['best_thirds'][:2]:
            pass
        _, fa, fb, _, _ = result['final']
        counts[fa]['final'] += 1
        counts[fb]['final'] += 1
        counts[result['champion']]['win'] += 1

        if i % 100 == 0:
            progress.progress((i+1)/n_sims)
            status.text(f"Simulating... {i+1}/{n_sims}")

    progress.progress(1.0)
    status.text("Done!")

    results = []
    for team in all_teams:
        c = counts[team]
        results.append({
            'team': team,
            'flag': get_flag(team),
            'rank': fifa_rankings.get(team, 99),
            'r32': round(c['r32']/n_sims*100, 1),
            'r16': round(c['r16']/n_sims*100, 1),
            'qf': round(c['qf']/n_sims*100, 1),
            'sf': round(c['sf']/n_sims*100, 1),
            'final': round(c['final']/n_sims*100, 1),
            'win': round(c['win']/n_sims*100, 1),
        })

    results.sort(key=lambda x: x['win'], reverse=True)

    st.divider()
    st.subheader(f"Results — {n_sims:,} simulations")

    top3 = results[:3]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            f"🥇 {top3[0]['flag']} {top3[0]['team']}",
            f"{top3[0]['win']}%", "Most likely winner")
    with c2:
        st.metric(
            f"🥈 {top3[1]['flag']} {top3[1]['team']}",
            f"{top3[1]['win']}%", "2nd most likely")
    with c3:
        st.metric(
            f"🥉 {top3[2]['flag']} {top3[2]['team']}",
            f"{top3[2]['win']}%", "3rd most likely")

    st.divider()
    st.markdown("**Full probability table**")

    header = st.columns([3,1.5,1.5,1.5,1.5,1.5,2])
    header[0].markdown("**Team**")
    header[1].markdown("**R32**")
    header[2].markdown("**R16**")
    header[3].markdown("**QF**")
    header[4].markdown("**SF**")
    header[5].markdown("**Win**")

    for r in results:
        cols = st.columns([3,1.5,1.5,1.5,1.5,1.5,2])
        cols[0].markdown(
            f"{r['flag']} **{r['team']}** "
            f"<span style='color:gray;font-size:11px'>"
            f"#{r['rank']}</span>",
            unsafe_allow_html=True
        )
        cols[1].markdown(f"{r['r32']}%")
        cols[2].markdown(f"{r['r16']}%")
        cols[3].markdown(f"{r['qf']}%")
        cols[4].markdown(f"{r['sf']}%")
        cols[5].markdown(f"**{r['win']}%**")
        cols[6].progress(r['win'] / 15)

    st.divider()
    st.caption(
        f"Poisson + FIFA rankings + fatigue + "
        f"continent advantage + Dixon-Coles · "
        f"Official FIFA 2026 bracket · "
        f"{n_sims:,} simulations"
    )
