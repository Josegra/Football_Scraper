from datetime import datetime
import requests
import pandas as pd
from unidecode import unidecode
import os
import time # <--- AÑADIDO PARA LA PAUSA

# --- Helper Function ---
def _get_season_string(start_year=None):
    if start_year is None:
        # Para la temporada 2024-2025, si estamos en 2025, start_year debería ser 2024.
        # datetime.now().year - 1 es correcto si la temporada ya terminó.
        # Si la temporada está en curso y queremos esa temporada, podría ser datetime.now().year
        # pero FBRef estructura sus URLs con el año de inicio de la temporada.
        # Por ejemplo, la temporada 2024-2025 tiene start_year=2024.
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Si estamos después de julio (inicio típico de nueva temporada de fichajes/preparación)
        # y el usuario no especifica, podríamos asumir que quiere la temporada que acaba de terminar.
        # Si estamos a principios/mediados de año, datetime.now().year - 1 es la temporada anterior completa.
        # FBRef usualmente completa los datos de una temporada (ej. 2023-2024) unos meses después de que termine (Mayo/Junio 2024).
        # Para la temporada 2024-2025, el año a usar es 2024.
        # Si ahora es Mayo 2025, la temporada 2024-2025 es la que acaba de terminar.
        # Así, year_to_use = 2024. (datetime.now().year - 1)
        default_year = current_year -1 # Asume que queremos la temporada más reciente completada o casi completada
        year_to_use = default_year

    else:
        try:
            year_to_use = int(start_year)
        except ValueError:
            print(f"Advertencia: start_year ('{start_year}') no válido. Usando {datetime.now().year - 1}.")
            year_to_use = datetime.now().year - 1
    return f"{year_to_use}-{year_to_use + 1}"

# --- Stat Scraping Functions (Simplified Comments) ---
def _fetch_and_clean_fbref_table(url):
    try:
        if not url.startswith("https://"):
            print(f"Advertencia: La URL {url} no usa HTTPS. Intentando con HTTPS.")
            if url.startswith("http://"):
                url = url.replace("http://", "https://", 1)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30) # Aumentado timeout a 30s por si acaso
        response.raise_for_status()
        dfs = pd.read_html(response.content)
        if not dfs:
            print(f"No se encontraron tablas en {url}")
            return pd.DataFrame()
        df = dfs[0]
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(0)
        df = df[df['Player'] != 'Player'].copy()
        if 'Matches' in df.columns:
            df.drop(columns='Matches', inplace=True)
        df.loc[:, 'Player'] = df['Player'].apply(lambda x: unidecode(str(x)) if pd.notnull(x) else x)
        df.loc[:, 'Squad'] = df['Squad'].apply(lambda x: unidecode(str(x)) if pd.notnull(x) else x)
        if 'Player' in df.columns and 'Squad' in df.columns:
            df.loc[:, 'PlSqu'] = df['Player'].astype(str) + df['Squad'].astype(str)
        else:
            df.loc[:, 'PlSqu'] = pd.Series(dtype='str')
        return df
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP al leer datos de {url}: {http_err}")
        if http_err.response.status_code == 403:
            print("Esto es un error 403 Forbidden. El servidor está bloqueando la solicitud.")
            print("Intenta aumentar el tiempo de espera entre solicitudes o revisar tu User-Agent/IP.")
        elif http_err.response.status_code == 404:
            print(f"Error 404: Página no encontrada en {url}. Verifica la URL y la temporada.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"Error de red o HTTP al leer datos de {url}: {e}")
        return pd.DataFrame()
    except ValueError as ve:
        print(f"Error al parsear HTML (posiblemente no hay tablas) de {url}: {ve}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error general al leer o limpiar datos de {url}: {e}")
        return pd.DataFrame()

def _export_df(df, base_name, season, export_format):
    if df.empty:
        return
    if export_format == 'csv':
        path = f'{base_name}_{season}.csv'
        df.to_csv(path, encoding='utf-8', index=False)
        print(f"Archivo CSV guardado en: {os.path.abspath(path)}")
    elif export_format == 'excel':
        path = f'{base_name}_{season}.xlsx'
        df.to_excel(path, index=False)
        print(f"Archivo Excel guardado en: {os.path.abspath(path)}")

def standard_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/stats/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None

    def rename_duplicates_std(columns, target_col):
        count = 1; new_columns = []
        for col in columns:
            if col == target_col: new_columns.append(f"{target_col}_{count}"); count +=1
            else: new_columns.append(col)
        return new_columns
    for col in ['Gls', 'Ast', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR','xG', 'npxG', 'xA', 'npxG+xA', 'G+A', 'xAG', 'npxG+xAG']:
        if col in df.columns:
             df.columns = rename_duplicates_std(df.columns, col)
    df.columns = [c.replace('_1','').replace('_2','_p90') if '_1' in c or '_2' in c else (c+'_p90' if c in ['G+A-PK','xG+xAG'] else c) for c in df.columns]

    if export_format and not return_df : _export_df(df, 'fbrefBig5standard', season, export_format)
    return df if return_df else None

def shooting_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/shooting/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    if export_format and not return_df: _export_df(df, 'fbrefBig5Shoot', season, export_format)
    return df if return_df else None

def possession_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/possession/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    cols, count = [], 1
    for column in df.columns: cols.append(f'Prog_{count}' if column == 'Prog' and (count:=count+1)-1 else column)
    df.columns = cols
    if export_format and not return_df: _export_df(df, 'fbrefBig5Possession', season, export_format)
    return df if return_df else None

def creation_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/gca/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_creation(columns, target_col):
        count = 1; new_columns = []
        for col in columns:
            if col == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col)
        return new_columns
    temp_cols = list(df.columns)
    for col_target in ['PassLive', 'PassDead', 'Drib', 'Sh', 'Fld', 'Def']:
        if col_target in df.columns:
            temp_cols = ren_dups_creation(temp_cols, col_target)
    df.columns = [c.replace('_1','_SCA').replace('_2','_GCA') if '_1' in c or '_2' in c else c for c in temp_cols]
    if export_format and not return_df: _export_df(df, 'fbrefBig5Creation', season, export_format)
    return df if return_df else None

def defense_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/defense/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_defense(columns, target_col):
        count = 1; new_columns = []
        for col in columns:
            if col == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col)
        return new_columns
    current_cols = list(df.columns)
    for col_target in ['Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl']:
        if col_target in df.columns:
            current_cols = ren_dups_defense(current_cols, col_target)
    df.columns = ['Tkl_tackles' if c == 'Tkl_1' else ('Tkl_challenges' if c == 'Tkl_2' else c) for c in current_cols]
    if export_format and not return_df: _export_df(df, 'fbrefBig5Defense', season, export_format)
    return df if return_df else None

