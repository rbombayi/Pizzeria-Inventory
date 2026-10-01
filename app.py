import streamlit as st
import pandas as pd
import sqlite3

# --- Page Configuration ---
st.set_page_config(
    page_title="Pizza Bonici Rouffiac: Inventory",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- High-Contrast, Deep Black Styling ---
st.markdown("""
<style>
    /* Force dark, crisp typography */
    * {
        color: #111111 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Category Section Headers (Clean Dark Green Banners) */
    .cat-header {
        background-color: #1b4d2e !important;
        color: #ffffff !important;
        padding: 10px 16px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 18px !important;
        margin-top: 24px;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .cat-header * {
        color: #ffffff !important;
    }

    /* KPI Summary Cards */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #1b4d2e !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #222222 !important;
    }

    /* Badges */
    .badge-order {
        background-color: #fee2e2;
        color: #b91c1c !important;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .badge-ok {
        background-color: #dcfce7;
        color: #15803d !important;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }

    /* Input styling */
    input[type=number], input[type=text] {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "pizzeria_stock.db"

CATALOG = [
    # 1. PÂTE & BASES
    ("1. PÂTE & BASES", "Farine (Flour) (sac 25kg)", 10, 0, ""),
    ("1. PÂTE & BASES", "Huile (Oil) (bidon 5L)", 4, 0, ""),
    ("1. PÂTE & BASES", "Levure (Yeast) (boîte / kg)", 4, 0, ""),
    ("1. PÂTE & BASES", "Sauce Tomate (boîte 2.5kg)", 12, 0, ""),
    ("1. PÂTE & BASES", "Crème fraîche (brique 1L)", 8, 0, ""),

    # 2. FROMAGES
    ("2. FROMAGES", "Emmental râpé (kg)", 35, 0, ""),
    ("2. FROMAGES", "Mozzarella Fior Di Latte (seau kg)", 20, 0, ""),
    ("2. FROMAGES", "Chèvre bûche (pièce / kg)", 6, 0, ""),
    ("2. FROMAGES", "Roquefort (kg)", 4, 0, ""),
    ("2. FROMAGES", "Camembert (pièce 250g)", 6, 0, ""),
    ("2. FROMAGES", "Cheddar (paquet / kg)", 8, 0, ""),
    ("2. FROMAGES", "Reblochon (pièce)", 5, 0, ""),
    ("2. FROMAGES", "Raclette (kg)", 6, 0, ""),
    ("2. FROMAGES", "Cabécou (pièce)", 10, 0, ""),
    ("2. FROMAGES", "Gorgonzola (kg)", 4, 0, ""),
    ("2. FROMAGES", "Copeaux de Parmesan (kg)", 4, 0, ""),
    ("2. FROMAGES", "Burrata (pièce)", 8, 0, ""),

    # 3. VIANDES & POISSONS
    ("3. VIANDES & POISSONS", "Jambon blanc (kg)", 15, 0, ""),
    ("3. VIANDES & POISSONS", "Poulet émincé (kg)", 12, 0, ""),
    ("3. VIANDES & POISSONS", "Lardons fumés (kg)", 8, 0, ""),
    ("3. VIANDES & POISSONS", "Viande Kebab halal (kg)", 12, 0, ""),
    ("3. VIANDES & POISSONS", "Merguez (paquet / kg)", 6, 0, ""),
    ("3. VIANDES & POISSONS", "Bœuf haché (kg)", 8, 0, ""),
    ("3. VIANDES & POISSONS", "Steak Black Angus (pièce 150g)", 25, 0, ""),
    ("3. VIANDES & POISSONS", "Steak végétal (pièce)", 10, 0, ""),
    ("3. VIANDES & POISSONS", "Bacon (paquet / kg)", 6, 0, ""),
    ("3. VIANDES & POISSONS", "Chorizo (kg)", 6, 0, ""),
    ("3. VIANDES & POISSONS", "Jambon de Parme (kg)", 5, 0, ""),
    ("3. VIANDES & POISSONS", "Magret de canard (kg)", 4, 0, ""),
    ("3. VIANDES & POISSONS", "Foie gras (bloc / kg)", 2, 0, ""),
    ("3. VIANDES & POISSONS", "Saumon fumé (kg)", 4, 0, ""),
    ("3. VIANDES & POISSONS", "Thon (boîte)", 6, 0, ""),
    ("3. VIANDES & POISSONS", "Anchois (bocal / boîte)", 4, 0, ""),
    ("3. VIANDES & POISSONS", "Œufs (plateau 30)", 3, 0, ""),

    # 4. LÉGUMES & FRUITS
    ("4. LÉGUMES & FRUITS", "Champignons frais (kg / cagette)", 8, 0, ""),
    ("4. LÉGUMES & FRUITS", "Poivrons (kg)", 5, 0, ""),
    ("4. LÉGUMES & FRUITS", "Aubergines (kg)", 4, 0, ""),
    ("4. LÉGUMES & FRUITS", "Courgettes (kg)", 4, 0, ""),
    ("4. LÉGUMES & FRUITS", "Oignons frais (filet 5kg)", 3, 0, ""),
    ("4. LÉGUMES & FRUITS", "Oignons rouges (filet / kg)", 3, 0, ""),
    ("4. LÉGUMES & FRUITS", "Oignons frits (sachet 1kg)", 4, 0, ""),
    ("4. LÉGUMES & FRUITS", "Confit d'oignons (bocal)", 3, 0, ""),
    ("4. LÉGUMES & FRUITS", "Pommes de terre (sac 10kg)", 3, 0, ""),
    ("4. LÉGUMES & FRUITS", "Galettes de pomme de terre (carton)", 4, 0, ""),
    ("4. LÉGUMES & FRUITS", "Tomates fraîches (kg / cagette)", 6, 0, ""),
    ("4. LÉGUMES & FRUITS", "Tomates séchées (bocal kg)", 3, 0, ""),
    ("4. LÉGUMES & FRUITS", "Roquette (sachet 500g)", 4, 0, ""),
    ("4. LÉGUMES & FRUITS", "Salade verte (cagette / sachet)", 6, 0, ""),
    ("4. LÉGUMES & FRUITS", "Olives noires (seau / bocal)", 3, 0, ""),
    ("4. LÉGUMES & FRUITS", "Câpres (bocal)", 2, 0, ""),
    ("4. LÉGUMES & FRUITS", "Ananas (boîte)", 3, 0, ""),
    ("4. LÉGUMES & FRUITS", "Ail & Persil (botte / kg)", 2, 0, ""),
    ("4. LÉGUMES & FRUITS", "Aneth / Citron (botte / pièce)", 2, 0, ""),
    ("4. LÉGUMES & FRUITS", "Pignons de pin / Noix (sachet kg)", 2, 0, ""),

    # 5. SAUCES & ÉPICES
    ("5. SAUCES & ÉPICES", "Ketchup (bidon / flacon)", 4, 0, ""),
    ("5. SAUCES & ÉPICES", "Sauce piquante (bouteille)", 3, 0, ""),
    ("5. SAUCES & ÉPICES", "Tabasco (bouteille)", 2, 0, ""),
    ("5. SAUCES & ÉPICES", "Moutarde (pot kg)", 2, 0, ""),
    ("5. SAUCES & ÉPICES", "Sauce Blanche (flacon / bidon)", 4, 0, ""),
    ("5. SAUCES & ÉPICES", "Sauce BBQ (flacon / bidon)", 3, 0, ""),
    ("5. SAUCES & ÉPICES", "Sauce Sweet Chili (bouteille)", 3, 0, ""),
    ("5. SAUCES & ÉPICES", "Sauce Cheddar (poche / flacon)", 4, 0, ""),
    ("5. SAUCES & ÉPICES", "Crème Balsamique (bouteille)", 2, 0, ""),
    ("5. SAUCES & ÉPICES", "Miel (pot / flacon)", 2, 0, ""),
    ("5. SAUCES & ÉPICES", "Confiture de figue (pot)", 2, 0, ""),
    ("5. SAUCES & ÉPICES", "Épices orientales (pot / sachet)", 2, 0, ""),
    ("5. SAUCES & ÉPICES", "Curry (pot / sachet)", 2, 0, ""),
    ("5. SAUCES & ÉPICES", "Épices mexicaines (pot / sachet)", 2, 0, ""),
    ("5. SAUCES & ÉPICES", "Origan / Herbes de Provence (sachet)", 2, 0, ""),

    # 6. TAPAS & FRITES
    ("6. TAPAS & FRITES", "Frites Deeps (carton kg)", 6, 0, ""),
    ("6. TAPAS & FRITES", "Frites patates douces (carton kg)", 4, 0, ""),
    ("6. TAPAS & FRITES", "Chicken Wings (carton)", 4, 0, ""),
    ("6. TAPAS & FRITES", "Crousti Tenders (carton)", 5, 0, ""),
    ("6. TAPAS & FRITES", "Bouchées Camembert (carton)", 3, 0, ""),
    ("6. TAPAS & FRITES", "Chili Cheese Nuggets (carton)", 4, 0, ""),
    ("6. TAPAS & FRITES", "Tomato Mozza Melters (carton)", 3, 0, ""),
    ("6. TAPAS & FRITES", "Nacho Cheese (carton)", 3, 0, ""),
    ("6. TAPAS & FRITES", "Onions Rings (carton)", 4, 0, ""),

    # 7. EMBALLAGES
    ("7. EMBALLAGES", "Boîtes Pizza 25 cm (paquet 100)", 4, 0, ""),
    ("7. EMBALLAGES", "Boîtes Pizza 33 cm (paquet 100)", 8, 0, ""),
    ("7. EMBALLAGES", "Boîtes Pizza 40 cm (paquet 50)", 4, 0, ""),
    ("7. EMBALLAGES", "Boîtes Pizza Enfant 18 cm (paquet 100)", 3, 0, ""),
    ("7. EMBALLAGES", "Serviettes en papier (carton / paquet)", 5, 0, ""),
    ("7. EMBALLAGES", "Sacs à emporter Kraft (paquet / carton)", 4, 0, ""),
    ("7. EMBALLAGES", "Papiers burger (paquet)", 3, 0, ""),
    ("7. EMBALLAGES", "Pots à sauce (carton 1000)", 2, 0, ""),

    # 8. HYGIÈNE & ENTRETIEN
    ("8. HYGIÈNE & ENTRETIEN", "Liquide vaisselle plonge (bidon 5L)", 3, 0, ""),
    ("8. HYGIÈNE & ENTRETIEN", "Tampons à récurer / Éponges (paquet 10)", 3, 0, ""),
    ("8. HYGIÈNE & ENTRETIEN", "Sel adoucisseur lave-vaisselle (sac 10kg)", 2, 0, ""),
    ("8. HYGIÈNE & ENTRETIEN", "Savon machine lave-vaisselle (bidon 10L)", 2, 0, ""),
    ("8. HYGIÈNE & ENTRETIEN", "Liquide de rinçage machine (bidon 5L)", 2, 0, ""),
    ("8. HYGIÈNE & ENTRETIEN", "Dégraissant cuisine pro (bidon / spray)", 3, 0, ""),
    ("8. HYGIÈNE & ENTRETIEN", "Désinfectant surfaces alimentaires (spray 750ml)", 4, 0, ""),
    ("8. HYGIÈNE & ENTRETIEN", "Rouleaux essuie-tout pro (pack bobines)", 4, 0, ""),
    ("8. HYGIÈNE & ENTRETIEN", "Sacs poubelle 100L (rouleau)", 4, 0, "")
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='stock'")
    table_exists = c.fetchone()[0] > 0
    
    # Auto-repair if previous buggy schema inverted "Sacs poubelle" or par levels are all 0
    recreate = False
    if table_exists:
        c.execute("SELECT count(*) FROM stock WHERE category LIKE '%Sacs poubelle%'")
        if c.fetchone()[0] > 0:
            recreate = True
        c.execute("SELECT sum(par_level) FROM stock")
        val = c.fetchone()[0]
        if val is None or val == 0:
            recreate = True
    else:
        recreate = True

    if recreate:
        c.execute("DROP TABLE IF EXISTS stock")
        c.execute("""
            CREATE TABLE stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                item TEXT UNIQUE,
                par_level REAL DEFAULT 0,
                current_count REAL DEFAULT 0,
                notes TEXT DEFAULT ''
            )
        """)
        c.executemany("""
            INSERT INTO stock (category, item, par_level, current_count, notes)
            VALUES (?, ?, ?, ?, ?)
        """, CATALOG)
        conn.commit()
    conn.close()

init_db()

def get_stock():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT id, category, item, par_level, current_count, notes FROM stock", conn)
    conn.close()
    df["order_needed"] = (df["par_level"] - df["current_count"]).apply(lambda x: max(0.0, x))
    df["status"] = df["order_needed"].apply(lambda x: "ORDER" if x > 0 else "OK")
    return df

def update_item_value(item_id, current_count, par_level, notes):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE stock 
        SET current_count = ?, par_level = ?, notes = ?
        WHERE id = ?
    """, (current_count, par_level, notes, item_id))
    conn.commit()
    conn.close()

