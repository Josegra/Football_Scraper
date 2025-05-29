from datetime import datetime
import requests
import pandas as pd
from unidecode import unidecode
import os
import time

# --- Helper Function ---
def _get_season_string(start_year=None):
    """Determines the season string, e.g., '2023-2024'."""
    current_year = datetime.now().year
    if start_year is None:
        # FBRef uses the starting year for the season URL, e.g., 2023 for 2023-2024 season.
        # If it's May 2025, the 2024-2025 season is the one likely just concluded or current.
        # So, the year to use would be current_year - 1.
        year_to_use = current_year - 1
    else:
        try:
            year_to_use = int(start_year)
        except ValueError:
            print(f"Advertencia: start_year ('{start_year}') no válido. Usando {current_year - 1}.")
            year_to_use = current_year - 1
    return f"{year_to_use}-{year_to_use + 1}"

# --- Stat Scraping Functions (Comments and logic preserved, minor adjustments) ---
def _fetch_and_clean_fbref_table(url):
    """Fetches and performs initial cleaning of an FBRef table."""
    try:
        if not url.startswith("https://"):
            print(f"Advertencia: La URL {url} no usa HTTPS. Intentando con HTTPS.")
            if url.startswith("http://"):
                url = url.replace("http://", "https://", 1)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        dfs = pd.read_html(response.content)
        if not dfs:
            print(f"No se encontraron tablas en {url}")
            return pd.DataFrame()

        df = dfs[0].copy() # Use .copy() early
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(0)
        df = df[df['Player'] != 'Player'].copy() # Ensure it's a copy after filtering

        if 'Matches' in df.columns:
            df.drop(columns='Matches', inplace=True)

        # Apply unidecode carefully
        if 'Player' in df.columns:
            df.loc[:, 'Player'] = df['Player'].apply(lambda x: unidecode(str(x)) if pd.notnull(x) else x)
        if 'Squad' in df.columns:
            df.loc[:, 'Squad'] = df['Squad'].apply(lambda x: unidecode(str(x)) if pd.notnull(x) else x)

        if 'Player' in df.columns and 'Squad' in df.columns:
            # Ensure Player and Squad are strings before concatenation
            df.loc[:, 'PlSqu'] = df['Player'].astype(str) + df['Squad'].astype(str)
        else:
            # Create an empty PlSqu column if Player or Squad is missing, to avoid downstream errors
            df.loc[:, 'PlSqu'] = pd.Series(index=df.index, dtype='str')
            print("Advertencia: Columnas 'Player' o 'Squad' no encontradas, 'PlSqu' creada vacía.")
        return df
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP al leer datos de {url}: {http_err} (Status: {http_err.response.status_code})")
        if http_err.response.status_code == 403:
            print("Error 403 Forbidden. El servidor está bloqueando la solicitud.")
        elif http_err.response.status_code == 404:
            print(f"Error 404: Página no encontrada en {url}.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"Error de red o HTTP al leer datos de {url}: {e}")
        return pd.DataFrame()
    except ValueError as ve: # Handles cases where read_html finds no tables
        print(f"Error al parsear HTML (posiblemente no hay tablas válidas) de {url}: {ve}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error general al leer o limpiar datos de {url}: {e}")
        return pd.DataFrame()

def _export_csv_to_data_folder(df, base_name, season):
    """Exports DataFrame to a CSV file in the ./data directory."""
    if df.empty:
        print(f"DataFrame para '{base_name}_{season}' está vacío. No se guardará.")
        return

    output_dir = './data'
    os.makedirs(output_dir, exist_ok=True) # Create ./data directory if it doesn't exist

    file_name = f'{base_name}_{season}.csv'
    output_path = os.path.join(output_dir, file_name)

    df.to_csv(output_path, encoding='utf-8', index=False)
    print(f"Archivo CSV guardado en: {os.path.abspath(output_path)}")


# Individual stat functions (standard_stats, shooting_stats, etc.)
# These retain their original structure but their export_format parameter
# won't be used by the merger_5leagues flow.
# Example for standard_stats, others follow the same pattern regarding export.
def standard_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/stats/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None # Return empty DF if needed

    # Renaming logic from original script
    def rename_duplicates_std(columns, target_col):
        count = 1; new_columns = []
        for col_item in columns: # Renamed col to col_item to avoid conflict if col is a parameter
            if col_item == target_col: new_columns.append(f"{target_col}_{count}"); count +=1
            else: new_columns.append(col_item)
        return new_columns

    for col_target in ['Gls', 'Ast', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR','xG', 'npxG', 'xA', 'npxG+xA', 'G+A', 'xAG', 'npxG+xAG']:
        if col_target in df.columns:
            df.columns = rename_duplicates_std(df.columns, col_target)
    df.columns = [c.replace('_1','').replace('_2','_p90') if '_1' in c or '_2' in c else (c+'_p90' if c in ['G+A-PK','xG+xAG'] else c) for c in df.columns]

    # The _export_df call here is effectively bypassed by merger_5leagues setting return_df=True
    if export_format and not return_df : _export_csv_to_data_folder(df, 'fbrefBig5standard_INDIVIDUAL', season)
    return df if return_df else None # Ensure it returns if return_df is True

def shooting_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/shooting/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    if export_format and not return_df: _export_csv_to_data_folder(df, 'fbrefBig5Shoot_INDIVIDUAL', season)
    return df if return_df else None

def possession_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/possession/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    cols, count = [], 1
    for column in df.columns: cols.append(f'Prog_{count}' if column == 'Prog' and (count:=count+1)-1 else column) # Walrus operator, requires Python 3.8+
    df.columns = cols
    if export_format and not return_df: _export_csv_to_data_folder(df, 'fbrefBig5Possession_INDIVIDUAL', season)
    return df if return_df else None

def creation_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/gca/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_creation(columns, target_col):
        count = 1; new_columns = []
        for col_item in columns:
            if col_item == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col_item)
        return new_columns
    temp_cols = list(df.columns)
    for col_target in ['PassLive', 'PassDead', 'Drib', 'Sh', 'Fld', 'Def']:
        if col_target in df.columns:
            temp_cols = ren_dups_creation(temp_cols, col_target)
    df.columns = [c.replace('_1','_SCA').replace('_2','_GCA') if '_1' in c or '_2' in c else c for c in temp_cols]
    if export_format and not return_df: _export_csv_to_data_folder(df, 'fbrefBig5Creation_INDIVIDUAL', season)
    return df if return_df else None

def defense_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/defense/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_defense(columns, target_col):
        count = 1; new_columns = []
        for col_item in columns:
            if col_item == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col_item)
        return new_columns
    current_cols = list(df.columns)
    for col_target in ['Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl']:
        if col_target in df.columns:
            current_cols = ren_dups_defense(current_cols, col_target)
    df.columns = ['Tkl_tackles' if c == 'Tkl_1' else ('Tkl_challenges' if c == 'Tkl_2' else c) for c in current_cols]
    if export_format and not return_df: _export_csv_to_data_folder(df, 'fbrefBig5Defense_INDIVIDUAL', season)
    return df if return_df else None

