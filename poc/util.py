# Reimport libraries and redefine data after kernel reset
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np

lithologias = [
  {
    "key": "GLI",
    "name": "Gnaisse Leucocrático Intemperizado",
    "color": "#d9d9d9",
    "pattern": "////"
  },
  {
    "key": "CC",
    "name": "Concreção Carbonática",
    "color": "#b3b3b3",
    "pattern": "..."
  },
  {
    "key": "FLD",
    "name": "Filito Destroçado",
    "color": "#a67c52",
    "pattern": "\\\\\\"
  },
  {
    "key": "SR",
    "name": "Solo Residual",
    "color": "#f4e19c",
    "pattern": None
  },
  {
    "key": "MAF",
    "name": "Rochas Máficas (Basalto ou Gabro)",
    "color": "#4d4d4d",
    "pattern": "xxx"
  },
  {
    "key": "SV",
    "name": "Saprolito Vesicular",
    "color": "#c2b280",
    "pattern": "+++"
  },
  {
    "key": "CCI",
    "name": "Concreção Carbonática Intemperizada",
    "color": "#cccccc",
    "pattern": "..."
  },
  {
    "key": "FC",
    "name": "Filito com Carbonato",
    "color": "#8c7853",
    "pattern": "|||"
  }
]

@dataclass
class LithMeta:
    key: str
    name: str
    color: str
    pattern: str

def create_lith_dict():
    liths: dict[str, LithMeta] = {}
    for lith in lithologias:
        key = lith['key']
        name = lith['name']
        color = lith['color']
        pattern = lith['pattern']
        liths[key] = LithMeta(key, name, color, pattern)
    return liths


thresholds = {"P2O5": 4.0, "Fe2O3": 3.0}

# Redefine the function
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from typing import List, Dict, Optional

def plot_multi_analyte_log_with_analysis(
    layers: List[Dict],
    assay_data: pd.DataFrame,
    analytes_with_thresholds: Optional[Dict[str, float]] = None,
    analysis_methods: Optional[List[str]] = None
) -> plt.Figure: # type: ignore
    analytes_with_thresholds = analytes_with_thresholds or {}
    analysis_methods = analysis_methods or []

    if "cutoff" in analysis_methods and not analytes_with_thresholds:
        raise ValueError("Cutoff analysis requires analytes_with_thresholds.")
    if analytes_with_thresholds and "cutoff" not in analysis_methods:
        raise ValueError("analytes_with_thresholds provided but 'cutoff' not in analysis_methods.")

    num_columns = 1 + len(analytes_with_thresholds)
    fig, axes = plt.subplots(1, num_columns, figsize=(2.5 * num_columns, 8), sharey=True,
                             gridspec_kw={"width_ratios": [1] + [1]*len(analytes_with_thresholds)})
    if num_columns == 1:
        axes = [axes]  # wrap single Axes object in a list
        
    lith_ax = axes[0]

    max_depth = max(layer["to"] for layer in layers)

    # Lithology plot
    for layer in layers:
        height = layer["to"] - layer["from"]
        lith_ax.add_patch(
            patches.Rectangle((0, layer["from"]), 1, height,
                              facecolor=layer["color"],
                              hatch=layer["pattern"],
                              edgecolor="black")
        )
        lith_ax.text(1.05, layer["from"] + height / 2, layer["lith"],
                     va='center', ha='left', fontsize=10, weight="bold")
        lith_ax.text(0.5, layer["from"] + height / 2, f"{height:.2f} m",
                     va='center', ha='center', fontsize=8, color="black", style="italic")

    lith_ax.set_ylim(max_depth, 0)
    lith_ax.set_xlim(0, 1.8)
    lith_ax.set_xticks([])
    lith_ax.set_yticks([layer["from"] for layer in layers] + [max_depth])
    lith_ax.set_ylabel("Cota (m)")
    lith_ax.set_title("Furo")

    for i, (analyte, threshold) in enumerate(analytes_with_thresholds.items()):
        ax = axes[i + 1]
        from_vals = assay_data["from"]
        to_vals = assay_data["to"]
        midpoints = [(f + t) / 2 for f, t in zip(from_vals, to_vals)]
        values = assay_data[analyte].values

        ax.plot(values, midpoints, color="black", linewidth=1.5)
        ax.set_xlabel(f"{analyte}")
        ax.set_xlim(0, max(max(values) * 1.2, threshold * 1.2))
        ax.grid(True)
        ax.set_title(f"{analyte}")
        ax.set_ylim(max_depth, 0)

        if "cutoff" in analysis_methods:
            ax.axvline(x=threshold, color="red", linestyle="--", label=f"Cut-off {threshold}")
            for f, t, v in zip(from_vals, to_vals, values):
                if v > threshold:
                    ax.fill_betweenx([f, t], 0, v, color="orange", alpha=0.3)

        if "zscore" in analysis_methods:
            mean = np.mean(values) # type: ignore
            std = np.std(values) # type: ignore
            z_scores = (values - mean) / std
            for f, t, z, v in zip(from_vals, to_vals, z_scores, values):
                if abs(z) > 2:
                    ax.fill_betweenx([f, t], 0, v, color="purple", alpha=0.2)

        if "percentile" in analysis_methods:
            p90 = np.percentile(values, 90) # type: ignore
            ax.axvline(x=p90, color="blue", linestyle=":", label="P90")
            for f, t, v in zip(from_vals, to_vals, values):
                if v > p90:
                    ax.fill_betweenx([f, t], 0, v, color="blue", alpha=0.2)

        if "iqr" in analysis_methods:
            q1 = np.percentile(values, 25) # type: ignore
            q3 = np.percentile(values, 75) # type: ignore
            iqr = q3 - q1
            upper = q3 + 1.5 * iqr
            ax.axvline(x=upper, color="green", linestyle="-.", label="IQR high")
            for f, t, v in zip(from_vals, to_vals, values):
                if v > upper:
                    ax.fill_betweenx([f, t], 0, v, color="green", alpha=0.2)

        ax.legend()

    plt.tight_layout()
    return fig

'''
# Sample data
layers = [
    {"from": 0.0, "to": 4.5, "lith": "Laterita fosfática", "color": "#fdd835", "pattern": None},
    {"from": 4.5, "to": 12.0, "lith": "Siltito fosfático", "color": "#e0e0e0", "pattern": "///"},
    {"from": 12.0, "to": 18.0, "lith": "Basalto alterado", "color": "#8d4a26", "pattern": None},
]
'''

def create_plot_layer(_from: float, _to: float, analyte: str):
    lith_meta = create_lith_dict()
    meta = lith_meta.get(analyte)
    color = 'white'
    pattern = None
    name = analyte
    if isinstance(meta, LithMeta):
        color = meta.color
        pattern = meta.pattern
        name = analyte #meta.name
    return {
        "from": _from,
        "to": _to,
        "lith": name,
        "color": color,
        "pattern": pattern
    }

def create_assay_data(_from: list[float], _to: list[float], analytes: dict[str, list[float]]):
    data = {
        "from": _from,
        "to":   _to,
        **analytes
    }    
    return pd.DataFrame(data)

'''
# Generate the plot
fig = plot_multi_analyte_log_with_analysis(
    [],
    assay_data,
    thresholds,
    analysis_methods=["cutoff", "zscore", "percentile", "iqr"]
)
plt.show()

'''