# --- Title & Top Header ---
st.title("🍕 Pizza Bonici Rouffiac: Inventory")

df = get_stock()

# Summary KPIs
to_order = df[df["order_needed"] > 0]
k1, k2, k3 = st.columns(3)
k1.metric("Articles à Commander", len(to_order))
k2.metric("En Stock Suffisant", len(df) - len(to_order))
k3.metric("Total Articles", len(df))

st.divider()

# Section Selector
categories = ["Toutes les Sections"] + sorted(df["category"].unique().tolist())
selected_category = st.selectbox("Sélectionner une Section :", categories)

sections_to_show = sorted(df["category"].unique().tolist()) if selected_category == "Toutes les Sections" else [selected_category]

# --- Native, High-Contrast Inventory Grid ---
for sec in sections_to_show:
    st.markdown(f"<div class='cat-header'>{sec}</div>", unsafe_allow_html=True)
    sec_df = df[df["category"] == sec]

    # Header Row
    cols = st.columns([3.5, 1.2, 1.2, 1.2, 1.3, 2.5])
    cols[0].markdown("**Produit**")
    cols[1].markdown("**Stock Idéal**")
    cols[2].markdown("**Stock Réel**")
    cols[3].markdown("**À Commander**")
    cols[4].markdown("**Statut**")
    cols[5].markdown("**Notes / Emplacement**")

    # Product Rows
    for _, row in sec_df.iterrows():
        c0, c1, c2, c3, c4, c5 = st.columns([3.5, 1.2, 1.2, 1.2, 1.3, 2.5])
        
        # Crisp Product Title
        c0.markdown(f"<div style='font-size:15px; font-weight:600; padding-top:6px; color:#111111;'>{row['item']}</div>", unsafe_allow_html=True)
        
        # Stock Idéal
        new_par = c1.number_input(
            label=f"par_{row['id']}",
            value=int(row['par_level']),
            min_value=0,
            step=1,
            key=f"par_{row['id']}",
            label_visibility="collapsed"
        )

        # Stock Réel
        new_count = c2.number_input(
            label=f"count_{row['id']}",
            value=int(row['current_count']),
            min_value=0,
            step=1,
            key=f"count_{row['id']}",
            label_visibility="collapsed"
        )

        # À Commander
        diff = max(0, new_par - new_count)
        c3.markdown(f"<div style='font-size:16px; font-weight:700; padding-top:6px; color:#111;'>{diff}</div>", unsafe_allow_html=True)
        
        # Statut Badge
        if diff > 0:
            c4.markdown("<div style='padding-top:4px;'><span class='badge-order'>🚨 ORDER</span></div>", unsafe_allow_html=True)
        else:
            c4.markdown("<div style='padding-top:4px;'><span class='badge-ok'>✅ OK</span></div>", unsafe_allow_html=True)

        # Notes / Emplacement
        new_note = c5.text_input(
            label=f"note_{row['id']}",
            value=row['notes'] if row['notes'] else "",
            placeholder="Étagère, marque...",
            key=f"note_{row['id']}",
            label_visibility="collapsed"
        )

        # Direct database sync if modified
        if (new_count != row['current_count']) or (new_par != row['par_level']) or (new_note != row['notes']):
            update_item_value(row['id'], new_count, new_par, new_note)

# --- WhatsApp Order Summary ---
st.write("")
with st.expander("📲 Voir le récapitulatif pour commande WhatsApp"):
    fresh_df = get_stock()
    fresh_order = fresh_df[fresh_df["order_needed"] > 0]
    if fresh_order.empty:
        st.info("🎉 Aucun article à commander !")
    else:
        text_out = "📋 *COMMANDE PIZZA BONICI ROUFFIAC* :\n\n"
        for sec_name, group in fresh_order.groupby("category"):
            text_out += f"*{sec_name}* :\n"
            for _, r in group.iterrows():
                qty = int(r["order_needed"]) if r["order_needed"].is_integer() else r["order_needed"]
                text_out += f"  • {r['item']} : *{qty}*\n"
            text_out += "\n"
        st.text_area("Texte prêt à copier :", value=text_out, height=220)