def passing_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/passing/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_pass(columns, target_col):
        count = 1; new_columns = []
        for col_item in columns:
            if col_item == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col_item)
        return new_columns
    current_cols = list(df.columns)
    for col_target in ['Cmp', 'Att', 'Cmp%']:
        if col_target in df.columns:
            current_cols = ren_dups_pass(current_cols, col_target)
    df.columns = [c.replace('_1','').replace('_2','_short').replace('_3','_medium').replace('_4','_long') if any(s in c for s in ['_1','_2','_3','_4']) else c for c in current_cols]
    if export_format and not return_df: _export_csv_to_data_folder(df, 'fbrefBig5Passing_INDIVIDUAL', season)
    return df if return_df else None

def passing_type_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/passing_types/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_passtypes(columns, target_col): # Renamed for clarity
        count = 1; new_columns = []
        for col_item in columns:
            if col_item == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col_item)
        return new_columns
    if 'Out' in df.columns: # Example, adjust if other cols need this
        df.columns = ren_dups_passtypes(list(df.columns), 'Out')
    if export_format and not return_df: _export_csv_to_data_folder(df, 'fbrefBig5PassingType_INDIVIDUAL', season)
    return df if return_df else None

def playing_time_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/playingtime/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_playtime(columns, target_col): # Renamed for clarity
        count = 1; new_columns = []
        for col_item in columns:
            if col_item == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col_item)
        return new_columns
    if 'On-Off' in df.columns: # Example, adjust if other cols need this
        df.columns = ren_dups_playtime(list(df.columns), 'On-Off')
    if export_format and not return_df: _export_csv_to_data_folder(df, 'fbrefBig5PlayingTime_INDIVIDUAL', season)
    return df if return_df else None

# --- Function to Scrape All Stats ---
def scrape_all_stats_for_merge(start_year=None):
    season_str = _get_season_string(start_year)
    print(f"Iniciando scraping para la temporada: {season_str} (para merge)")

    stat_funcs_ordered = [
        standard_stats, shooting_stats, passing_stats, passing_type_stats,
        creation_stats, defense_stats, possession_stats, playing_time_stats
    ]
    dfs_list = []
    for i, func in enumerate(stat_funcs_ordered):
        if i > 0:
            print("Esperando 20 segundos antes de la siguiente solicitud...")
            time.sleep(20)

        print(f"Obteniendo datos de: {func.__name__}...")
        # Call with return_df=True to get DataFrame, export_format=None (or default) to bypass individual export
        df = func(start_year=start_year, return_df=True)
        if df is not None and not df.empty:
            dfs_list.append(df)
            print(f"Datos de {func.__name__} obtenidos. {df.shape[0]} filas, {df.shape[1]} columnas.")
        else:
            print(f"Advertencia: {func.__name__} devolvió un DataFrame vacío o None para {season_str}.")
    return dfs_list