def passing_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/passing/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_pass(columns, target_col):
        count = 1; new_columns = []
        for col in columns:
            if col == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col)
        return new_columns
    current_cols = list(df.columns)
    for col_target in ['Cmp', 'Att', 'Cmp%']:
        if col_target in df.columns:
            current_cols = ren_dups_pass(current_cols, col_target)
    df.columns = [c.replace('_1','').replace('_2','_short').replace('_3','_medium').replace('_4','_long') if any(s in c for s in ['_1','_2','_3','_4']) else c for c in current_cols]
    if export_format and not return_df: _export_df(df, 'fbrefBig5Passing', season, export_format)
    return df if return_df else None

def passing_type_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/passing_types/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_passtypes(columns, target_col):
        count = 1; new_columns = []
        for col in columns:
            if col == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col)
        return new_columns
    if 'Out' in df.columns:
        df.columns = ren_dups_passtypes(list(df.columns), 'Out')
    if export_format and not return_df: _export_df(df, 'fbrefBig5PassingType', season, export_format)
    return df if return_df else None

def playing_time_stats(start_year=None, export_format=None, return_df=False):
    season = _get_season_string(start_year)
    url = f'https://fbref.com/en/comps/Big5/{season}/playingtime/players/{season}-Big-5-European-Leagues-Stats'
    df = _fetch_and_clean_fbref_table(url)
    if df.empty: return pd.DataFrame() if return_df else None
    def ren_dups_playtime(columns, target_col):
        count = 1; new_columns = []
        for col in columns:
            if col == target_col: new_columns.append(f"{target_col}_{count}"); count += 1
            else: new_columns.append(col)
        return new_columns
    if 'On-Off' in df.columns:
        df.columns = ren_dups_playtime(list(df.columns), 'On-Off')
    if export_format and not return_df: _export_df(df, 'fbrefBig5PlayingTime', season, export_format)
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
    for i, func in enumerate(stat_funcs_ordered): # Añadido enumerate para el primer sleep
        if i > 0: # No dormir antes de la primera solicitud de la serie
            print(f"Esperando 20 segundos antes de la siguiente solicitud para evitar ser bloqueado...")
            time.sleep(20) # <--- PAUSA DE 20 SEGUNDOS AÑADIDA AQUÍ

        print(f"Obteniendo datos de: {func.__name__}...")
        df = func(start_year=start_year, return_df=True)
        if df is not None and not df.empty:
            dfs_list.append(df)
            print(f"Datos de {func.__name__} obtenidos exitosamente. {df.shape[0]} filas y {df.shape[1]} columnas.")
        else:
            print(f"Advertencia: {func.__name__} devolvió un DataFrame vacío o None para {season_str}.")
    return dfs_list

