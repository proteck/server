import csv
import os
import sys
import re
from textual.app import App, ComposeResult
from textual.widgets import Input, DataTable, Header, Footer, Static, TabbedContent, TabPane
from textual.containers import Vertical, Horizontal
from textual import work
from collections import defaultdict

CSV_FILE = "resultats/tous_les_resultats.csv"

SHOOT_TYPES = {
    "POINTS": {"label": "Points", "color": "#f1c40f"},
    "MOUCHE": {"label": "Mouche", "color": "#e74c3c"},
    "CHANNE": {"label": "Channe", "color": "#3498db"},
    "JEUNESSE": {"label": "Jeunesse", "color": "#2ecc71"},
    "INDIVIDUEL": {"label": "Individuel", "color": "#9b59b6"},
    "GROUPES": {"label": "Groupes", "color": "#e67e22"},
}

def render_ascii_chart(history, title="Progression", height=10):
    """Renders a large ASCII bar chart for score progression."""
    if not history or len(history) < 1:
        return "[i]Sélectionnez un tireur pour voir le graphique de progression[/i]"
    
    history.sort()
    years = [h[0] for h in history]
    scores = [h[1] for h in history]
    
    min_s, max_s = min(scores), max(scores)
    y_min = max(0, min_s - 5)
    y_max = max_s + 2
    y_range = y_max - y_min if y_max != y_min else 1
    
    chart = [f"[b][yellow]{title}[/][/b]", ""]
    
    for r in range(height, 0, -1):
        threshold = y_min + (r / height) * y_range
        row = f"{int(threshold):>3} │ "
        for s in scores:
            if s >= threshold:
                row += "[bold yellow]█  [/]"
            elif s >= threshold - (y_range/height):
                 row += "[yellow]▄  [/]"
            else:
                row += "   "
        chart.append(row)
    
    chart.append("    └" + "───" * len(years))
    year_row = "      "
    for y in years:
        year_row += f"{str(y)[2:]} "
    chart.append(year_row)
    
    return "\n".join(chart)

class ChartWidget(Static):
    """Widget to display the large ASCII chart."""
    pass

