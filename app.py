
import pandas as pd
import plotly.graph_objects as go
from flask import Flask, render_template, request
import os

app = Flask(__name__)

def load_data():
    df = pd.read_excel("Performeter_2025_AI.xlsx", sheet_name="DATA INPUT", header=6)
    df.columns = df.columns.str.strip()
    return df

@app.route("/", methods=["GET", "POST"])
def index():
    df = load_data()

    kraje = sorted(df["Kraj"].dropna().unique())
    odvetvia = sorted(df["Odvetvie"].dropna().unique())
    zamestnanci_kategorie = sorted(df["Kategória zamestnancov"].dropna().unique())
    firmy = df["Názov"].dropna().unique()

    selected_kraj = request.form.get("kraj")
    selected_odvetvie = request.form.get("odvetvie")
    selected_zam = request.form.get("zamestnanci")
    selected_trzby = request.form.get("trzby")
    selected_firmy = request.form.getlist("firmy")
    action = request.form.get("action")

    df_filtered = df.copy()

    if selected_kraj:
        df_filtered = df_filtered[df_filtered["Kraj"] == selected_kraj]

    if selected_odvetvie:
        df_filtered = df_filtered[df_filtered["Odvetvie"] == selected_odvetvie]

    if selected_zam:
        df_filtered = df_filtered[df_filtered["Kategória zamestnancov"] == selected_zam]

    if selected_trzby:
        try:
            min_val, max_val = map(float, selected_trzby.split("-"))
            df_filtered = df_filtered[df_filtered["Tržby rok 2023"].between(min_val, max_val)]
        except:
            pass

    tachometer_html = None
    if action == "Porovnaj vybrané firmy" and selected_firmy:
        df_vybrane = df_filtered[df_filtered["Názov"].isin(selected_firmy)]
        if not df_vybrane.empty:
            tachometer_html = render_compare_tachometer(df_vybrane)

    return render_template("index.html",
                           kraje=kraje,
                           odvetvia=odvetvia,
                           zamestnanci=zamestnanci_kategorie,
                           firmy=df_filtered["Názov"].unique(),
                           selected_firmy=selected_firmy,
                           tachometer_html=tachometer_html)

def render_compare_tachometer(df):
    df = df.sort_values("PM INDEX FINAL 2024", ascending=False).head(10)
    pm_indexy = df["PM INDEX FINAL 2024"].tolist()
    mena = df["Názov"].tolist()

    fig = go.Figure()

    # body
    angles = [val / 400 * 180 for val in pm_indexy]
    for i, (a, m) in enumerate(zip(angles, mena)):
        fig.add_trace(go.Scatterpolar(
            r=[0.8],
            theta=[a],
            mode="markers",
            marker=dict(size=12),
            name=m,
            hovertext=m,
            showlegend=False
        ))

    # ručička - priemer
    avg = sum(pm_indexy) / len(pm_indexy)
    avg_angle = avg / 400 * 180
    fig.add_trace(go.Scatterpolar(
        r=[0, 0.9],
        theta=[0, avg_angle],
        mode="lines",
        line=dict(color="blue", width=3),
        name="Priemer"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(direction="clockwise", rotation=90)
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig.to_html(include_plotlyjs="cdn")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