# --- MERGER FUNCTION (Modified) ---
def merger_5leagues(start_year=None): # Removed export_format and return_df
    season_str = _get_season_string(start_year)
    print(f"Iniciando merge para la temporada: {season_str}")

    all_dfs = scrape_all_stats_for_merge(start_year=start_year)

    if not all_dfs:
        print(f"No se obtuvieron datos de ninguna tabla para {season_str}. No se puede mergear.")
        return # Exit if no data

    final_merged_df = pd.DataFrame()
    initial_df_found = False
    temp_all_dfs = list(all_dfs) # Create a mutable copy

    for i, df_iter in enumerate(all_dfs):
        if not df_iter.empty:
            final_merged_df = df_iter.copy() # Use a copy
            initial_df_found = True
            temp_all_dfs = all_dfs[i+1:] # Slice the original list for remaining DFs
            print(f"DataFrame inicial para merge tomado de {i+1}ª función. Forma: {final_merged_df.shape}")
            break
    
    if not initial_df_found:
        print(f"Todos los DataFrames obtenidos están vacíos para {season_str}. No se puede mergear.")
        return

    for df_to_add in temp_all_dfs:
        if df_to_add.empty:
            continue
        if 'PlSqu' in df_to_add.columns and 'PlSqu' in final_merged_df.columns:
            # Identify columns to keep from df_to_add (only 'PlSqu' and new columns)
            cols_from_new_df_to_keep = ['PlSqu'] + [col for col in df_to_add.columns if col not in final_merged_df.columns and col != 'PlSqu']
            df_cleaned_for_merge = df_to_add[cols_from_new_df_to_keep].copy()

            if not df_cleaned_for_merge.drop(columns=['PlSqu'], errors='ignore').empty: # Check if there are new columns besides PlSqu
                final_merged_df = pd.merge(final_merged_df, df_cleaned_for_merge, on='PlSqu', how='inner')
            else:
                print("Advertencia: Un DataFrame intermedio no tenía nuevas columnas (además de PlSqu) y fue omitido del merge.")
        else:
            print("Advertencia: Un DataFrame intermedio no contiene 'PlSqu' o el DF base no lo tiene; fue omitido del merge.")
    
    if final_merged_df.empty:
        print(f"El DataFrame fusionado (antes de maestro) está vacío para {season_str}.")
    else:
        print(f"DataFrame fusionado (antes de maestro) tiene {final_merged_df.shape[0]} filas, {final_merged_df.shape[1]} columnas.")
        # Nation mapping, Comp cleaning, Age to Decimal (preserved from original)
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
            extracted_nation_code = final_merged_df['Nation'].astype(str).str.extract(r'^(\w+)')[0].str.lower()
            final_merged_df.loc[:, 'Nation'] = extracted_nation_code.map(nation_mapping).fillna(final_merged_df['Nation']) # Use .loc for assignment

        if 'Comp' in final_merged_df.columns:
            final_merged_df.loc[:, 'Comp'] = final_merged_df['Comp'].astype(str).str.extract(r'^\w+\s+(.*)')[0].fillna(final_merged_df['Comp'])

        def edad_a_decimal(edad_str):
            if pd.isnull(edad_str): return None
            try:
                partes = str(edad_str).split('-')
                años = int(partes[0])
                dias = int(partes[1]) if len(partes) > 1 else 0
                return round(años + dias / 365, 2)
            except (ValueError, TypeError, IndexError): # Catch more specific errors
                try: return int(edad_str) # If it's just a year
                except: return None # If conversion fails
        
        if 'Age' in final_merged_df.columns:
            final_merged_df.loc[:, 'DecimalAge'] = final_merged_df['Age'].apply(edad_a_decimal)
        else: print("Advertencia: Columna 'Age' no encontrada para DecimalAge.")

        print("Intentando merge con players.csv (maestro)...")
        try:
            def generar_player_code_para_fbref(nombre_fbref):
                if pd.notnull(nombre_fbref) and str(nombre_fbref).strip():
                    s = str(nombre_fbref).lower().strip().replace("'", "")
                    return unidecode(s.replace(' ', '-'))
                return None

            if 'Player' in final_merged_df.columns:
                final_merged_df.loc[:, 'player_code'] = final_merged_df['Player'].apply(generar_player_code_para_fbref)
            else:
                print("Advertencia: 'Player' no en final_merged_df. No se puede generar 'player_code'.")
                final_merged_df.loc[:, 'player_code'] = pd.Series(dtype='object') # Create empty if not present

            df_maestro_raw = pd.read_csv("https://raw.githubusercontent.com/Josegra/Football_Scraper/main/players.csv")
            df_maestro = df_maestro_raw.copy()
            
            if 'name' in df_maestro.columns:
                df_maestro['player_code_maestro'] = df_maestro['name'].apply(generar_player_code_para_fbref)
            elif 'player_code' in df_maestro.columns: # If 'player_code' exists, use it as the key
                df_maestro.rename(columns={'player_code': 'player_code_maestro'}, inplace=True)
            else:
                print("Error crítico: 'players.csv' no tiene 'name' ni 'player_code'.")
                raise KeyError("Falta la columna clave ('name' o 'player_code') en players.csv para el merge.")

            if 'player_code_maestro' in df_maestro.columns and 'player_code' in final_merged_df.columns:
                columnas_maestro_seleccionadas = [
                    'player_code_maestro', 'sub_position', 'current_club_name',
                    'market_value_in_eur', 'last_season',
                    'foot', 'height_in_cm', 'contract_expiration_date'
                ]
                columnas_maestro_existentes = [col for col in columnas_maestro_seleccionadas if col in df_maestro.columns]
                
                if 'player_code_maestro' not in columnas_maestro_existentes:
                     print("Error Crítico: 'player_code_maestro' no está en las columnas del maestro para el cruce.")
                else:
                    df_maestro_filtrado = df_maestro[columnas_maestro_existentes].drop_duplicates(subset=['player_code_maestro'], keep='first')
                    
                    final_merged_df = final_merged_df.merge(
                        df_maestro_filtrado,
                        left_on='player_code',
                        right_on='player_code_maestro',
                        how='left',
                        suffixes=('', '_maestro') # Simpler suffix
                    )
                    if 'player_code_maestro' in final_merged_df.columns: # Drop the redundant key from maestro
                        final_merged_df.drop(columns=['player_code_maestro'], inplace=True)
                    
                    # Consolidate columns if suffixes were applied by merge due to existing col names
                    for col_base in [c for c in columnas_maestro_existentes if c != 'player_code_maestro']:
                        col_maestro_suffixed = col_base + '_maestro'
                        if col_maestro_suffixed in final_merged_df.columns:
                            # Prioritize maestro's data if it exists, otherwise keep original
                            final_merged_df[col_base] = final_merged_df[col_maestro_suffixed].fillna(final_merged_df.get(col_base))
                            final_merged_df.drop(columns=[col_maestro_suffixed], inplace=True)
                    print("Cruce con archivo maestro realizado.")
            else:
                print("Error: 'player_code' o 'player_code_maestro' no disponibles para el cruce con maestro.")

        except FileNotFoundError:
            print("Error: players.csv no encontrado en la URL.")
        except KeyError as ke:
            print(f"Error: columna faltante durante el merge con maestro: {ke}")
        except Exception as e:
            print(f"Error inesperado durante el merge con maestro: {e}")

    if not final_merged_df.empty:
        print("Convirtiendo columnas a formato numérico adecuado...")
        exclude_cols = [
            'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Born', 'foot',
            'contract_expiration_date', 'player_code', 'sub_position', 'current_club_name',
            'PlSqu', 'Age'
        ]
        for col in final_merged_df.columns:
            if col not in exclude_cols:
                # Attempt conversion only if not already numeric, handling various object types
                if final_merged_df[col].dtype == 'object' or pd.api.types.is_string_dtype(final_merged_df[col]):
                    final_merged_df.loc[:, col] = pd.to_numeric(final_merged_df[col], errors='coerce')
        print("Conversión a numérico completada.")
    else:
        print("DataFrame final vacío, no se realiza conversión numérica.")

    # Always export the final merged DataFrame using the new CSV export function
    _export_csv_to_data_folder(final_merged_df, 'final_fbref_all5_merged_data', season_str)
    # No return value needed as the script's purpose is to save the file.

# --- Main execution block ---
if __name__ == "__main__":
    print(f"--- Iniciando ejecución de {os.path.basename(__file__)} ---")
    # Determine the start_year for the season. None will use the default (latest completed season).
    # You could also pass a specific year, e.g., merger_5leagues(start_year=2022) for 2022-2023 season.
    target_start_year = None # o un año específico como 2023
    merger_5leagues(start_year=target_start_year)
    print(f"--- Ejecución de {os.path.basename(__file__)} completada ---")
