def standard_stats(export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    # URL
    url = 'https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content)

    # Drop top header
    df[1].columns = df[1].columns.droplevel(0)

    # Cleaning
    dfdata = df[1]
    dfstandard = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

    # Convert string to float
    numeric_cols = ['90s', 'Gls', 'Ast', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR',
                    'G+A', 'G+A-PK', 'xG', 'npxG', 'npxG+xAG', 'xG+xAG']
    dfstandard[numeric_cols] = dfstandard[numeric_cols].astype(float)

    # Handle duplicate column names
    def rename_duplicates(columns, target_col):
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    for col in ['Gls', 'Ast', 'G-PK', 'xG', 'npxG', 'xA', 'npxG+xA', 'G+A', 'xAG', 'npxG+xAG']:
        dfstandard.columns = rename_duplicates(dfstandard.columns, col)

    # Clean additional columns
    dfstandard['PlSqu'] = dfstandard['Player'] + dfstandard['Squad']
    dfstandard['Player'] = dfstandard['Player'].apply(unidecode)
    dfstandard['Squad'] = dfstandard['Squad'].apply(unidecode)
    dfstandard.drop(columns='Matches', inplace=True)

    # Renaming columns
    dfstandard.columns = [
        col.replace('_1', '') if '_1' in col else
        col.replace('_2', '_p90') if '_2' in col else
        col + '_p90' if col in ['G+A-PK', 'xG+xAG'] else
        col
        for col in dfstandard.columns
    ]

    # Decide si exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'fbrefBig5standard.csv'
        dfstandard.to_csv(file_path, encoding='utf-8', index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'fbrefBig5standard.xlsx'
        dfstandard.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfstandard
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def shooting_stats(export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    # URL
    url = 'https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content)
    
    # Clean the age columns
    df[1].columns = df[1].columns.droplevel(0)  # Drop top header row
    dfdata = df[1]
    dfshoot = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)
    
    # Convert to strings and to float
    numeric_cols = ['90s', 'Gls', 'Sh', 'SoT', 'SoT%', 'Sh/90', 'SoT/90', 'G/Sh', 
                    'G/SoT', 'Dist', 'FK', 'PK', 'PKatt', 'xG', 'npxG', 
                    'npxG/Sh', 'G-xG', 'np:G-xG']
    dfshoot[numeric_cols] = dfshoot[numeric_cols].astype(float)

    # Drop Matches column
    dfshoot.drop(columns='Matches', inplace=True)
    
    # Key and final touches
    dfshoot['PlSqu'] = dfshoot['Player'] + dfshoot['Squad']
    dfshoot['Player'] = dfshoot['Player'].apply(unidecode)
    dfshoot['Squad'] = dfshoot['Squad'].apply(unidecode)

    # Decide si exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'fbrefBig5Shoot.csv'
        dfshoot.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'fbrefBig5Shoot.xlsx'
        dfshoot.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfshoot
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def possession_stats(export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    # URL
    url = 'https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content)

    # Clean the top header row
    df[1].columns = df[1].columns.droplevel(0)
    dfdata = df[1]
    dfpossession = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

    # Convert to numeric
    numeric_cols = ['90s', 'Touches', 'Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att Pen', 'Live',
                    'Succ', 'Att', 'Succ%', 'Carries', 'TotDist', 'PrgDist', '1/3', 'CPA', 'Mis',
                    'Dis', 'Rec']
    dfpossession[numeric_cols] = dfpossession[numeric_cols].astype(float)

    # Rename duplicate columns for "Prog"
    cols = []
    count = 1
    for column in dfpossession.columns:
        if column == 'Prog':
            cols.append(f'Prog_{count}')
            count += 1
        else:
            cols.append(column)
    dfpossession.columns = cols

    # Clean data
    dfpossession['PlSqu'] = dfpossession['Player'] + dfpossession['Squad']
    dfpossession['Player'] = dfpossession['Player'].apply(unidecode)
    dfpossession['Squad'] = dfpossession['Squad'].apply(unidecode)

    # Drop Matches column
    dfpossession.drop(columns='Matches', inplace=True)

    # Decide si exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'fbrefBig5Possession.csv'
        dfpossession.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'fbrefBig5Possession.xlsx'
        dfpossession.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfpossession
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def creation_stats(export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    # URL
    url = 'https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content)

    # Clean the top header row
    df[1].columns = df[1].columns.droplevel(0)
    dfdata = df[1]
    dfcreation = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

    # Convert numeric columns to float
    numeric_cols = ['90s', 'SCA', 'PassLive', 'PassDead', 'Sh', 'Fld', 'Def', 'GCA']
    dfcreation[numeric_cols] = dfcreation[numeric_cols].astype(float)

    # Rename duplicate columns
    def rename_duplicates(columns, target_col, suffix):
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{suffix}{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    # Rename specific columns
    for col, suffix in [('PassLive', ''), ('PassDead', ''), ('Drib', ''), ('Sh', ''), ('Fld', ''), ('Def', '')]:
        dfcreation.columns = rename_duplicates(dfcreation.columns, col, suffix)

    # Adjust column names for SCA and GCA
    dfcreation.columns = [
        col.replace('_1', '_SCA') if '_1' in col else
        col.replace('_2', '_GCA') if '_2' in col else
        col
        for col in dfcreation.columns
    ]

    # Clean data
    dfcreation.drop(columns='Matches', inplace=True)
    dfcreation['PlSqu'] = dfcreation['Player'] + dfcreation['Squad']
    dfcreation['Player'] = dfcreation['Player'].apply(unidecode)
    dfcreation['Squad'] = dfcreation['Squad'].apply(unidecode)

    # Decide si exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'fbrefBig5Creation.csv'
        dfcreation.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'fbrefBig5Creation.xlsx'
        dfcreation.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfcreation
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def defense_stats(export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    # URL
    url = 'https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content)

    # Clean the top header row
    df[1].columns = df[1].columns.droplevel(0)
    dfdata = df[1]
    dfdefense = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

    # Convert numeric columns to float
    numeric_cols = ['90s', 'Tkl', 'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att', 
                    'Tkl%', 'Blocks', 'Sh', 'Pass', 'Int', 'Tkl+Int', 'Clr', 'Err']
    dfdefense[numeric_cols] = dfdefense[numeric_cols].astype(float)

    # Rename duplicate columns
    def rename_duplicates(columns, target_col, suffix):
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{suffix}{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    # Rename specific columns
    for col, suffix in [('Def 3rd', ''), ('Mid 3rd', ''), ('Att 3rd', ''), ('Tkl', '')]:
        dfdefense.columns = rename_duplicates(dfdefense.columns, col, suffix)

    # Adjust column names for Tackle and Challenge
    dfdefense.columns = [
        col.replace('_1', '_tackles') if '_1' in col else
        col.replace('_2', '_challenges') if '_2' in col else
        col
        for col in dfdefense.columns
    ]

    # Clean data
    dfdefense.drop(columns='Matches', inplace=True)
    dfdefense['PlSqu'] = dfdefense['Player'] + dfdefense['Squad']
    dfdefense['Player'] = dfdefense['Player'].apply(unidecode)
    dfdefense['Squad'] = dfdefense['Squad'].apply(unidecode)

    # Decide si exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'fbrefBig5Defense.csv'
        dfdefense.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'fbrefBig5Defense.xlsx'
        dfdefense.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfdefense
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def passing_stats(export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    # URL
    url = 'https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content)

    # Clean the top header row
    df[1].columns = df[1].columns.droplevel(0)
    dfdata = df[1]
    dfPassing = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

    # Convert numeric columns to float
    numeric_cols = ['90s', 'Cmp', 'Att', 'Cmp%', 'TotDist', 'PrgDist', 'Ast', 'xA',
                    'KP', '1/3', 'PPA', 'CrsPA']
    dfPassing[numeric_cols] = dfPassing[numeric_cols].astype(float)

    # Rename duplicate columns
    def rename_duplicates(columns, target_col, suffix):
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{suffix}{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    # Rename specific columns
    for col, suffix in [('Cmp', ''), ('Att', ''), ('Cmp%', '')]:
        dfPassing.columns = rename_duplicates(dfPassing.columns, col, suffix)

    # Rename other columns with suffixes for different pass lengths
    dfPassing.columns = [
        col.replace('_1', '') if '_1' in col else
        col.replace('_2', '_short') if '_2' in col else
        col.replace('_3', '_medium') if '_3' in col else
        col.replace('_4', '_long') if '_4' in col else
        col
        for col in dfPassing.columns
    ]

    # Clean data
    dfPassing.drop(columns='Matches', inplace=True)
    dfPassing['PlSqu'] = dfPassing['Player'] + dfPassing['Squad']
    dfPassing['Player'] = dfPassing['Player'].apply(unidecode)
    dfPassing['Squad'] = dfPassing['Squad'].apply(unidecode)

    # Decide si exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'fbrefBig5Passing.csv'
        dfPassing.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'fbrefBig5Passing.xlsx'
        dfPassing.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfPassing
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def passing_type_stats(export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    # URL
    url = 'https://fbref.com/en/comps/Big5/passing_types/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content)

    # Clean the top header row
    df[1].columns = df[1].columns.droplevel(0)
    dfdata = df[1]
    dfpassingtypes = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

    # Convert numeric columns to float
    numeric_cols = ['90s', 'Att', 'Live', 'Dead', 'FK', 'TB', 'Sw', 'Crs', 'CK',
                    'In', 'Out', 'Str', 'TI', 'Cmp', 'Off', 'Blocks']
    dfpassingtypes[numeric_cols] = dfpassingtypes[numeric_cols].astype(float)

    # Rename duplicate columns
    def rename_duplicates(columns, target_col, suffix):
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{suffix}{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    # Rename specific columns
    dfpassingtypes.columns = rename_duplicates(dfpassingtypes.columns, 'Out', '')

    # Drop the Matches column
    dfpassingtypes.drop(columns='Matches', inplace=True)

    # Concatenate Player and Squad columns
    dfpassingtypes['PlSqu'] = dfpassingtypes['Player'] + dfpassingtypes['Squad']
    dfpassingtypes['Player'] = dfpassingtypes['Player'].apply(unidecode)
    dfpassingtypes['Squad'] = dfpassingtypes['Squad'].apply(unidecode)

    # Decide si exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'fbrefBig5PassingType.csv'
        dfpassingtypes.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'fbrefBig5PassingType.xlsx'
        dfpassingtypes.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfpassingtypes
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def playing_time_stats(export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    # URL
    url = 'https://fbref.com/en/comps/Big5/playingtime/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content, encoding='utf-8')

    # Clean the top header row and fill NaN values with 0
    df[0].columns = df[0].columns.droplevel(0)
    df[0] = df[0].fillna(0)
    dfdata = df[0]
    dfplayingtime = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

    # Convert numeric columns to float
    numeric_cols = ['90s', 'Starts', 'Mn/Start', 'Compl', 'Subs', 'Mn/Sub', 'unSub',
                    'PPM', 'onG', 'onGA', '+/-', '+/-90', 'On-Off', 'onxG', 'onxGA',
                    'xG+/-', 'xG+/-90']
    dfplayingtime[numeric_cols] = dfplayingtime[numeric_cols].astype(float)

    # Rename duplicate columns
    def rename_duplicates(columns, target_col, suffix):
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{suffix}{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    # Rename specific columns
    dfplayingtime.columns = rename_duplicates(dfplayingtime.columns, 'On-Off', '')

    # Drop the Matches column
    dfplayingtime.drop(columns='Matches', inplace=True)

    # Concatenate Player and Squad columns
    dfplayingtime['PlSqu'] = dfplayingtime['Player'] + dfplayingtime['Squad']
    dfplayingtime['Player'] = dfplayingtime['Player'].apply(unidecode)
    dfplayingtime['Squad'] = dfplayingtime['Squad'].apply(unidecode)

    # Decide si exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'fbrefBig5PlayingTime.csv'
        dfplayingtime.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'fbrefBig5PlayingTime.xlsx'
        dfplayingtime.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfplayingtime
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def scrape_all_stats(export_format=None, return_dfs=False):
    # Lista para almacenar DataFrames si es necesario
    dfs = []

    # Funciones de scraping
    print("Starting to scrape shooting stats...")
    if return_dfs:
        dfs.append(shooting_stats(return_df=True))
    else:
        shooting_stats(export_format)

    print("Starting to scrape defense stats...")
    if return_dfs:
        dfs.append(defense_stats(return_df=True))
    else:
        defense_stats(export_format)

    print("Starting to scrape passing stats...")
    if return_dfs:
        dfs.append(passing_stats(return_df=True))
    else:
        passing_stats(export_format)

    print("Starting to scrape passing type stats...")
    if return_dfs:
        dfs.append(passing_type_stats(return_df=True))
    else:
        passing_type_stats(export_format)

    print("Starting to scrape playing time stats...")
    if return_dfs:
        dfs.append(playing_time_stats(return_df=True))
    else:
        playing_time_stats(export_format)

    print("Starting to scrape standard stats...")
    if return_dfs:
        dfs.append(standard_stats(return_df=True))
    else:
        standard_stats(export_format)

    print("Starting to scrape possession stats...")
    if return_dfs:
        dfs.append(possession_stats(return_df=True))
    else:
        possession_stats(export_format)

    print("Starting to scrape creation stats...")
    if return_dfs:
        dfs.append(creation_stats(return_df=True))
    else:
        creation_stats(export_format)

    print("All stats have been scraped and saved.")

    # Devuelve la lista de DataFrames si se solicita
    if return_dfs:
        return dfs


def merger_5leagues(export_format=None, return_df=False):
    import pandas as pd
    import os

    # Leer DataFrames usando las funciones de scraping
    player_stand_stats = standard_stats(return_df=True)
    player_shoot_stats = shooting_stats(return_df=True)
    player_pass_stats = passing_stats(return_df=True)
    player_passtypes_stats = passing_type_stats(return_df=True)
    player_ga_stats = creation_stats(return_df=True)
    player_defense_stats = defense_stats(return_df=True)
    player_possession_stats = possession_stats(return_df=True)
    player_time_stats = playing_time_stats(return_df=True)

    # Unión de player_stand_stats con player_shoot_stats
    merged_df = pd.merge(
        player_stand_stats,
        player_shoot_stats,
        on='PlSqu',
        how='inner',
        suffixes=('_stand', '_shoot')
    )

    # Eliminar columnas duplicadas y ajustar nombres de columnas
    columns_to_drop = [col for col in merged_df.columns if col.endswith('_shoot') and col[:-6] in player_stand_stats.columns]
    merged_df = merged_df.drop(columns=columns_to_drop)
    merged_df.columns = [col.replace('_stand', '') for col in merged_df.columns]

    # Agregar player_pass_stats
    final_merged_df = pd.merge(
        merged_df,
        player_pass_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_passing')
    )
    columns_to_drop = [col for col in final_merged_df.columns if col.endswith('_passing') and col[:-8] in merged_df.columns]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    # Agregar player_ga_stats
    final_merged_df = pd.merge(
        final_merged_df,
        player_ga_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_ga')
    )
    columns_to_drop = [col for col in final_merged_df.columns if col.endswith('_ga') and col[:-3] in final_merged_df.columns]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    # Agregar player_defense_stats
    final_merged_df = pd.merge(
        final_merged_df,
        player_defense_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_defense')
    )
    columns_to_drop = [col for col in final_merged_df.columns if col.endswith('_defense') and col[:-8] in final_merged_df.columns]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    # Agregar player_possession_stats
    final_merged_df = pd.merge(
        final_merged_df,
        player_possession_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_possession')
    )
    columns_to_drop = [col for col in final_merged_df.columns if col.endswith('_possession') and col[:-11] in final_merged_df.columns]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    # Agregar player_time_stats
    final_merged_df = pd.merge(
        final_merged_df,
        player_time_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_time')
    )
    columns_to_drop = [col for col in final_merged_df.columns if col.endswith('_time') and col[:-5] in final_merged_df.columns]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    # Exportar o devolver el DataFrame
    if export_format == 'csv':
        file_path = 'final_fbref_all5_columns.csv'
        final_merged_df.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = 'final_fbref_all5_columns.xlsx'
        final_merged_df.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return final_merged_df
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")

