from dataclasses import dataclass
from typing import Self
from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path

from util import create_assay_data, create_plot_layer, plot_multi_analyte_log_with_analysis

@dataclass
class ColTitle:
    name: str
    method: str
    unit: str
    
    @property
    def key(self):
        sufix = f'__{self.method.lower()}' if self.method else ''
        return f'{self.name.lower()}{sufix}'

    @property
    def is_analyte(self):
        return bool(self.unit)
    
    @property
    def friendly_name(self):
        method = self.method[:3]
        return f'{self.name} ({self.unit}) [{method}]'
    
class LabHeaders:
    def __init__(self) -> None:
        self.__cols: dict[str, ColTitle] = {}
        
    def add_col_title(self, col: ColTitle):
        if col.key not in self.__cols:
            self.__cols[col.key] = col
    
    def __getitem__(self, key: str):
        if key in self.__cols:
            return self.__cols[key]
        return None
    
    def __iter__(self):
        for _, col in self.__cols.items():
            yield col
            
    def __add__(self, other: Self):
        if not isinstance(other, self.__class__):
            raise ValueError('Instances is not of the same type')
        for col in other:
            self.add_col_title(col)
        return self
            

def merge_lab_with_geology(geology_df: pd.DataFrame, lab_df: pd.DataFrame) -> pd.DataFrame:
    geology_df = geology_df.copy()
    lab_df = lab_df.copy()

    geology_df['from'] = geology_df['from'].astype(float)
    geology_df['to'] = geology_df['to'].astype(float)
    lab_df['sample_from'] = lab_df['sample_from'].astype(float)
    lab_df['sample_to'] = lab_df['sample_to'].astype(float)

    # Prepare output list
    merged_records = []

    for _, sample_row in lab_df.iterrows(): # type: ignore
        match = geology_df[ # type: ignore
            (geology_df['hole_number'] == sample_row['hole_number']) &
            (geology_df['from'] <= sample_row['sample_from']) &
            (geology_df['to'] >= sample_row['sample_to'])
        ]

        if not match.empty:
            litho_info = match.iloc[0]
        else:
            overlapping = geology_df[
                (geology_df['hole_number'] == sample_row['hole_number']) &
                (geology_df['to'] > sample_row['sample_from']) &
                (geology_df['from'] < sample_row['sample_to'])
            ]

            if not overlapping.empty:
                litho_info = overlapping.iloc[0].copy()
                litho_info['lithology'] = '+'.join(overlapping['lithology'].unique())
            else:
                # No matching or overlapping lithology found
                litho_info = pd.Series({
                    'from': None,
                    'to': None,
                    'lithology': None
                })

        if 'hole_number' in litho_info:
            litho_info = litho_info.drop(['hole_number'])

        merged_row = pd.concat([sample_row, litho_info])

        merged_records.append(merged_row)

    return pd.DataFrame(merged_records)

 
def load_and_concat_csvs(
    directory: str
) -> tuple[pd.DataFrame, LabHeaders]:
    csv_files = Path(directory).glob("*.csv")
    row_header_index = 7
    row_header_n = 3
    
    def __make_header(df: pd.DataFrame):
        columns_info = LabHeaders()
        for col in df.columns:
            one, two, three = df[col].fillna('').astype(str) # type: ignore
            one = '-'.join(one.strip().split(' '))
            two = '-'.join(two.strip().split(' '))
            three = '-'.join(three.strip().split(' '))
            name = two if two else one
            method = one if two else ''
            unit = three if three else ''
            columns_info.add_col_title(ColTitle(name=name, method=method, unit=unit))
        return columns_info
            
    dataframes: list[pd.DataFrame] = []        
    row_content_index = 10
    super_headers = LabHeaders()
    for file in csv_files:
        header_data = pd.read_csv(file, header=None, skiprows=row_header_index, nrows=row_header_n, index_col=False) # type: ignore
        cols_title = __make_header(header_data)
        titles = [col.key for col in cols_title]
        data = pd.read_csv(file, names=titles, skiprows=row_content_index) # type: ignore
        data['__file__'] = file
        dataframes.append(data)
        super_headers = super_headers + cols_title
    df = pd.concat(dataframes).reset_index(drop=True)
    return df, super_headers
    
def join_sample_lab(sample: pd.DataFrame, lab: pd.DataFrame):
    lab.rename(columns={'sample-id': 'sample_code'}, inplace=True)
    #Just SMP metters for this analysis...
    lab = lab[lab['type'] == 'SMP'].reset_index(drop=True)
    df_merge = sample.merge(lab, on='sample_code', how='left')
    return df_merge


def create_plot(df: pd.DataFrame, headers: LabHeaders, hole_number: str):
    df_hole = df[df['hole_number'] == hole_number].reset_index(drop=True)
    ## Create the lithology layers
    columns_lith = ['lithology', 'from', 'to']
    lith_df = df_hole[columns_lith]
    layers = []
    for _, row in lith_df.iterrows():
        _from = row['from']
        if not pd.isna(_from):
            layers.append(create_plot_layer(_from, row['to'], row['lithology']))
    
    analytes: dict[str, list[float]] = {}
    for col in headers:
        if not col.is_analyte:
            continue
        col_data = df_hole[col.key]
        ## remove that -99999...
        analytes[col.friendly_name] = list(col_data.fillna(0).apply(lambda x: max(x, 0)))
    print('ANALY', analytes)
    data = create_assay_data(list(df_hole['sample_from']), list(df_hole['sample_to']), analytes)
    data = data.dropna(subset=['from', 'to'])
    
    print('DATA', data)
    print('Layers', layers)
    
    fig = plot_multi_analyte_log_with_analysis(
        layers,
        data, 
        analytes_with_thresholds= {'Al2O3 (%) [ICP]': 23, 'Ba (ppm) [ICP]': 4500},  
        analysis_methods=["cutoff", "zscore", "percentile", "iqr"]
    )
    fig.savefig("output.png", dpi=300, bbox_inches="tight")
    

def main():
    geology_df_plan = pd.read_csv('./campo_data/DH_geology.csv') # type: ignore
    interest_columns = {
        'Hole number': 'hole_number',
        'From': 'from',
        'To': 'to',
        'LITOLOGIA': 'lithology'
    }
    geology_df = geology_df_plan[interest_columns.keys()].rename(columns=interest_columns)
    
    sample_df_plan = pd.read_csv('./campo_data/DH_sample.csv') # type: ignore
    interest_sample_columns = {
        'Hole number': 'hole_number',
        'From': 'sample_from',
        'To': 'sample_to',
        'COD_AMOSTRA': 'sample_code',
        'TIPO_AMOSTRA': 'sample_type',
        'TIPO_CONTROLE': 'control_type',
        'parent sample number': 'parent_code'
    }
    sample_df = sample_df_plan[interest_sample_columns.keys()].rename(columns=interest_sample_columns)
    #print(sample_df.control_type.value_counts())
    
    labs_df, cols_title = load_and_concat_csvs('./lab')
    
    ## Join sample_df and labs_df
    results_df = join_sample_lab(sample_df, labs_df)
    
    ## I'M GONNA SKIP THE LAB EVALUATION AND GO STRAIGHT TO THE REPORT
    
    # merge result_df and geology
    final_df = merge_lab_with_geology(geology_df, results_df)
    print(final_df.head())
    
    create_plot(final_df, cols_title, 'MN-AC-0001')

if __name__ == '__main__':
    main()