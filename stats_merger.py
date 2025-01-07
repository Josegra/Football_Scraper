def standard_stats(export_format='csv', return_df=False):
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
    # cleaning 
    dfdata = df[1]
    dfstandard = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

    # Convert string to float 
    dfstandard['90s'] = dfstandard['90s'].astype(float)
    dfstandard['Gls'] = dfstandard['Gls'].astype(float)
    dfstandard['Ast'] = dfstandard['Ast'].astype(float)
    dfstandard['G-PK'] = dfstandard['G-PK'].astype(float)
    dfstandard['PK'] = dfstandard['PK'].astype(float)
    dfstandard['PKatt'] = dfstandard['PKatt'].astype(float)
    dfstandard['CrdY'] = dfstandard['CrdY'].astype(float)
    dfstandard['CrdR'] = dfstandard['CrdR'].astype(float)
    dfstandard['G+A'] = dfstandard['G+A'].astype(float)
    dfstandard['G+A-PK'] = dfstandard['G+A-PK'].astype(float)
    dfstandard['xG'] = dfstandard['xG'].astype(float)
    dfstandard['npxG'] = dfstandard['npxG'].astype(float)
    dfstandard['npxG+xAG'] = dfstandard['npxG+xAG'].astype(float)
    dfstandard['xG+xAG'] = dfstandard['xG+xAG'].astype(float)
    dfstandard['npxG+xAG'] = dfstandard['npxG+xAG'].astype(float)

    # Duplicate columns but not the first 
    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'Gls':
            cols.append(f'Gls_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'Ast':
            cols.append(f'Ast_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'G-PK':
            cols.append(f'G-PK_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'xG':
            cols.append(f'xG_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'npxG':
            cols.append(f'npxG_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'xA':
            cols.append(f'xA_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'npxG+xA':
            cols.append(f'npxG+xA_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'G+A':
            cols.append(f'G+A_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'xAG':
            cols.append(f'xAG_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    cols = []
    count = 1
    for column in dfstandard.columns:
        if column == 'npxG+xAG':
            cols.append(f'npxG+xAG_{count}')
            count+=1
            continue
        cols.append(column)
    dfstandard.columns = cols

    ## Cleaning 
    dfstandard['PlSqu'] = dfstandard['Player'] + dfstandard['Squad']
    dfstandard['Player'] = dfstandard['Player'].apply(unidecode)
    dfstandard['Squad'] = dfstandard['Squad'].apply(unidecode)
    dfstandard.drop(columns='Matches', inplace=True)

    # Cambiando nombre de las columnas 
    dfstandard.columns = [
        col.replace('_1', '') if '_1' in col else
        col.replace('_2', '_p90') if '_2' in col else
        col + '_p90' if col in ['G+A-PK', 'xG+xAG'] else
        col
        for col in dfstandard.columns
    ]

    # Define the file path and export based on format
    if export_format == 'csv':
        file_path = 'fbrefBig5standard.csv'
        dfstandard.to_csv(file_path, encoding='utf-8', index=False)
    elif export_format == 'excel':
        file_path = 'fbrefBig5standard.xlsx'
        dfstandard.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print the file path and confirmation message
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, the data has been scraped and saved.")

    # Return DataFrame if requested
    if return_df:
        return dfstandard

def shooting_stats(export_format='csv', return_df=False):
    import requests
    import pandas as pd
    from unidecode import unidecode
    import os
    # URL
    url = 'https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats'
    html_content = requests.get(url).text.replace('<!--', '').replace('-->', '')
    df = pd.read_html(html_content)
    
    # Clean the age columns
    df[1].columns = df[1].columns.droplevel(0)  # drop top header row
    dfdata = df[1]
    dfshoot = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)
    
    # Convert to strings and to float
    dfshoot['90s'] = dfshoot['90s'].astype(float)
    dfshoot['Gls'] = dfshoot['Gls'].astype(float)
    dfshoot['Sh'] = dfshoot['Sh'].astype(float)
    dfshoot['SoT'] = dfshoot['SoT'].astype(float)
    dfshoot['SoT%'] = dfshoot['SoT%'].astype(float)
    dfshoot['Sh/90'] = dfshoot['Sh/90'].astype(float)
    dfshoot['SoT/90'] = dfshoot['SoT/90'].astype(float)
    dfshoot['G/Sh'] = dfshoot['G/Sh'].astype(float)
    dfshoot['G/SoT'] = dfshoot['G/SoT'].astype(float)
    dfshoot['Dist'] = dfshoot['Dist'].astype(float)
    dfshoot['FK'] = dfshoot['FK'].astype(float)
    dfshoot['PK'] = dfshoot['PK'].astype(float)
    dfshoot['PKatt'] = dfshoot['PKatt'].astype(float)
    dfshoot['xG'] = dfshoot['xG'].astype(float)
    dfshoot['npxG'] = dfshoot['npxG'].astype(float)
    dfshoot['npxG/Sh'] = dfshoot['npxG/Sh'].astype(float)
    dfshoot['G-xG'] = dfshoot['G-xG'].astype(float)
    dfshoot['np:G-xG'] = dfshoot['np:G-xG'].astype(float)

    # Drop Matches
    dfshoot.drop(columns='Matches', inplace=True)
    
    # Key and final touches
    dfshoot['PlSqu'] = dfshoot['Player'] + dfshoot['Squad']
    dfshoot['Player'] = dfshoot['Player'].apply(unidecode)
    dfshoot['Squad'] = dfshoot['Squad'].apply(unidecode)

    # Define the file path and export based on format
    if export_format == 'csv':
        file_path = 'fbrefBig5Shoot.csv'
        dfshoot.to_csv(file_path, index=False)
    elif export_format == 'excel':
        file_path = 'fbrefBig5Shoot.xlsx'
        dfshoot.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print the file path and confirmation message
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, the shooting stats have been scraped and saved.")

    # Return DataFrame if requested
    if return_df:
        return dfshoot

def possession_stats(export_format='csv', return_df=False):
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

    # Convert to strings and to float
    dfpossession['90s'] = dfpossession['90s'].astype(float)
    dfpossession['Touches'] = dfpossession['Touches'].astype(float)
    dfpossession['Def Pen'] = dfpossession['Def Pen'].astype(float)
    dfpossession['Def 3rd'] = dfpossession['Def 3rd'].astype(float)
    dfpossession['Mid 3rd'] = dfpossession['Mid 3rd'].astype(float)
    dfpossession['Att 3rd'] = dfpossession['Att 3rd'].astype(float)
    dfpossession['Att Pen'] = dfpossession['Att Pen'].astype(float)
    dfpossession['Live'] = dfpossession['Live'].astype(float)
    dfpossession['Succ'] = dfpossession['Succ'].astype(float)
    dfpossession['Att'] = dfpossession['Att'].astype(float)
    dfpossession['Succ%'] = dfpossession['Succ%'].astype(float)
    dfpossession['Carries'] = dfpossession['Carries'].astype(float)
    dfpossession['TotDist'] = dfpossession['TotDist'].astype(float)
    dfpossession['PrgDist'] = dfpossession['PrgDist'].astype(float)
    dfpossession['1/3'] = dfpossession['1/3'].astype(float)
    dfpossession['CPA'] = dfpossession['CPA'].astype(float)
    dfpossession['Mis'] = dfpossession['Mis'].astype(float)
    dfpossession['Dis'] = dfpossession['Dis'].astype(float)
    dfpossession['Rec'] = dfpossession['Rec'].astype(float)

    # Rename duplicate columns but not the first
    cols = []
    count = 1
    for column in dfpossession.columns:
        if column == 'Prog':
            cols.append(f'Prog_{count}')
            count += 1
            continue
        cols.append(column)
    dfpossession.columns = cols

    # Clean data
    dfpossession['PlSqu'] = dfpossession['Player'] + dfpossession['Squad']
    dfpossession['Player'] = dfpossession['Player'].apply(unidecode)
    dfpossession['Squad'] = dfpossession['Squad'].apply(unidecode)

    # Drop Matches
    dfpossession.drop(columns='Matches', inplace=True)

    # Define the file path and export based on format
    if export_format == 'csv':
        file_path = 'fbrefBig5Possession.csv'
        dfpossession.to_csv(file_path, index=False)
    elif export_format == 'excel':
        file_path = 'fbrefBig5Possession.xlsx'
        dfpossession.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print the file path and confirmation message
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, the possession stats have been scraped and saved.")

    # Return DataFrame if requested
    if return_df:
        return dfpossession

def creation_stats(export_format='csv', return_df=False):
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

    # Convert to strings and to float
    dfcreation['90s'] = dfcreation['90s'].astype(float)
    dfcreation['SCA'] = dfcreation['SCA'].astype(float)
    dfcreation['PassLive'] = dfcreation['PassLive'].astype(float)
    dfcreation['PassDead'] = dfcreation['PassDead'].astype(float)
    dfcreation['Sh'] = dfcreation['Sh'].astype(float)
    dfcreation['Fld'] = dfcreation['Fld'].astype(float)
    dfcreation['Def'] = dfcreation['Def'].astype(float)
    dfcreation['GCA'] = dfcreation['GCA'].astype(float)

    # Rename duplicate columns but not the first
    cols = []
    count = 1
    for column in dfcreation.columns:
        if column == 'PassLive':
            cols.append(f'PassLive_{count}')
            count += 1
            continue
        cols.append(column)
    dfcreation.columns = cols

    # Renaming PassDead
    cols = []
    count = 1
    for column in dfcreation.columns:
        if column == 'PassDead':
            cols.append(f'PassDead_{count}')
            count += 1
            continue
        cols.append(column)
    dfcreation.columns = cols

    # Renaming Drib
    cols = []
    count = 1
    for column in dfcreation.columns:
        if column == 'Drib':
            cols.append(f'Drib_{count}')
            count += 1
            continue
        cols.append(column)
    dfcreation.columns = cols

    # Renaming Sh
    cols = []
    count = 1
    for column in dfcreation.columns:
        if column == 'Sh':
            cols.append(f'Sh_{count}')
            count += 1
            continue
        cols.append(column)
    dfcreation.columns = cols

    # Renaming Fld
    cols = []
    count = 1
    for column in dfcreation.columns:
        if column == 'Fld':
            cols.append(f'Fld_{count}')
            count += 1
            continue
        cols.append(column)
    dfcreation.columns = cols

    # Renaming Def
    cols = []
    count = 1
    for column in dfcreation.columns:
        if column == 'Def':
            cols.append(f'Def_{count}')
            count += 1
            continue
        cols.append(column)
    dfcreation.columns = cols

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

    # Define the file path and export based on format
    if export_format == 'csv':
        file_path = 'fbrefBig5Creation.csv'
        dfcreation.to_csv(file_path, index=False)
    elif export_format == 'excel':
        file_path = 'fbrefBig5Creation.xlsx'
        dfcreation.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print the file path and confirmation message
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, the creation stats have been scraped and saved.")

    # Return DataFrame if requested
    if return_df:
        return dfcreation

def defense_stats(export_format='csv', return_df=False):
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

    # Convert to strings and to float
    dfdefense['90s'] = dfdefense['90s'].astype(float)
    dfdefense['Tkl'] = dfdefense['Tkl'].astype(float)
    dfdefense['TklW'] = dfdefense['TklW'].astype(float)
    dfdefense['Def 3rd'] = dfdefense['Def 3rd'].astype(float)
    dfdefense['Mid 3rd'] = dfdefense['Mid 3rd'].astype(float)
    dfdefense['Att 3rd'] = dfdefense['Att 3rd'].astype(float)
    dfdefense['Att'] = dfdefense['Att'].astype(float)
    dfdefense['Tkl%'] = dfdefense['Tkl%'].astype(float)
    dfdefense['Blocks'] = dfdefense['Blocks'].astype(float)
    dfdefense['Sh'] = dfdefense['Sh'].astype(float)
    dfdefense['Pass'] = dfdefense['Pass'].astype(float)
    dfdefense['Int'] = dfdefense['Int'].astype(float)
    dfdefense['Tkl+Int'] = dfdefense['Tkl+Int'].astype(float)
    dfdefense['Clr'] = dfdefense['Clr'].astype(float)
    dfdefense['Err'] = dfdefense['Err'].astype(float)

    # Rename duplicate columns but not the first
    cols = []
    count = 1
    for column in dfdefense.columns:
        if column == 'Def 3rd':
            cols.append(f'Def 3rd_{count}')
            count += 1
            continue
        cols.append(column)
    dfdefense.columns = cols

    # Renaming Mid 3rd
    cols = []
    count = 1
    for column in dfdefense.columns:
        if column == 'Mid 3rd':
            cols.append(f'Mid 3rd_{count}')
            count += 1
            continue
        cols.append(column)
    dfdefense.columns = cols

    # Renaming Att 3rd
    cols = []
    count = 1
    for column in dfdefense.columns:
        if column == 'Att 3rd':
            cols.append(f'Att 3rd_{count}')
            count += 1
            continue
        cols.append(column)
    dfdefense.columns = cols

    # Renaming Tkl
    cols = []
    count = 1
    for column in dfdefense.columns:
        if column == 'Tkl':
            cols.append(f'Tkl_{count}')
            count += 1
            continue
        cols.append(column)
    dfdefense.columns = cols

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

    # Define the file path and export based on format
    if export_format == 'csv':
        file_path = 'fbrefBig5Defense.csv'
        dfdefense.to_csv(file_path, index=False)
    elif export_format == 'excel':
        file_path = 'fbrefBig5Defense.xlsx'
        dfdefense.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print the file path and confirmation message
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, the defense stats have been scraped and saved.")

    # Return DataFrame if requested
    if return_df:
        return dfdefense

def passing_stats(export_format='csv', return_df=False):
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

    # Convert to strings and to float
    dfPassing['90s'] = dfPassing['90s'].astype(float)
    dfPassing['Cmp'] = dfPassing['Cmp'].astype(float)
    dfPassing['Att'] = dfPassing['Att'].astype(float)
    dfPassing['Cmp%'] = dfPassing['Cmp%'].astype(float)
    dfPassing['TotDist'] = dfPassing['TotDist'].astype(float)
    dfPassing['PrgDist'] = dfPassing['PrgDist'].astype(float)
    dfPassing['Ast'] = dfPassing['Ast'].astype(float)
    dfPassing['xA'] = dfPassing['xA'].astype(float)
    dfPassing['KP'] = dfPassing['KP'].astype(float)
    dfPassing['1/3'] = dfPassing['1/3'].astype(float)
    dfPassing['PPA'] = dfPassing['PPA'].astype(float)
    dfPassing['CrsPA'] = dfPassing['CrsPA'].astype(float)

    # Rename duplicate columns but not the first
    cols = []
    count = 1
    for column in dfPassing.columns:
        if column == 'Cmp':
            cols.append(f'Cmp_{count}')
            count += 1
            continue
        cols.append(column)
    dfPassing.columns = cols

    # Renaming Att columns
    cols = []
    count = 1
    for column in dfPassing.columns:
        if column == 'Att':
            cols.append(f'Att_{count}')
            count += 1
            continue
        cols.append(column)
    dfPassing.columns = cols

    # Renaming Cmp% columns
    cols = []
    count = 1
    for column in dfPassing.columns:
        if column == 'Cmp%':
            cols.append(f'Cmp%_{count}')
            count += 1
            continue
        cols.append(column)
    dfPassing.columns = cols

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

    # Define the file path and export based on format
    if export_format == 'csv':
        file_path = 'fbrefBig5Passing.csv'
        dfPassing.to_csv(file_path, index=False)
    elif export_format == 'excel':
        file_path = 'fbrefBig5Passing.xlsx'
        dfPassing.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print the file path and confirmation message
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, the passing stats have been scraped and saved.")

    # Return DataFrame if requested
    if return_df:
        return dfPassing

def passing_type_stats(export_format='csv', return_df=False):
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

    # Convert to strings and to float
    dfpassingtypes['90s'] = dfpassingtypes['90s'].astype(float)
    dfpassingtypes['Att'] = dfpassingtypes['Att'].astype(float)
    dfpassingtypes['Live'] = dfpassingtypes['Live'].astype(float)
    dfpassingtypes['Dead'] = dfpassingtypes['Dead'].astype(float)
    dfpassingtypes['FK'] = dfpassingtypes['FK'].astype(float)
    dfpassingtypes['TB'] = dfpassingtypes['TB'].astype(float)
    dfpassingtypes['Sw'] = dfpassingtypes['Sw'].astype(float)
    dfpassingtypes['Crs'] = dfpassingtypes['Crs'].astype(float)
    dfpassingtypes['CK'] = dfpassingtypes['CK'].astype(float)
    dfpassingtypes['In'] = dfpassingtypes['In'].astype(float)
    dfpassingtypes['Out'] = dfpassingtypes['Out'].astype(float)
    dfpassingtypes['Str'] = dfpassingtypes['Str'].astype(float)
    dfpassingtypes['TI'] = dfpassingtypes['TI'].astype(float)
    dfpassingtypes['Cmp'] = dfpassingtypes['Cmp'].astype(float)
    dfpassingtypes['Off'] = dfpassingtypes['Off'].astype(float)
    dfpassingtypes['Blocks'] = dfpassingtypes['Blocks'].astype(float)

    # Rename duplicate columns but not the first
    cols = []
    count = 1
    for column in dfpassingtypes.columns:
        if column == 'Out':
            cols.append(f'Out_{count}')
            count += 1
            continue
        cols.append(column)
    dfpassingtypes.columns = cols

    # Drop the Matches column
    dfpassingtypes.drop(columns='Matches', inplace=True)

    # Concatenate Player and Squad columns
    dfpassingtypes['PlSqu'] = dfpassingtypes['Player'] + dfpassingtypes['Squad']
    dfpassingtypes['Player'] = dfpassingtypes['Player'].apply(unidecode)
    dfpassingtypes['Squad'] = dfpassingtypes['Squad'].apply(unidecode)

    # Define the file path and export
    if export_format == 'csv':
        file_path = 'fbrefBig5PassingType.csv'
        dfpassingtypes.to_csv(file_path, index=False)
    elif export_format == 'excel':
        file_path = 'fbrefBig5PassingType.xlsx'
        dfpassingtypes.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print confirmation
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, the passing type stats have been scraped and saved.")

    # Return DataFrame if requested
    if return_df:
        return dfpassingtypes

def playing_time_stats(export_format='csv', return_df=False):
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

    # Convert columns to float
    dfplayingtime['90s'] = dfplayingtime['90s'].astype(float)
    dfplayingtime['Starts'] = dfplayingtime['Starts'].astype(float)
    dfplayingtime['Mn/Start'] = dfplayingtime['Mn/Start'].astype(float)
    dfplayingtime['Compl'] = dfplayingtime['Compl'].astype(float)
    dfplayingtime['Subs'] = dfplayingtime['Subs'].astype(float)
    dfplayingtime['Mn/Sub'] = dfplayingtime['Mn/Sub'].astype(float)
    dfplayingtime['unSub'] = dfplayingtime['unSub'].astype(float)
    dfplayingtime['PPM'] = dfplayingtime['PPM'].astype(float)
    dfplayingtime['onG'] = dfplayingtime['onG'].astype(float)
    dfplayingtime['onGA'] = dfplayingtime['onGA'].astype(float)
    dfplayingtime['+/-'] = dfplayingtime['+/-'].astype(float)
    dfplayingtime['+/-90'] = dfplayingtime['+/-90'].astype(float)
    dfplayingtime['On-Off'] = dfplayingtime['On-Off'].astype(float)
    dfplayingtime['onxG'] = dfplayingtime['onxG'].astype(float)
    dfplayingtime['onxGA'] = dfplayingtime['onxGA'].astype(float)
    dfplayingtime['xG+/-'] = dfplayingtime['xG+/-'].astype(float)
    dfplayingtime['xG+/-90'] = dfplayingtime['xG+/-90'].astype(float)

    # Rename duplicate columns but not the first
    cols = []
    count = 1
    for column in dfplayingtime.columns:
        if column == 'Onn-Off':
            cols.append(f'On-Off_{count}')
            count += 1
            continue
        cols.append(column)
    dfplayingtime.columns = cols

    # Drop the Matches column
    dfplayingtime.drop(columns='Matches', inplace=True)

    # Concatenate Player and Squad columns
    dfplayingtime['PlSqu'] = dfplayingtime['Player'] + dfplayingtime['Squad']
    dfplayingtime['Player'] = dfplayingtime['Player'].apply(unidecode)
    dfplayingtime['Squad'] = dfplayingtime['Squad'].apply(unidecode)

    # Define the file path and export
    if export_format == 'csv':
        file_path = 'fbrefBig5PlayingTime.csv'
        dfplayingtime.to_csv(file_path, index=False)
    elif export_format == 'excel':
        file_path = 'fbrefBig5PlayingTime.xlsx'
        dfplayingtime.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print confirmation
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, the playing time stats have been scraped and saved.")

    # Return DataFrame if requested
    if return_df:
        return dfplayingtime

def scrape_all_stats(export_format='csv'):
    # Execute each scraping function
    print("Starting to scrape shooting stats...")
    shooting_stats(export_format)
    
    print("Starting to scrape defense stats...")
    defense_stats(export_format)
    
    print("Starting to scrape passing stats...")
    passing_stats(export_format)
    
    print("Starting to scrape passing type stats...")
    passing_type_stats(export_format)
    
    print("Starting to scrape playing time stats...")
    playing_time_stats(export_format)
    
    print("Starting to scrape standard stats...")
    standard_stats(export_format)
    
    print("Starting to scrape possession stats...")
    possession_stats(export_format)
    
    print("Starting to scrape creation stats...")
    creation_stats(export_format)
    
    print("All stats have been scraped and saved.")

def merger_5leagues(export_format='csv', return_df=False):
    ## Leer los CSV 
    import pandas as pd
    import numpy as np
    import os
    df0 = pd.read_csv('fbrefBig5standard.csv', encoding='latin-1')
    df1 = pd.read_csv('fbrefBig5Shoot.csv', encoding='latin-1')
    df2 = pd.read_csv('fbrefBig5passing.csv', encoding='latin-1')
    df3 = pd.read_csv('fbrefBig5PassingType.csv', encoding='latin-1')
    df4 = pd.read_csv('fbrefBig5Creation.csv', encoding='latin-1')
    df5 = pd.read_csv('fbrefBig5defense.csv', encoding='latin-1')
    df6 = pd.read_csv('fbrefBig5Possession.csv', encoding='latin-1')
    df7 = pd.read_csv('fbrefBig5PlayingTime.csv', encoding='latin-1')


    ## Renombrar los CSV

    player_stand_stats = df0
    player_shoot_stats = df1
    player_pass_stats = df2
    player_passtypes_stats = df3
    player_ga_stats = df4
    player_defense_stats = df5
    player_possession_stats = df6
    player_time_stats = df7

    ## Union de Standart con Shooting
    merged_df = pd.merge(
        player_stand_stats,
        player_shoot_stats,
        on='PlSqu',
        how='inner',
        suffixes=('_stand', '_shoot')  # Sufijos para diferenciar columnas
    )

    # Identificar columnas duplicadas y mantener las de `player_stand_stats`
    columns_to_drop = [col for col in merged_df.columns if col.endswith('_shoot') and col[:-6] in player_stand_stats.columns]
    merged_df = merged_df.drop(columns=columns_to_drop)

    # Renombrar columnas para eliminar sufijos
    merged_df.columns = [col.replace('_stand', '') for col in merged_df.columns]
    
    ## Agregando Pass types

    final_merged_df = pd.merge(
        merged_df,
        player_pass_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_passing')
    )

    # Step 4: Clean up duplicates from the second merge
    columns_to_drop = [col for col in final_merged_df.columns if col.endswith('_passing') and col[:-8] in merged_df.columns]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    ## Player GA Stats

    final_merged_df = pd.merge(
        final_merged_df,
        player_ga_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_ga')
    )
    columns_to_drop = [
        col for col in final_merged_df.columns
        if col.endswith('_ga') and col[:-3] in final_merged_df.columns
    ]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    ## Player defense 

    # Merge `final_merged_df` with `player_defense_stats`
    final_merged_df = pd.merge(
        final_merged_df,
        player_defense_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_defense')
    )

    # Clean up duplicates from the merge
    columns_to_drop = [
        col for col in final_merged_df.columns
        if col.endswith('_defense') and col[:-8] in final_merged_df.columns
    ]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    ## Possession stats 

    # Merge `final_merged_df` with `player_possession_stats`
    final_merged_df = pd.merge(
        final_merged_df,
        player_possession_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_possession')
    )

    # Clean up duplicates from the merge
    columns_to_drop = [
        col for col in final_merged_df.columns
        if col.endswith('_possession') and col[:-11] in final_merged_df.columns
    ]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    ## Players with stats 

    final_merged_df = pd.merge(
        final_merged_df,
        player_time_stats,
        on='PlSqu',
        how='inner',
        suffixes=('', '_time')
    )

    # Clean up duplicates from the merge
    columns_to_drop = [
        col for col in final_merged_df.columns
        if col.endswith('_time') and col[:-5] in final_merged_df.columns
    ]
    final_merged_df = final_merged_df.drop(columns=columns_to_drop)

    # Define the file path and export based on format
    if export_format == 'csv':
        file_path = 'final_fbref_all5_columns.csv'
        final_merged_df.to_csv(file_path, index=False)
    elif export_format == 'excel':
        file_path = 'final_fbref_all5_columns.xlsx'
        final_merged_df.to_excel(file_path, index=False)
    else:
        print("Invalid export format. Please choose 'csv' or 'excel'.")
        return

    # Print the file path and confirmation message
    print(f"File has been saved at: {os.path.abspath(file_path)}")
    print("Done, all 5 leagues have been merged.")

    # Return DataFrame if requested
    if return_df:
        return final_merged_df
