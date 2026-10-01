import streamlit as st
import pandas as pd
import sqlite3

# --- Page Setup ---
st.set_page_config(
    page_title="Pizza Bonici Rouffiac - Stock & Commandes",
    page_icon="🍕",
    layout="wide"
)

# Custom styling to mirror the Google Sheet's green theme
st.markdown("""
<style>
    .metric-card {
        background-color: #f1f8f3;
        border: 1px solid #c2e0c6;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .section-header {
        background-color: #1e4620;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-top: 16px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "pizzeria_stock.db"

# --- Complete Menu & Stock Catalog matching your sheet ---
MENU_DATA = [
    # 1. PÂTE & BASES
    ("1. PÂTE & BASES", "Farine (Flour) (sac 25kg)", 10, 0, "Fournisseur A", ""),
    ("1. PÂTE & BASES", "Huile (Oil) (bidon 5L)", 4, 0, "Fournisseur A", ""),
    ("1. PÂTE & BASES", "Levure (Yeast) (boîte / kg)", 4, 0, "Fournisseur A", ""),
    ("1. PÂTE & BASES", "Sauce Tomate (boîte 2.5kg)", 12, 0, "Fournisseur A", ""),
    ("1. PÂTE & BASES", "Crème fraîche (brique 1L)", 8, 0, "Fournisseur A", ""),

    # 2. FROMAGES
    ("2. FROMAGES", "Emmental râpé (kg)", 35, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Mozzarella Fior Di Latte (seau kg)", 20, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Chèvre bûche (pièce / kg)", 6, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Roquefort (kg)", 4, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Camembert (pièce 250g)", 6, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Cheddar (paquet / kg)", 8, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Reblochon (pièce)", 5, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Raclette (kg)", 6, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Cabécou (pièce)", 10, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Gorgonzola (kg)", 4, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Copeaux de Parmesan (kg)", 4, 0, "Fournisseur Laitier", ""),
    ("2. FROMAGES", "Burrata (pièce)", 8, 0, "Fournisseur Laitier", ""),

    # 3. VIANDES & POISSONS
    ("3. VIANDES & POISSONS", "Jambon blanc (kg)", 15, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Poulet émincé (kg)", 12, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Lardons fumés (kg)", 8, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Viande Kebab halal (kg)", 12, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Merguez (paquet / kg)", 6, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Bœuf haché (kg)", 8, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Steak Black Angus (pièce 150g)", 25, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Steak végétal (pièce)", 10, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Bacon (paquet / kg)", 6, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Chorizo (kg)", 6, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Jambon de Parme (kg)", 5, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Magret de canard (kg)", 4, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Foie gras (bloc / kg)", 2, 0, "Boucherie", ""),
    ("3. VIANDES & POISSONS", "Saumon fumé (kg)", 4, 0, "Marée", ""),
    ("3. VIANDES & POISSONS", "Thon (boîte)", 6, 0, "Épicerie", ""),
    ("3. VIANDES & POISSONS", "Anchois (bocal / boîte)", 4, 0, "Épicerie", ""),
    ("3. VIANDES & POISSONS", "Œufs (plateau 30)", 3, 0, "Frais", ""),

    # 4. LÉGUMES & FRUITS
    ("4. LÉGUMES & FRUITS", "Champignons frais (kg / cagette)", 8, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Poivrons (kg)", 5, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Aubergines (kg)", 4, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Courgettes (kg)", 4, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Oignons frais (filet 5kg)", 3, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Oignons rouges (filet / kg)", 3, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Oignons frits (sachet 1kg)", 4, 0, "Épicerie", ""),
    ("4. LÉGUMES & FRUITS", "Confit d'oignons (bocal)", 3, 0, "Épicerie", ""),
    ("4. LÉGUMES & FRUITS", "Pommes de terre (sac 10kg)", 3, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Galettes de pomme de terre (carton)", 4, 0, "Surgelés", ""),
    ("4. LÉGUMES & FRUITS", "Tomates fraîches (kg / cagette)", 6, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Tomates séchées (bocal kg)", 3, 0, "Épicerie", ""),
    ("4. LÉGUMES & FRUITS", "Roquette (sachet 500g)", 4, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Salade verte (cagette / sachet)", 6, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Olives noires (seau / bocal)", 3, 0, "Épicerie", ""),
    ("4. LÉGUMES & FRUITS", "Câpres (bocal)", 2, 0, "Épicerie", ""),
    ("4. LÉGUMES & FRUITS", "Ananas (boîte)", 3, 0, "Épicerie", ""),
    ("4. LÉGUMES & FRUITS", "Ail & Persil (botte / kg)", 2, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Aneth / Citron (botte / pièce)", 2, 0, "Primeur", ""),
    ("4. LÉGUMES & FRUITS", "Pignons de pin / Noix (sachet kg)", 2, 0, "Épicerie", ""),

    # 5. SAUCES & ÉPICES
    ("5. SAUCES & ÉPICES", "Ketchup (bidon / flacon)", 4, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Sauce piquante (bouteille)", 3, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Tabasco (bouteille)", 2, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Moutarde (pot kg)", 2, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Sauce Blanche (flacon / bidon)", 4, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Sauce BBQ (flacon / bidon)", 3, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Sauce Sweet Chili (bouteille)", 3, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Sauce Cheddar (poche / flacon)", 4, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Crème Balsamique (bouteille)", 2, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Miel (pot / flacon)", 2, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Confiture de figue (pot)", 2, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Épices orientales (pot / sachet)", 2, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Curry (pot / sachet)", 2, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Épices mexicaines (pot / sachet)", 2, 0, "Épicerie", ""),
    ("5. SAUCES & ÉPICES", "Origan / Herbes de Provence (sachet)", 2, 0, "Épicerie", ""),

    # 6. TAPAS & FRITES
    ("6. TAPAS & FRITES", "Frites Deeps (carton kg)", 6, 0, "Surgelés", ""),
    ("6. TAPAS & FRITES", "Frites patates douces (carton kg)", 4, 0, "Surgelés", ""),
    ("6. TAPAS & FRITES", "Chicken Wings (carton)", 4, 0, "Surgelés", ""),
    ("6. TAPAS & FRITES", "Crousti Tenders (carton)", 5, 0, "Surgelés", ""),
    ("6. TAPAS & FRITES", "Bouchées Camembert (carton)", 3, 0, "Surgelés", ""),
    ("6. TAPAS & FRITES", "Chili Cheese Nuggets (carton)", 4, 0, "Surgelés", ""),
    ("6. TAPAS & FRITES", "Tomato Mozza Melters (carton)", 3, 0, "Surgelés", ""),
    ("6. TAPAS & FRITES", "Nacho Cheese (carton)", 3, 0, "Surgelés", ""),
    ("6. TAPAS & FRITES", "Onions Rings (carton)", 4, 0, "Surgelés", ""),

    # 7. EMBALLAGES
    ("7. EMBALLAGES", "Boîtes Pizza 25 cm (paquet 100)", 4, 0, "Emballages", ""),
    ("7. EMBALLAGES", "Boîtes Pizza 33 cm (paquet 100)", 8, 0, "Emballages", ""),
    ("7. EMBALLAGES", "Boîtes Pizza 40 cm (paquet 50)", 4, 0, "Emballages", ""),
    ("7. EMBALLAGES", "Boîtes Pizza Enfant 18 cm (paquet 100)", 3, 0, "Emballages", ""),
    ("7. EMBALLAGES", "Serviettes en papier (carton / paquet)", 5, 0, "Emballages", ""),
    ("7. EMBALLAGES", "Sacs à emporter Kraft (paquet / carton)", 4, 0, "Emballages", ""),
    ("7. EMBALLAGES", "Papiers burger (paquet)", 3, 0, "Emballages", ""),
    ("7. EMBALLAGES", "Pots à sauce (carton 1000)", 2, 0, "Emballages", ""),

    # 8. HYGIÈNE & ENTRETIEN
    ("8. HYGIÈNE & ENTRETIEN", "Liquide vaisselle plonge (bidon 5L)", 3, 0, "Hygiène & Entretien", ""),
    ("8. HYGIÈNE & ENTRETIEN", "Tampons à récurer / Éponges (paquet 10)", 3, 0, "Hygiène & Entretien", ""),
    ("8. HYGIÈNE & ENTRETIEN", "Sel adoucisseur lave-vaisselle (sac 10kg)", 2, 0, "Hygiène & Entretien", ""),
    ("8. HYGIÈNE & ENTRETIEN", "Savon machine lave-vaisselle (bidon 10L)", 2, 0, "Hygiène & Entretien", ""),
    ("8. HYGIÈNE & ENTRETIEN", "Liquide de rinçage machine (bidon 5L)", 2, 0, "Hygiène & Entretien", ""),
    ("8. HYGIÈNE & ENTRETIEN", "Dégraissant cuisine pro (bidon / spray)", 3, 0, "Hygiène & Entretien", ""),
    ("8. HYGIÈNE & ENTRETIEN", "Désinfectant surfaces alimentaires (spray 750ml)", 4, 0, "Hygiène & Entretien", ""),
    ("8. HYGIÈNE & ENTRETIEN", "Rouleaux essuie-tout pro (pack bobines)", 4, 0, "Hygiène & Entretien", ""),
    ("8. HYGIÈNE & ENTRETIEN", "Sacs poubelle 100L (rouleau)", 4, 0, "Hygiène & Entretien")
]

# --- Database Setup & Initialization ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Check if table exists and has the 'notes' column; if not, recreate it
    c.execute("PRAGMA table_info(stock)")
    cols = [col[1] for col in c.fetchall()]
    if "notes" not in cols:
        c.execute("DROP TABLE IF EXISTS stock")
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            item TEXT UNIQUE,
            par_level REAL DEFAULT 0,
            current_count REAL DEFAULT 0,
            supplier TEXT DEFAULT '',
            notes TEXT DEFAULT ''
        )
    """)
    conn.commit()

    c.execute("SELECT count(*) FROM stock")
    if c.fetchone()[0] == 0:
        for row in MENU_DATA:
            if len(row) == 5:
                # Format: (item, category, par, count, supplier)
                c.execute("""
                    INSERT INTO stock (item, category, par_level, current_count, supplier, notes)
                    VALUES (?, ?, ?, ?, ?, '')
                """, row)
            elif len(row) >= 6:
                # Format: (category, item, par, count, supplier, notes)
                c.execute("""
                    INSERT INTO stock (category, item, par_level, current_count, supplier, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, row[:6])
        conn.commit()
    conn.close()

init_db()

def get_full_stock():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT id, category, item, par_level, current_count, supplier, notes FROM stock", conn)
    conn.close()
    
    # Calculate Order Needed and Status exactly like the Google Sheet
    df["order_needed"] = (df["par_level"] - df["current_count"]).apply(lambda x: max(0.0, x))
    df["status"] = df["order_needed"].apply(lambda x: "ORDER" if x > 0 else "OK")
    return df

def save_changes(records):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for row in records:
        c.execute("""
            UPDATE stock 
            SET current_count = ?, par_level = ?, supplier = ?, notes = ?
            WHERE id = ?
        """, (row["current_count"], row["par_level"], row.get("supplier", ""), row.get("notes", ""), row["id"]))
    conn.commit()
    conn.close()

# --- Main App Layout ---
st.title("🍕 Pizzeria - Inventaire & Commandes")

df = get_full_stock()

# KPI Top Bar (matching the top of the Google Sheet)
items_to_order = df[df["order_needed"] > 0]
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Articles à Commander", len(items_to_order))
kpi2.metric("Articles en Stock Suffisant", len(df) - len(items_to_order))
kpi3.metric("Total Produits Suivis", len(df))

st.divider()

# Filter by Section (or show all together)
categories = ["Toutes les Sections (Vue Complète)"] + sorted(df["category"].unique().tolist())
selected_section = st.selectbox("📂 Section du Stock :", categories)

if selected_section == "Toutes les Sections (Vue Complète)":
    display_df = df
else:
    display_df = df[df["category"] == selected_section]

st.caption("💡 Modifiez directement la colonne **Stock Réel** ou **Stock Idéal**, puis cliquez sur **Enregistrer**.")

# Single unified editable table mirroring the exact sheet
edited_df = st.data_editor(
    display_df[["id", "category", "item", "par_level", "current_count", "order_needed", "status", "supplier", "notes"]],
    disabled=["id", "category", "item", "order_needed", "status"],
    column_config={
        "id": None,  # Hidden
        "category": st.column_config.TextColumn("Section", width="medium"),
        "item": st.column_config.TextColumn("Produit", width="large"),
        "par_level": st.column_config.NumberColumn("Stock Idéal", min_value=0, step=1, width="small"),
        "current_count": st.column_config.NumberColumn("Stock Réel", min_value=0, step=1, width="small"),
        "order_needed": st.column_config.NumberColumn("À Commander", width="small"),
        "status": st.column_config.TextColumn("Statut", width="small"),
        "supplier": st.column_config.TextColumn("Fournisseur", width="medium"),
        "notes": st.column_config.TextColumn("Notes / Emplacement", width="medium"),
    },
    hide_index=True,
    use_container_width=True
)

if st.button("💾 Enregistrer les Modifications", type="primary", use_container_width=True):
    save_changes(edited_df.to_dict("records"))
    st.success("✅ Stock enregistré avec succès !")
    st.rerun()

# Quick WhatsApp/SMS Summary Expander for the Owners
with st.expander("📲 Voir le récapitulatif de commande à copier (WhatsApp / SMS)"):
    if items_to_order.empty:
        st.info("Aucun article à commander.")
    else:
        summary_text = "📋 *COMMANDE PIZZERIA* :\n\n"
        for sup, group in items_to_order.groupby("supplier"):
            sup_name = sup if sup.strip() else "Fournisseur Non Défini"
            summary_text += f"🔹 *{sup_name}* :\n"
            for _, r in group.iterrows():
                qty = int(r["order_needed"]) if r["order_needed"].is_integer() else r["order_needed"]
                summary_text += f"  • {r['item']} : *{qty}*\n"
            summary_text += "\n"
        st.text_area("Texte prêt à envoyer :", value=summary_text, height=180)