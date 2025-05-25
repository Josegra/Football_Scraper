from datetime import datetime
import requests
import pandas as pd
from unidecode import unidecode
import os

# --- Helper Function ---
def _get_season_string(start_year=None):
    if start_year is None:
        year_to_use = datetime.now().year - 1
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
        # Asegurarse de que requests usa https
        if not url.startswith("https://"):
            print(f"Advertencia: La URL {url} no usa HTTPS. Intentando con HTTPS.")
            if url.startswith("http://"):
                url = url.replace("http://", "https://", 1)
            else: # Asumir que es un dominio sin protocolo
                 print(f"Advertencia: URL {url} sin protocolo, se asume https.")
                 # Esto es un intento, podría fallar si el formato es inesperado.
                 # Para FBRef, generalmente es seguro asumir que el dominio es correcto y solo falta https.
                 # Pero si la url fuera 'fbref.com/foo' sin 'en/comps/...' podría ser problemático.
                 # Dado el contexto de las URLs usadas, esto debería ser seguro.

        # Utilizar un User-Agent para simular un navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15) # timeout de 15 segundos
        response.raise_for_status() # Levanta un error para códigos 4xx/5xx

        # Leer directamente el contenido de la respuesta
        dfs = pd.read_html(response.content)
        if not dfs:
            print(f"No se encontraron tablas en {url}")
            return pd.DataFrame()
        df = dfs[0] # Asumir que la primera tabla es la deseada

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
    except requests.exceptions.RequestException as e:
        print(f"Error de red o HTTP al leer datos de {url}: {e}")
        return pd.DataFrame()
    except ValueError as ve: # pd.read_html puede lanzar ValueError si no hay tablas
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
    for col in ['Gls', 'Ast', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR','xG', 'npxG', 'xA', 'npxG+xA', 'G+A', 'xAG', 'npxG+xAG']: #Añadidas más columnas que podrían estar duplicadas
        if col in df.columns: # Verificar si la columna existe antes de intentar renombrar
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
        if col_target in df.columns: # Verificar si la columna existe
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
        if col_target in df.columns: # Verificar si la columna existe
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
        if col_target in df.columns: # Verificar si la columna existe
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
    if 'Out' in df.columns: # Verificar si la columna existe
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
    if 'On-Off' in df.columns: # Verificar si la columna existe
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
    for func in stat_funcs_ordered:
        print(f"Obteniendo datos de: {func.__name__}...")
        df = func(start_year=start_year, return_df=True)
        if df is not None and not df.empty:
            dfs_list.append(df)
            print(f"Datos de {func.__name__} obtenidos exitosamente. Columnas: {list(df.columns[:5])}...") # Muestra primeras 5 cols
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

    # Iniciar con el primer DataFrame no vacío
    final_merged_df = pd.DataFrame()
    initial_df_found = False
    for i, df in enumerate(all_dfs):
        if not df.empty:
            final_merged_df = df.copy()
            initial_df_found = True
            all_dfs = all_dfs[i+1:] # Resto de DFs para mergear
            print(f"DataFrame inicial para merge: {type(all_dfs[0] if all_dfs else None).__name__ if all_dfs else 'N/A'} (basado en el primer DF no vacío)")
            break
    
    if not initial_df_found:
        print(f"Todos los DataFrames obtenidos están vacíos para {season_str}. No se puede mergear.")
        if return_df: return pd.DataFrame()
        return None


    for df_to_add in all_dfs:
        if df_to_add.empty:
            # print(f"Omitiendo un DataFrame vacío en la lista de merge.") # Menos verboso
            continue
        if 'PlSqu' in df_to_add.columns and 'PlSqu' in final_merged_df.columns:
            cols_to_drop_from_new_df = [c for c in df_to_add.columns if c in final_merged_df.columns and c != 'PlSqu']
            # Asegurar que no se dropea 'PlSqu' si es la única columna común
            if 'PlSqu' in cols_to_drop_from_new_df : cols_to_drop_from_new_df.remove('PlSqu')

            df_cleaned = df_to_add.drop(columns=cols_to_drop_from_new_df, errors='ignore')

            if not df_cleaned.empty:
                # print(f"Mergeando con DataFrame que tiene columnas: {list(df_cleaned.columns[:5])}...") # Debug
                # Antes del merge, verificar si 'PlSqu' está vacío o tiene NaNs y cuántos
                # if df_cleaned['PlSqu'].isnull().any(): print(f"Advertencia: 'PlSqu' en df_cleaned tiene {df_cleaned['PlSqu'].isnull().sum()} NaNs antes del merge.")
                # if final_merged_df['PlSqu'].isnull().any(): print(f"Advertencia: 'PlSqu' en final_merged_df tiene {final_merged_df['PlSqu'].isnull().sum()} NaNs antes del merge.")
                
                final_merged_df = pd.merge(final_merged_df, df_cleaned, on='PlSqu', how='inner')
                # print(f"Tamaño después del merge: {final_merged_df.shape}") # Debug
            else:
                print(f"Advertencia: Un DataFrame intermedio quedó vacío después de limpiar columnas duplicadas (excepto PlSqu) y fue omitido.")
        else:
            print(f"Advertencia: Un DataFrame intermedio no contiene 'PlSqu' (o el principal no lo tiene) y fue omitido del merge.")

    if final_merged_df.empty:
        print(f"El DataFrame fusionado (antes de maestro) está vacío para {season_str}.")
    else:
        print(f"DataFrame fusionado (antes de maestro) tiene {final_merged_df.shape[0]} filas y {final_merged_df.shape[1]} columnas.")
        # --- Limpieza de Datos Post-Merge (Naciones, Comp, Edad) ---
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

        # --- Merge con DataFrame Maestro (players.csv) ---
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
            
            # ASUNCIÓN: Generar 'player_code' en df_maestro si no existe o para asegurar consistencia
            if 'name' in df_maestro.columns: # Asumiendo que 'name' es la columna de nombres en players.csv
                 df_maestro['player_code'] = df_maestro['name'].apply(generar_player_code_para_fbref)
            elif 'player_code' not in df_maestro.columns:
                print("Error crítico: 'players.csv' no tiene columna 'name' para generar 'player_code', ni 'player_code' preexistente.")
                # No continuar con este merge si no hay clave
            
            if 'player_code' in df_maestro.columns and 'player_code' in final_merged_df.columns:
                columnas_maestro_seleccionadas = [
                    'player_code', 'sub_position', 'current_club_name',
                    'market_value_in_eur', 'last_season',
                    'foot', 'height_in_cm', 'contract_expiration_date'
                ]
                columnas_maestro_existentes = [col for col in columnas_maestro_seleccionadas if col in df_maestro.columns]
                
                if 'player_code' not in columnas_maestro_existentes: # Doble check por si player_code fue droppeado o no seleccionado
                    print("Error Crítico: 'player_code' no está en las columnas seleccionadas del maestro para el cruce.")
                else:
                    df_maestro_filtrado = df_maestro[columnas_maestro_existentes].drop_duplicates(subset='player_code', keep='first')
                    
                    # Antes de mergear, verificar valores únicos y duplicados en 'player_code'
                    # print(f"Debug: player_code unique in final_merged_df: {final_merged_df['player_code'].nunique()} / {len(final_merged_df)}")
                    # print(f"Debug: player_code unique in df_maestro_filtrado: {df_maestro_filtrado['player_code'].nunique()} / {len(df_maestro_filtrado)}")

                    final_merged_df = final_merged_df.merge(
                        df_maestro_filtrado,
                        on='player_code',
                        how='left',
                        suffixes=('', '_maestro')
                    )
                    cols_a_consolidar = list(set(columnas_maestro_existentes) - {'player_code'})
                    for col_base in cols_a_consolidar:
                        if col_base + '_maestro' in final_merged_df.columns:
                            # Priorizar la información del maestro si existe, sino mantener la original (si la hubiera con el mismo nombre)
                            final_merged_df[col_base] = final_merged_df[col_base + '_maestro'].fillna(final_merged_df.get(col_base))
                            final_merged_df.drop(columns=[col_base + '_maestro'], inplace=True, errors='ignore')
                        # Si la columna base original no existía y ahora sí (traída del maestro), está bien.
                        # Si existía y no hubo colisión (no se creó _maestro), también está bien.
                    print("Cruce con archivo maestro realizado correctamente.")
            else:
                 print("Error: 'player_code' no está disponible en ambos DataFrames para el cruce con el maestro.")

        except FileNotFoundError:
            print("Error: players.csv no encontrado en la URL especificada.")
        except KeyError as ke:
            print(f"Error: columna faltante durante el merge o preparación del maestro: {ke}")
        except Exception as e:
            print(f"Error inesperado durante el merge con el maestro: {e}")

    # --- INICIO: Conversión a formato numérico adecuado ---
    if not final_merged_df.empty:
        print("Convirtiendo columnas a formato numérico adecuado...")
        exclude_cols = [
            'Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Born', 'foot',
            'contract_expiration_date', 'player_code', 'sub_position', 'current_club_name',
            'PlSqu',  # Clave de string usada para merges internos
            'Age'     # Columna original de edad tipo string "YY-DDD", DecimalAge es la numérica
        ]

        for col in final_merged_df.columns:
            if col not in exclude_cols:
                # Comprobar si la columna es de tipo objeto o string antes de convertir
                # para evitar intentar convertir columnas ya numéricas innecesariamente
                # o columnas de fecha/hora que podrían necesitar un manejo diferente (aunque pd.to_numeric las pasaría a NaN con coerce)
                if final_merged_df[col].dtype == 'object' or pd.api.types.is_string_dtype(final_merged_df[col]):
                    final_merged_df[col] = pd.to_numeric(final_merged_df[col], errors='coerce')
                elif pd.api.types.is_datetime64_any_dtype(final_merged_df[col]):
                    # Si tienes columnas de fecha/hora que no están en exclude_cols y no quieres convertirlas a NaN:
                    # print(f"Columna {col} es de tipo fecha/hora y no está en exclude_cols. Se omitirá la conversión a numérico.")
                    pass # O maneja específicamente
        print("Conversión a numérico completada.")
    elif export_format or return_df: # Solo imprimir si se esperaba una acción
        print("DataFrame final vacío, no se realiza conversión numérica.")
    # --- FIN: Conversión a formato numérico adecuado ---

    # Exportar o devolver
    if not final_merged_df.empty:
        _export_df(final_merged_df, 'final_fbref_all5_merged_data', season_str, export_format) # Nombre de archivo actualizado
    elif export_format: # Solo imprimir si se esperaba exportar y está vacío
        print(f"DataFrame final vacío. No se guarda {export_format} para 'final_fbref_all5_merged_data'.")

    return final_merged_df if return_df else None