# --- MERGER FUNCTION ---
def merger_5leagues(start_year=None, export_format=None, return_df=False):
    season_str = _get_season_string(start_year)
    print(f"Iniciando merge para la temporada: {season_str}")

    all_dfs = scrape_all_stats_for_merge(start_year=start_year)

    if not all_dfs:
        print(f"No se obtuvieron datos de ninguna tabla para {season_str}. No se puede mergear.")
        if return_df: return pd.DataFrame()
        return None

    final_merged_df = pd.DataFrame()
    initial_df_found = False
    temp_all_dfs = list(all_dfs) # Copiar para poder modificarla

    for i, df_iter in enumerate(all_dfs):
        if not df_iter.empty:
            final_merged_df = df_iter.copy()
            initial_df_found = True
            temp_all_dfs = all_dfs[i+1:]
            print(f"DataFrame inicial para merge tomado de la función de scraping número {i+1}. Forma: {final_merged_df.shape}")
            break
    
    if not initial_df_found:
        print(f"Todos los DataFrames obtenidos están vacíos para {season_str}. No se puede mergear.")
        if return_df: return pd.DataFrame()
        return None

    for df_to_add in temp_all_dfs: # Usar la lista modificada
        if df_to_add.empty:
            continue
        if 'PlSqu' in df_to_add.columns and 'PlSqu' in final_merged_df.columns:
            cols_to_drop_from_new_df = [c for c in df_to_add.columns if c in final_merged_df.columns and c != 'PlSqu']
            if 'PlSqu' in cols_to_drop_from_new_df : cols_to_drop_from_new_df.remove('PlSqu')
            df_cleaned = df_to_add.drop(columns=cols_to_drop_from_new_df, errors='ignore')
            if not df_cleaned.empty:
                final_merged_df = pd.merge(final_merged_df, df_cleaned, on='PlSqu', how='inner')
            else:
                print(f"Advertencia: Un DataFrame intermedio quedó vacío después de limpiar columnas duplicadas y fue omitido.")
        else:
            print(f"Advertencia: Un DataFrame intermedio no contiene 'PlSqu' y fue omitido del merge.")

    if final_merged_df.empty:
        print(f"El DataFrame fusionado (antes de maestro) está vacío para {season_str}.")
    else:
        print(f"DataFrame fusionado (antes de maestro) tiene {final_merged_df.shape[0]} filas y {final_merged_df.shape[1]} columnas.")
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
            final_merged_df['Nation'] = extracted_nation_code.map(nation_mapping).fillna(extracted_nation_code)

        if 'Comp' in final_merged_df.columns:
            final_merged_df['Comp'] = final_merged_df['Comp'].astype(str).str.extract(r'^\w+\s+(.*)')[0].fillna(final_merged_df['Comp'])

        def edad_a_decimal(edad_str):
            if pd.isnull(edad_str): return None
            try:
                partes = str(edad_str).split('-')
                años = int(partes[0])
                dias = int(partes[1]) if len(partes) > 1 else 0
                return round(años + dias / 365, 2)
            except ValueError:
                try: return int(edad_str)
                except: return None
            except Exception: return None

        if 'Age' in final_merged_df.columns:
            final_merged_df['DecimalAge'] = final_merged_df['Age'].apply(edad_a_decimal)
        else: print("Advertencia: Columna 'Age' no encontrada para DecimalAge.")

        print("Intentando merge con players.csv...")
        try:
            def generar_player_code_para_fbref(nombre_fbref):
                if pd.notnull(nombre_fbref) and str(nombre_fbref).strip():
                    s = str(nombre_fbref).lower().strip().replace("'", "")
                    return unidecode(s.replace(' ', '-'))
                return None

            if 'Player' in final_merged_df.columns:
                final_merged_df['player_code'] = final_merged_df['Player'].apply(generar_player_code_para_fbref)
            else:
                print("Advertencia: Columna 'Player' no en final_merged_df. No se puede generar 'player_code' para el cruce.")
                final_merged_df['player_code'] = pd.Series(dtype='object')

            df_maestro_raw = pd.read_csv("https://raw.githubusercontent.com/Josegra/Football_Scraper/main/players.csv")
            df_maestro = df_maestro_raw.copy()
            
            if 'name' in df_maestro.columns:
                 df_maestro['player_code_maestro'] = df_maestro['name'].apply(generar_player_code_para_fbref) # Usar un nombre diferente para evitar conflicto inmediato
            elif 'player_code' not in df_maestro.columns: # Si no tiene 'name' ni 'player_code'
                print("Error crítico: 'players.csv' no tiene columna 'name' para generar 'player_code', ni 'player_code' preexistente.")
            else: # Si tiene 'player_code' pero no 'name', lo renombramos para consistencia interna
                df_maestro.rename(columns={'player_code': 'player_code_maestro'}, inplace=True)


            if 'player_code_maestro' in df_maestro.columns and 'player_code' in final_merged_df.columns:
                columnas_maestro_seleccionadas = [
                    'player_code_maestro', 'sub_position', 'current_club_name',
                    'market_value_in_eur', 'last_season',
                    'foot', 'height_in_cm', 'contract_expiration_date'
                ]
                columnas_maestro_existentes = [col for col in columnas_maestro_seleccionadas if col in df_maestro.columns]
                
                if 'player_code_maestro' not in columnas_maestro_existentes:
                    print("Error Crítico: 'player_code_maestro' no está en las columnas seleccionadas del maestro para el cruce.")
                else:
                    df_maestro_filtrado = df_maestro[columnas_maestro_existentes].drop_duplicates(subset='player_code_maestro', keep='first')
                    
                    final_merged_df = final_merged_df.merge(
                        df_maestro_filtrado,
                        left_on='player_code',
                        right_on='player_code_maestro', # Usar la columna renombrada/generada del maestro
                        how='left',
                        suffixes=('', '_duplicate_from_maestro') # Sufijo más específico
                    )
                    # Eliminar la clave de merge duplicada del maestro si se añadió
                    if 'player_code_maestro' in final_merged_df.columns:
                         final_merged_df.drop(columns=['player_code_maestro'], inplace=True)

                    # Consolidar columnas si hubo sufijos _duplicate_from_maestro
                    cols_originales_del_maestro = list(set(columnas_maestro_existentes) - {'player_code_maestro'}) # Columnas que queríamos traer
                    for col_base in cols_originales_del_maestro:
                        col_con_sufijo = col_base + '_duplicate_from_maestro'
                        if col_con_sufijo in final_merged_df.columns:
                            # Si la columna original (ej. 'foot') ya existía en final_merged_df y también vino del maestro (como 'foot_duplicate_from_maestro')
                            # Esta lógica prioriza el valor del maestro. Si el valor del maestro es NaN, se queda con el valor original de final_merged_df.
                            final_merged_df[col_base] = final_merged_df[col_con_sufijo].combine_first(final_merged_df.get(col_base))
                            final_merged_df.drop(columns=[col_con_sufijo], inplace=True)
                        # Si la col_base no existía en final_merged_df antes, y ahora sí (porque vino del maestro sin sufijo,
                        # lo cual pd.merge hace si no hay colisión), entonces ya está bien.
                        # Si la col_base existía y no hubo colisión de nombres (el maestro no la tenía o tenía otro nombre), también está bien.

                    print("Cruce con archivo maestro realizado correctamente.")
            else:
                 print("Error: Clave de jugador ('player_code' o 'player_code_maestro') no está disponible en ambos DataFrames para el cruce con el maestro.")

        except FileNotFoundError:
            print("Error: players.csv no encontrado en la URL especificada.")
        except KeyError as ke:
            print(f"Error: columna faltante durante el merge o preparación del maestro: {ke}")
        except Exception as e:
            print(f"Error inesperado durante el merge con el maestro: {e}")

    if not final_merged_df.empty:
        print("Convirtiendo columnas a formato numérico adecuado...")
        exclude_cols = [
            'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Born', 'foot',
            'contract_expiration_date', 'player_code', 'sub_position', 'current_club_name',
            'PlSqu', 'Age'
        ]
        for col in final_merged_df.columns:
            if col not in exclude_cols:
                if final_merged_df[col].dtype == 'object' or pd.api.types.is_string_dtype(final_merged_df[col]):
                    final_merged_df[col] = pd.to_numeric(final_merged_df[col], errors='coerce')
                elif pd.api.types.is_datetime64_any_dtype(final_merged_df[col]):
                    pass
        print("Conversión a numérico completada.")
    elif export_format or return_df:
        print("DataFrame final vacío, no se realiza conversión numérica.")

    if not final_merged_df.empty:
        _export_df(final_merged_df, 'final_fbref_all5_merged_data', season_str, export_format)
    elif export_format:
        print(f"DataFrame final vacío. No se guarda {export_format} para 'final_fbref_all5_merged_data'.")

    return final_merged_df if return_df else None
