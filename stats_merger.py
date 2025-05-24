from datetime import datetime # Import needed for the helper function

def _get_season_string(start_year=None):
    """
    Determina la cadena de la temporada basada en el start_year.
    Ejemplo: Para start_year=2022, devuelve "2022-2023".
    Si start_year es None, por defecto usa la temporada que comenzó el año calendario anterior.
    """
    if start_year is None:
        year_to_use = datetime.now().year - 1
    else:
        try:
            year_to_use = int(start_year)
        except ValueError:
            #Fallback al año anterior si start_year no es un entero válido
            print(f"Advertencia: start_year ('{start_year}') no es válido. Usando {datetime.now().year - 1} por defecto.")
            year_to_use = datetime.now().year - 1
    return f"{year_to_use}-{year_to_use + 1}"

def standard_stats(start_year=None, export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/stats/players/{season}-Big-5-European-Leagues-Stats'

    try:
        df = pd.read_html(url)[0]  # Lee la primera tabla de la página
    except Exception as e:
        print(f"Error al leer datos de {url}: {e}")
        if return_df:
            return pd.DataFrame() # Devuelve DataFrame vacío en caso de error
        else:
            return

    # Drop top header
    df.columns = df.columns.droplevel(0)

    # Cleaning
    dfstandard = df[df['Player'] != 'Player'].copy() # Usar .copy() para evitar SettingWithCopyWarning

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
    dfstandard.loc[:, 'PlSqu'] = dfstandard['Player'] + dfstandard['Squad']
    dfstandard.loc[:, 'Player'] = dfstandard['Player'].apply(unidecode)
    dfstandard.loc[:, 'Squad'] = dfstandard['Squad'].apply(unidecode)
    if 'Matches' in dfstandard.columns:
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
        file_path = f'fbrefBig5standard_{season}.csv' # Nombre de archivo con temporada
        dfstandard.to_csv(file_path, encoding='utf-8', index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'fbrefBig5standard_{season}.xlsx' # Nombre de archivo con temporada
        dfstandard.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfstandard
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def shooting_stats(start_year=None, export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/shooting/players/{season}-Big-5-European-Leagues-Stats'

    try:
        df = pd.read_html(url)[0]
    except Exception as e:
        print(f"Error al leer datos de {url}: {e}")
        if return_df:
            return pd.DataFrame()
        else:
            return

    df.columns = df.columns.droplevel(0)
    dfshoot = df[df['Player'] != 'Player'].copy()

    if 'Matches' in dfshoot.columns:
        dfshoot.drop(columns='Matches', inplace=True)

    dfshoot.loc[:, 'PlSqu'] = dfshoot['Player'] + dfshoot['Squad']
    dfshoot.loc[:, 'Player'] = dfshoot['Player'].apply(unidecode)
    dfshoot.loc[:, 'Squad'] = dfshoot['Squad'].apply(unidecode)

    if export_format == 'csv':
        file_path = f'fbrefBig5Shoot_{season}.csv'
        dfshoot.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'fbrefBig5Shoot_{season}.xlsx'
        dfshoot.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfshoot
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def possession_stats(start_year=None, export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/possession/players/{season}-Big-5-European-Leagues-Stats'

    try:
        df = pd.read_html(url)[0]
    except Exception as e:
        print(f"Error al leer datos de {url}: {e}")
        if return_df:
            return pd.DataFrame()
        else:
            return

    df.columns = df.columns.droplevel(0)
    dfpossession = df[df['Player'] != 'Player'].copy()

    cols = []
    count = 1
    for column in dfpossession.columns:
        if column == 'Prog':
            cols.append(f'Prog_{count}')
            count += 1
        else:
            cols.append(column)
    dfpossession.columns = cols

    dfpossession.loc[:, 'PlSqu'] = dfpossession['Player'] + dfpossession['Squad']
    dfpossession.loc[:, 'Player'] = dfpossession['Player'].apply(unidecode)
    dfpossession.loc[:, 'Squad'] = dfpossession['Squad'].apply(unidecode)

    if 'Matches' in dfpossession.columns:
        dfpossession.drop(columns='Matches', inplace=True)

    if export_format == 'csv':
        file_path = f'fbrefBig5Possession_{season}.csv'
        dfpossession.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'fbrefBig5Possession_{season}.xlsx'
        dfpossession.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfpossession
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def creation_stats(start_year=None, export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/gca/players/{season}-Big-5-European-Leagues-Stats'

    try:
        df = pd.read_html(url)[0]
    except Exception as e:
        print(f"Error al leer datos de {url}: {e}")
        if return_df:
            return pd.DataFrame()
        else:
            return

    df.columns = df.columns.droplevel(0)
    dfcreation = df[df['Player'] != 'Player'].copy()

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

    for col, suffix in [('PassLive', ''), ('PassDead', ''), ('Drib', ''), ('Sh', ''), ('Fld', ''), ('Def', '')]:
        dfcreation.columns = rename_duplicates(dfcreation.columns, col, suffix)

    dfcreation.columns = [
        col.replace('_1', '_SCA') if '_1' in col else
        col.replace('_2', '_GCA') if '_2' in col else
        col
        for col in dfcreation.columns
    ]

    if 'Matches' in dfcreation.columns:
        dfcreation.drop(columns='Matches', inplace=True)
    dfcreation.loc[:, 'PlSqu'] = dfcreation['Player'] + dfcreation['Squad']
    dfcreation.loc[:, 'Player'] = dfcreation['Player'].apply(unidecode)
    dfcreation.loc[:, 'Squad'] = dfcreation['Squad'].apply(unidecode)

    if export_format == 'csv':
        file_path = f'fbrefBig5Creation_{season}.csv'
        dfcreation.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'fbrefBig5Creation_{season}.xlsx'
        dfcreation.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfcreation
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def defense_stats(start_year=None, export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/defense/players/{season}-Big-5-European-Leagues-Stats'

    try:
        df = pd.read_html(url)[0]
    except Exception as e:
        print(f"Error al leer datos de {url}: {e}")
        if return_df:
            return pd.DataFrame()
        else:
            return

    df.columns = df.columns.droplevel(0)
    dfdefense = df[df['Player'] != 'Player'].copy()

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

    for col, suffix in [('Def 3rd', ''), ('Mid 3rd', ''), ('Att 3rd', ''), ('Tkl', '')]: #Verificar si Tkl realmente necesita esto o si es manejado por el siguiente bloque
        dfdefense.columns = rename_duplicates(dfdefense.columns, col, suffix)

    # Ajustar nombres de columnas para Tackle y Challenge
    # Esta lógica parece más específica, asegurar que no entre en conflicto con el bucle anterior
    new_cols_defense = []
    tkl_count = 1
    for col_name in dfdefense.columns:
        if col_name == 'Tkl': # Asumiendo que este 'Tkl' es el que se quiere renombrar a Tkl_tackles
            new_cols_defense.append(f'Tkl_tackles') # El original lo renombraba a Tkl_1 -> Tkl_tackles
            tkl_count += 1
        elif col_name == 'Tkl_2': # Asumiendo que este sería el renombrado por rename_duplicates si hubiera un segundo 'Tkl' original
             new_cols_defense.append('Tkl_challenges')
        else:
            new_cols_defense.append(col_name)
    dfdefense.columns = new_cols_defense
    # Re-evaluar la lógica original de renombrado de Tkl:
    # dfdefense.columns = [
    # col.replace('_1', '_tackles') if '_1' in col else # Originalmente col == 'Tkl_1'
    # col.replace('_2', '_challenges') if '_2' in col else # Originalmente col == 'Tkl_2'
    # col
    # for col in dfdefense.columns
    # ]
    # Esto sugiere que después de rename_duplicates, podrías tener 'Tkl_1', 'Tkl_2' etc.
    # Vamos a seguir el patrón original de forma más directa:
    final_cols = []
    temp_cols = list(dfdefense.columns) # Trabajar sobre una copia temporal de las columnas

    # Primero, el renombrado genérico de duplicados
    for target_col_rename in ['Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl']:
         temp_cols = rename_duplicates(temp_cols, target_col_rename, "") # El suffix original era vacío

    # Luego, el renombrado específico para Tkl si aparecen como Tkl_1, Tkl_2
    processed_cols = []
    for col in temp_cols:
        if col == "Tkl_1": # Asumiendo que 'Tkl_1' viene de rename_duplicates
            processed_cols.append("Tkl_tackles")
        elif col == "Tkl_2": # Asumiendo que 'Tkl_2' viene de rename_duplicates
            processed_cols.append("Tkl_challenges")
        else:
            processed_cols.append(col)
    dfdefense.columns = processed_cols


    if 'Matches' in dfdefense.columns:
        dfdefense.drop(columns='Matches', inplace=True)
    dfdefense.loc[:, 'PlSqu'] = dfdefense['Player'] + dfdefense['Squad']
    dfdefense.loc[:, 'Player'] = dfdefense['Player'].apply(unidecode)
    dfdefense.loc[:, 'Squad'] = dfdefense['Squad'].apply(unidecode)

    if export_format == 'csv':
        file_path = f'fbrefBig5Defense_{season}.csv'
        dfdefense.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'fbrefBig5Defense_{season}.xlsx'
        dfdefense.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfdefense
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def passing_stats(start_year=None, export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/passing/players/{season}-Big-5-European-Leagues-Stats'

    try:
        df = pd.read_html(url)[0]
    except Exception as e:
        print(f"Error al leer datos de {url}: {e}")
        if return_df:
            return pd.DataFrame()
        else:
            return

    df.columns = df.columns.droplevel(0)
    dfPassing = df[df['Player'] != 'Player'].copy()

    def rename_duplicates(columns, target_col, suffix=""): # Suffix por defecto vacío como en el original
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{suffix}{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    current_columns = list(dfPassing.columns)
    for col_target in ['Cmp', 'Att', 'Cmp%']: # Columnas que se renombraban con sufijos numéricos
        current_columns = rename_duplicates(current_columns, col_target) # Usar el suffix por defecto que añade _1, _2 etc.
    dfPassing.columns = current_columns

    dfPassing.columns = [
        col.replace('_1', '') if '_1' in col else  # Para Cmp_1 -> Cmp, Att_1 -> Att, Cmp%_1 -> Cmp%
        col.replace('_2', '_short') if '_2' in col else
        col.replace('_3', '_medium') if '_3' in col else
        col.replace('_4', '_long') if '_4' in col else
        col
        for col in dfPassing.columns
    ]

    if 'Matches' in dfPassing.columns:
        dfPassing.drop(columns='Matches', inplace=True)
    dfPassing.loc[:, 'PlSqu'] = dfPassing['Player'] + dfPassing['Squad']
    dfPassing.loc[:, 'Player'] = dfPassing['Player'].apply(unidecode)
    dfPassing.loc[:, 'Squad'] = dfPassing['Squad'].apply(unidecode)

    if export_format == 'csv':
        file_path = f'fbrefBig5Passing_{season}.csv'
        dfPassing.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'fbrefBig5Passing_{season}.xlsx'
        dfPassing.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfPassing
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def passing_type_stats(start_year=None, export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/passing_types/players/{season}-Big-5-European-Leagues-Stats'

    try:
        df = pd.read_html(url)[0]
    except Exception as e:
        print(f"Error al leer datos de {url}: {e}")
        if return_df:
            return pd.DataFrame()
        else:
            return

    df.columns = df.columns.droplevel(0)
    dfpassingtypes = df[df['Player'] != 'Player'].copy()

    def rename_duplicates(columns, target_col, suffix=""): # Suffix por defecto vacío como en el original
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{suffix}{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    dfpassingtypes.columns = rename_duplicates(dfpassingtypes.columns, 'Out', '') # El original usaba '' como suffix

    if 'Matches' in dfpassingtypes.columns:
        dfpassingtypes.drop(columns='Matches', inplace=True)

    dfpassingtypes.loc[:, 'PlSqu'] = dfpassingtypes['Player'] + dfpassingtypes['Squad']
    dfpassingtypes.loc[:, 'Player'] = dfpassingtypes['Player'].apply(unidecode)
    dfpassingtypes.loc[:, 'Squad'] = dfpassingtypes['Squad'].apply(unidecode)

    if export_format == 'csv':
        file_path = f'fbrefBig5PassingType_{season}.csv'
        dfpassingtypes.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'fbrefBig5PassingType_{season}.xlsx'
        dfpassingtypes.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfpassingtypes
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def playing_time_stats(start_year=None, export_format=None, return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os

    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/playingtime/players/{season}-Big-5-European-Leagues-Stats'

    try:
        df = pd.read_html(url)[0]
    except Exception as e:
        print(f"Error al leer datos de {url}: {e}")
        if return_df:
            return pd.DataFrame()
        else:
            return

    df.columns = df.columns.droplevel(0)
    dfplayingtime = df[df['Player'] != 'Player'].copy()

    def rename_duplicates(columns, target_col, suffix=""): # Suffix por defecto vacío como en el original
        count = 1
        new_columns = []
        for col in columns:
            if col == target_col:
                new_columns.append(f"{target_col}_{suffix}{count}")
                count += 1
            else:
                new_columns.append(col)
        return new_columns

    dfplayingtime.columns = rename_duplicates(dfplayingtime.columns, 'On-Off', '') # El original usaba '' como suffix

    if 'Matches' in dfplayingtime.columns:
        dfplayingtime.drop(columns='Matches', inplace=True)

    dfplayingtime.loc[:, 'PlSqu'] = dfplayingtime['Player'] + dfplayingtime['Squad']
    dfplayingtime.loc[:, 'Player'] = dfplayingtime['Player'].apply(unidecode)
    dfplayingtime.loc[:, 'Squad'] = dfplayingtime['Squad'].apply(unidecode)

    if export_format == 'csv':
        file_path = f'fbrefBig5PlayingTime_{season}.csv'
        dfplayingtime.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'fbrefBig5PlayingTime_{season}.xlsx'
        dfplayingtime.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return dfplayingtime
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")


def scrape_all_stats(start_year=None, export_format=None, return_dfs=False):
    dfs = []
    season_str = _get_season_string(start_year) # Para mensajes y nombres de archivo si es necesario
    print(f"Iniciando scraping para la temporada: {season_str}")

    print("Starting to scrape shooting stats...")
    if return_dfs:
        dfs.append(shooting_stats(start_year=start_year, return_df=True))
    else:
        shooting_stats(start_year=start_year, export_format=export_format)

    print("Starting to scrape defense stats...")
    if return_dfs:
        dfs.append(defense_stats(start_year=start_year, return_df=True))
    else:
        defense_stats(start_year=start_year, export_format=export_format)

    print("Starting to scrape passing stats...")
    if return_dfs:
        dfs.append(passing_stats(start_year=start_year, return_df=True))
    else:
        passing_stats(start_year=start_year, export_format=export_format)

    print("Starting to scrape passing type stats...")
    if return_dfs:
        dfs.append(passing_type_stats(start_year=start_year, return_df=True))
    else:
        passing_type_stats(start_year=start_year, export_format=export_format)

    print("Starting to scrape playing time stats...")
    if return_dfs:
        dfs.append(playing_time_stats(start_year=start_year, return_df=True))
    else:
        playing_time_stats(start_year=start_year, export_format=export_format)

    print("Starting to scrape standard stats...")
    if return_dfs:
        dfs.append(standard_stats(start_year=start_year, return_df=True))
    else:
        standard_stats(start_year=start_year, export_format=export_format)

    print("Starting to scrape possession stats...")
    if return_dfs:
        dfs.append(possession_stats(start_year=start_year, return_df=True))
    else:
        possession_stats(start_year=start_year, export_format=export_format)

    print("Starting to scrape creation stats...")
    if return_dfs:
        dfs.append(creation_stats(start_year=start_year, return_df=True))
    else:
        creation_stats(start_year=start_year, export_format=export_format)

    print(f"All stats for season {season_str} have been scraped.")
    if not return_dfs and export_format:
         print(f"Files saved with _{season_str} suffix.")


    if return_dfs:
        return dfs


def merger_5leagues(start_year=None, export_format=None, return_df=False):
    import pandas as pd
    import os
    import unicodedata

    season_str = _get_season_string(start_year)
    print(f"Iniciando merge para la temporada: {season_str}")

    player_stand_stats = standard_stats(start_year=start_year, return_df=True)
    player_shoot_stats = shooting_stats(start_year=start_year, return_df=True)
    player_pass_stats = passing_stats(start_year=start_year, return_df=True)
    player_passtypes_stats = passing_type_stats(start_year=start_year, return_df=True) # No se usaba en el merge original, pero lo cargo por si acaso
    player_ga_stats = creation_stats(start_year=start_year, return_df=True)
    player_defense_stats = defense_stats(start_year=start_year, return_df=True)
    player_possession_stats = possession_stats(start_year=start_year, return_df=True)
    player_time_stats = playing_time_stats(start_year=start_year, return_df=True)

    # Verificar si algún DataFrame está vacío antes de hacer merge
    dataframes_to_merge = {
        "standard": player_stand_stats,
        "shooting": player_shoot_stats,
        "passing": player_pass_stats,
        "ga": player_ga_stats,
        "defense": player_defense_stats,
        "possession": player_possession_stats,
        "time": player_time_stats
    }

    for name, df_check in dataframes_to_merge.items():
        if df_check.empty:
            print(f"Advertencia: El DataFrame '{name}' para la temporada {season_str} está vacío. El merge podría fallar o estar incompleto.")
            # Podrías decidir devolver un DataFrame vacío o parar aquí si un df crucial está vacío
            # Por ahora, continuará e intentará el merge.

    if player_stand_stats.empty:
        print(f"El DataFrame principal 'standard_stats' está vacío para la temporada {season_str}. No se puede continuar con el merge.")
        if return_df:
            return pd.DataFrame()
        return

    # Unión de player_stand_stats con player_shoot_stats
    merged_df = pd.merge(
        player_stand_stats,
        player_shoot_stats.drop(columns=[col for col in player_shoot_stats.columns if col in player_stand_stats.columns and col != 'PlSqu'], errors='ignore'), # Evitar duplicados excepto PlSqu
        on='PlSqu',
        how='inner', # Cambiar a 'left' si quieres mantener todos los jugadores de player_stand_stats
        suffixes=('_stand', '_shoot')
    )

    # Limpieza de columnas duplicadas (una forma más genérica)
    # Columnas base del primer DF (player_stand_stats)
    base_cols = {col for col in player_stand_stats.columns if col != 'PlSqu'}

    # Lista de DataFrames a fusionar (excluyendo el primero que es la base)
    additional_dfs = [
        player_pass_stats,
        player_ga_stats,
        player_defense_stats,
        player_possession_stats,
        player_time_stats,
        player_passtypes_stats # Añadido aquí si se decide incluirlo en el merge
    ]

    current_merged_df = merged_df.copy()

    for i, df_to_add in enumerate(additional_dfs):
        if df_to_add.empty:
            print(f"Saltando merge con DataFrame vacío (índice {i}).")
            continue
        # Columnas a eliminar del df_to_add: aquellas que ya están en current_merged_df excepto 'PlSqu'
        cols_to_drop_from_df_to_add = [col for col in df_to_add.columns if col in current_merged_df.columns and col != 'PlSqu']
        df_cleaned = df_to_add.drop(columns=cols_to_drop_from_df_to_add, errors='ignore')

        current_merged_df = pd.merge(
            current_merged_df,
            df_cleaned,
            on='PlSqu',
            how='inner', # O 'left' sobre current_merged_df si se prefiere
            suffixes=(f'_df{i}', f'_df{i+1}') # Sufijos genéricos para evitar colisiones, se limpiarán después
        )
        if current_merged_df.empty and not df_cleaned.empty:
             print(f"Advertencia: El merge con el DataFrame (índice {i}) resultó en un DataFrame vacío. Verificar 'PlSqu' IDs.")


    final_merged_df = current_merged_df.copy()

    # Eliminar columnas de unión redundantes que no sean 'PlSqu' y las auxiliares de merge
    # Por ejemplo, si Player_shoot, Squad_shoot etc. se crearon y no se quieren.
    # Esto es más complejo de generalizar sin conocer todos los nombres exactos post-merge.
    # La lógica original de drop por sufijos era más específica.
    # Reimplementando la lógica de drop específica post-merge:

    # Columnas a eliminar si tienen sufijos y la base ya existe
    def drop_suffixed_duplicates(df, base_df_cols, suffix):
        cols_to_drop = [col for col in df.columns if col.endswith(suffix) and col[:-len(suffix)] in base_df_cols]
        return df.drop(columns=cols_to_drop, errors='ignore')

    # Después del primer merge (stand y shoot)
    # Las columnas de player_stand_stats son la base. Si player_shoot_stats tenía 'Player', 'Squad', etc., se renombran con _shoot
    # La lógica original era:
    # columns_to_drop = [col for col in merged_df.columns if col.endswith('_shoot') and col[:-6] in player_stand_stats.columns]
    # merged_df = merged_df.drop(columns=columns_to_drop)
    # merged_df.columns = [col.replace('_stand', '') for col in merged_df.columns]

    # Esta parte es compleja porque los sufijos de pd.merge se aplican a TODAS las columnas que colisionan,
    # no solo a las que no son la clave de unión.
    # El enfoque original de merge y luego drop de columnas con sufijos específicos es probablemente más robusto
    # si se conocen los DataFrames.

    # Reintentando la secuencia de merge original con la limpieza adecuada:
    final_merged_df = player_stand_stats.copy()

    # Merge con player_shoot_stats
    if not player_shoot_stats.empty:
        cols_from_shoot_to_drop = [c for c in player_shoot_stats.columns if c in final_merged_df.columns and c != 'PlSqu']
        final_merged_df = pd.merge(final_merged_df, player_shoot_stats.drop(columns=cols_from_shoot_to_drop, errors='ignore'), on='PlSqu', how='inner')

    # Merge con player_pass_stats
    if not player_pass_stats.empty:
        cols_from_pass_to_drop = [c for c in player_pass_stats.columns if c in final_merged_df.columns and c != 'PlSqu']
        final_merged_df = pd.merge(final_merged_df, player_pass_stats.drop(columns=cols_from_pass_to_drop, errors='ignore'), on='PlSqu', how='inner')

    # Merge con player_ga_stats
    if not player_ga_stats.empty:
        cols_from_ga_to_drop = [c for c in player_ga_stats.columns if c in final_merged_df.columns and c != 'PlSqu']
        final_merged_df = pd.merge(final_merged_df, player_ga_stats.drop(columns=cols_from_ga_to_drop, errors='ignore'), on='PlSqu', how='inner')

    # Merge con player_defense_stats
    if not player_defense_stats.empty:
        cols_from_defense_to_drop = [c for c in player_defense_stats.columns if c in final_merged_df.columns and c != 'PlSqu']
        final_merged_df = pd.merge(final_merged_df, player_defense_stats.drop(columns=cols_from_defense_to_drop, errors='ignore'), on='PlSqu', how='inner')

    # Merge con player_possession_stats
    if not player_possession_stats.empty:
        cols_from_possession_to_drop = [c for c in player_possession_stats.columns if c in final_merged_df.columns and c != 'PlSqu']
        final_merged_df = pd.merge(final_merged_df, player_possession_stats.drop(columns=cols_from_possession_to_drop, errors='ignore'), on='PlSqu', how='inner')

    # Merge con player_time_stats
    if not player_time_stats.empty:
        cols_from_time_to_drop = [c for c in player_time_stats.columns if c in final_merged_df.columns and c != 'PlSqu']
        final_merged_df = pd.merge(final_merged_df, player_time_stats.drop(columns=cols_from_time_to_drop, errors='ignore'), on='PlSqu', how='inner')

    # Merge con player_passtypes_stats (si se va a incluir)
    if not player_passtypes_stats.empty:
        cols_from_passtypes_to_drop = [c for c in player_passtypes_stats.columns if c in final_merged_df.columns and c != 'PlSqu']
        final_merged_df = pd.merge(final_merged_df, player_passtypes_stats.drop(columns=cols_from_passtypes_to_drop, errors='ignore'), on='PlSqu', how='inner')


    # --- Limpieza final aplicada al final_merged_df ---
    if final_merged_df.empty:
        print(f"El DataFrame fusionado final está vacío para la temporada {season_str}. No se aplicará limpieza adicional.")
    else:
        nation_mapping = {
            'eng': 'England', 'es': 'Spain', 'ie': 'Ireland', 'fr': 'France', 'ma': 'Morocco',
            'dz': 'Algeria', 'eg': 'Egypt', 'tn': 'Tunisia', 'sa': 'Saudi Arabia', 'dk': 'Denmark',
            'br': 'Brazil', 'it': 'Italy', 'ng': 'Nigeria', 'sct': 'Scotland', 'us': 'USA',
            'at': 'Austria', 'de': 'Germany', 'ci': 'Ivory Coast', 'me': 'Montenegro', 'ch': 'Switzerland',
            'se': 'Sweden', 'gh': 'Ghana', 'no': 'Norway', 'ro': 'Romania', 'nl': 'Netherlands',
            'ar': 'Argentina', 'py': 'Paraguay', 'ga': 'Gabon', 'pt': 'Portugal', 'mx': 'Mexico',
            'sn': 'Senegal', 'pa': 'Panama', 'pr': 'Puerto Rico', 'jm': 'Jamaica', 'uy': 'Uruguay',
            've': 'Venezuela', 'ht': 'Haiti', 'is': 'Iceland', 'jp': 'Japan', 'al': 'Albania',
            'co': 'Colombia', 'tg': 'Togo', 'id': 'Indonesia', 'gn': 'Guinea', 'hr': 'Croatia',
            'sl': 'Sierra Leone', 'ca': 'Canada', 'cd': 'Congo (DR)', 'cm': 'Cameroon', 'hu': 'Hungary',
            'zm': 'Zambia', 'cz': 'Czech Republic', 'be': 'Belgium', 'tr': 'Turkey', 'sr': 'Suriname',
            'pl': 'Poland', 'sk': 'Slovakia', 'gw': 'Guinea-Bissau', 'si': 'Slovenia', 'ml': 'Mali',
            'nir': 'Northern Ireland', 'rs': 'Serbia', 'cl': 'Chile', 'wls': 'Wales', 'au': 'Australia',
            'nz': 'New Zealand', 'ec': 'Ecuador', 'lu': 'Luxembourg', 'gm': 'Gambia', 'cg': 'Congo',
            'bd': 'Bangladesh', 'gq': 'Equatorial Guinea', 'cv': 'Cape Verde', 'ge': 'Georgia',
            'mq': 'Martinique', 'ba': 'Bosnia and Herzegovina', 'mk': 'North Macedonia', 'bf': 'Burkina Faso',
            'gr': 'Greece', 'ua': 'Ukraine', 'cr': 'Costa Rica', 'lt': 'Lithuania', 'ru': 'Russia',
            'do': 'Dominican Republic', 'iq': 'Iraq', 'kr': 'South Korea', 'ph': 'Philippines',
            'bj': 'Benin', 'fi': 'Finland', 'ee': 'Estonia', 'zw': 'Zimbabwe', 'il': 'Israel',
            'cy': 'Cyprus', 'uz': 'Uzbekistan', 'ao': 'Angola', 'cf': 'Central African Republic',
            'gp': 'Guadeloupe', 'mg': 'Madagascar', 'pe': 'Peru', 'gf': 'French Guiana',
            'mz': 'Mozambique', 'am': 'Armenia', 'xk': 'Kosovo', 'ly': 'Libya', 'bi': 'Burundi',
            'ke': 'Kenya', 'km': 'Comoros', 'md': 'Moldova', 'ms': 'Montserrat', 'jo': 'Jordan',
            'ir': 'Iran', 'mt': 'Malta'
        }
        if 'Nation' in final_merged_df.columns:
            final_merged_df.loc[:,'Nation'] = final_merged_df['Nation'].astype(str).str.extract(r'^(\w+)')[0].str.lower()
            final_merged_df.loc[:,'Nation'] = final_merged_df['Nation'].map(nation_mapping)
        else:
            print("Advertencia: Columna 'Nation' no encontrada en el DataFrame fusionado.")


        if 'Comp' in final_merged_df.columns:
            final_merged_df.loc[:,'Comp'] = final_merged_df['Comp'].astype(str).str.extract(r'^\w+\s+(.*)')[0]
        else:
            print("Advertencia: Columna 'Comp' no encontrada en el DataFrame fusionado.")


        def edad_a_decimal(edad_str):
            if pd.isnull(edad_str):
                return None
            try:
                partes = str(edad_str).split('-')
                años = int(partes[0])
                dias = int(partes[1]) if len(partes) > 1 else 0 # Manejar edad sin días
                return round(años + dias / 365, 2)
            except:
                return None # O np.nan si se prefiere

        if 'Age' in final_merged_df.columns:
            final_merged_df.loc[:,'DecimalAge'] = final_merged_df['Age'].apply(edad_a_decimal)
        else:
            print("Advertencia: Columna 'Age' no encontrada en el DataFrame fusionado.")


        try:
            df_maestro = pd.read_csv("https://raw.githubusercontent.com/Josegra/Football_Scraper/main/players.csv")
        except Exception as e:
            print(f"No se pudo cargar el archivo maestro de jugadores: {e}. No se agregarán sub-posiciones.")
            df_maestro = pd.DataFrame(columns=['name_norm', 'sub_position']) # Crear df vacío para evitar errores


        def normalizar_nombre(nombre):
            if pd.isnull(nombre):
                return ""
            nombre = unicodedata.normalize('NFKD', str(nombre)).encode('ASCII', 'ignore').decode('utf-8')
            return nombre.lower().strip()

        if 'Player' in final_merged_df.columns:
            final_merged_df.loc[:,'Player_norm'] = final_merged_df['Player'].apply(normalizar_nombre)
        else:
            print("Advertencia: Columna 'Player' no encontrada en el DataFrame fusionado. No se puede normalizar para merge.")
            final_merged_df.loc[:,'Player_norm'] = "" # Columna vacía para evitar error en merge

        df_maestro.loc[:,'name_norm'] = df_maestro['name'].apply(normalizar_nombre) if 'name' in df_maestro.columns else ""

        df_maestro_unico = df_maestro[['name_norm', 'sub_position']].drop_duplicates(subset='name_norm') if 'name_norm' in df_maestro.columns and 'sub_position' in df_maestro.columns else pd.DataFrame(columns=['name_norm', 'sub_position'])


        if not df_maestro_unico.empty and 'Player_norm' in final_merged_df.columns:
             final_merged_df = final_merged_df.merge(
                df_maestro_unico,
                how='left',
                left_on='Player_norm',
                right_on='name_norm'
            )
             final_merged_df.drop(columns=['name_norm', 'Player_norm'], inplace=True, errors='ignore')
        elif 'Player_norm' in final_merged_df.columns: # Player_norm existe pero df_maestro_unico está vacío
            final_merged_df.drop(columns=['Player_norm'], inplace=True, errors='ignore')
            print("Advertencia: df_maestro_unico está vacío, no se añaden sub-posiciones.")


    # --- Fin limpieza final ---

    if export_format == 'csv':
        file_path = f'final_fbref_all5_columns_{season_str}.csv'
        final_merged_df.to_csv(file_path, index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(file_path)}")
    elif export_format == 'excel':
        file_path = f'final_fbref_all5_columns_{season_str}.xlsx'
        final_merged_df.to_excel(file_path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(file_path)}")
    elif return_df:
        return final_merged_df
    else:
        print("Por favor, especifica un formato de exportación ('csv' o 'excel') o selecciona return_df=True para obtener un DataFrame.")