class TirageSearchApp(App):
    """TUI with fixed selection logic, cleaned HC mentions and ASCII chart."""
    
    TITLE = "Résultats Tirage Payerne"
    BINDINGS = [
        ("q", "quit", "Quitter"),
        ("f", "focus_input", "Rechercher"),
    ]
    
    CSS = """
    Screen { background: #1e1e1e; }
    #search_container { height: auto; margin: 1 2; }
    #input_label { padding: 0 1; color: #f1c40f; text-style: bold; }
    Input { width: 100%; border: solid #f1c40f; background: #2d2d2d; }
    #main_layout { height: 1fr; }
    TabbedContent { height: 1fr; }
    DataTable { height: 1fr; background: #252525; }
    #chart_pane {
        height: 18;
        background: #121212;
        border-top: solid #34495e;
        padding: 1 4;
        color: white;
    }
    Footer { background: #2c3e50; color: white; }
    """

    def __init__(self):
        super().__init__()
        self.all_records = []
        self.load_data_to_memory()

    def load_data_to_memory(self):
        if not os.path.exists(CSV_FILE): return
        try:
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                raw_records = list(csv.DictReader(f))
            
            self.all_records = []
            hc_pattern = re.compile(r'HC\d{4}[A-Z]?', re.IGNORECASE)

            for row in raw_records:
                name = row.get('Nom et prénom', '').strip()
                year = row.get('Année', '').strip()
                st = row.get('Type de tir', '').upper()
                res_str = row.get('Résultat', '').strip()
                tires = row.get('Tires', '').strip()
                
                if not name or not year: continue
                
                # Extract HC from name or tires
                hc_mention = ""
                match = hc_pattern.search(name)
                if match:
                    hc_mention = match.group(0).upper()
                    name = hc_pattern.sub('', name).strip()
                
                if not hc_mention:
                    match = hc_pattern.search(tires)
                    if match:
                        hc_mention = match.group(0).upper()
                        tires = hc_pattern.sub('', tires).strip()

                # Clean name from common prefixes
                name = re.sub(r'^(Roi du Tir|[\d\.]+\s+Couronne)\s+', '', name, flags=re.IGNORECASE).strip()
                
                self.all_records.append({
                    'Année': year,
                    'Type de tir': st,
                    'Nom et prénom': name,
                    'Résultat': res_str,
                    'Tires': tires,
                    'Hors concours': hc_mention,
                    'Classement': row.get('Classement', '')
                })
        except: pass

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="search_container"):
            yield Static("Rechercher un tireur :", id="input_label")
            yield Input(placeholder="Tapez un nom...", id="search_input")
        
        with Vertical(id="main_layout"):
            with TabbedContent():
                for key, config in SHOOT_TYPES.items():
                    with TabPane(config["label"], id=f"tab_{key}"):
                        yield DataTable(id=f"table_{key}")
                with TabPane("Autres", id="tab_AUTRES"):
                    yield DataTable(id="table_AUTRES")
            
            yield ChartWidget(id="chart_pane")
            
        yield Footer()

    def on_mount(self) -> None:
        for key in list(SHOOT_TYPES.keys()) + ["AUTRES"]:
            table = self.query_one(f"#table_{key}", DataTable)
            table.add_columns("Année", "Rang", "Nom", "Résultat", "Détails", "HC")
            table.cursor_type = "row"
            table.zebra_stripes = True
        self.query_one(Input).focus()
        self.filter_data("")

    def action_focus_input(self) -> None:
        self.query_one(Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_data(event.value.strip())

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        try:
            table = event.data_table
            if event.cursor_row < table.row_count:
                row = table.get_row_at(event.cursor_row)
                if row and len(row) > 2:
                    self.update_large_chart(row[2])
        except Exception: pass

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        self.call_after_refresh(self.auto_update_chart)

    def filter_data(self, search_term: str) -> None:
        search_term = search_term.lower()
        categorized = {k: [] for k in SHOOT_TYPES.keys()}
        categorized["AUTRES"] = []
        
        for row in self.all_records:
            name = row.get('Nom et prénom', '')
            if not search_term or search_term in name.lower():
                st = row.get('Type de tir', '').upper()
                cat = "AUTRES"
                for k in SHOOT_TYPES.keys():
                    if k in st: cat = k; break
                categorized[cat].append((
                    row.get('Année', ''), row.get('Classement', ''), name,
                    row.get('Résultat', ''), row.get('Tires', ''), row.get('Hors concours', '')
                ))

        for key in list(SHOOT_TYPES.keys()) + ["AUTRES"]:
            table = self.query_one(f"#table_{key}", DataTable)
            rows = categorized[key]
            def sort_key(x):
                try: r = int(x[1])
                except: r = 999999
                return (x[0], -r)
            rows.sort(key=sort_key, reverse=True)
            table.clear()
            table.add_rows(rows[:200])
        
        self.auto_update_chart()

    def auto_update_chart(self):
        try:
            tab_id = self.query_one(TabbedContent).active
            if not tab_id: return
            cat_key = tab_id.replace("tab_", "")
            table = self.query_one(f"#table_{cat_key}", DataTable)
            
            if table.row_count > 0:
                cursor_row = table.cursor_row
                if cursor_row < table.row_count:
                    row = table.get_row_at(cursor_row)
                    if row: self.update_large_chart(row[2])
                else:
                    row = table.get_row_at(0)
                    if row: self.update_large_chart(row[2])
            else:
                self.query_one(ChartWidget).update("[i]Aucun résultat pour cette catégorie[/i]")
        except Exception: pass

    def update_large_chart(self, name):
        if not name: return
        tab_id = self.query_one(TabbedContent).active
        category = tab_id.replace("tab_", "")
        
        history = []
        name_lower = name.lower().strip()
        
        for row in self.all_records:
            row_name = row.get('Nom et prénom', '').lower().strip()
            if row_name == name_lower:
                st = row.get('Type de tir', '').upper()
                match_cat = (category == "AUTRES") or (category in st)
                
                if match_cat:
                    res_str = row.get('Résultat', '')
                    nums = re.findall(r'\d+', res_str)
                    if nums:
                        try: history.append((int(row.get('Année')), int(nums[0])))
                        except: pass
        
        if not history:
            self.query_one(ChartWidget).update(f"[i]Pas d'historique trouvé pour {name} en {category}[/i]")
        else:
            chart_text = render_ascii_chart(history, title=f"Historique: {name} ({category})")
            self.query_one(ChartWidget).update(chart_text)

if __name__ == "__main__":
    TirageSearchApp().run()
