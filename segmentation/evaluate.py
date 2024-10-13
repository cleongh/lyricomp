import os
import re
import string

import pandas as pd
import music21 as m21
import unicodedata

from baseline_algo import run_for_file

from escribir_fichero import escribir_en_fichero, reset_fichero, escribir_correcto

METADATA_XLS = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/Metadata template PTNERA.xlsx'
COPLAS_XLS = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/DIGIFOLK Ejemplos de coplas.xlsx'
DIR_XML_FILES = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera'

COL_ID = 'Id'
COL_OBRA = 'Obra'
COL_NOMBRE = 'Nombre Obra'
COL_VERSOS = 'Versos'

RANGE_TEST = range(5, 16)
DEBUG = True


def info_from_coplas_xls(coplas_xls, col_nombre, col_versos):
    df = pd.read_excel(coplas_xls, sheet_name=1)
    dict_title_lyrics = {}

    nombre = None
    for i, row in df.iterrows():
        if not pd.isna(row[col_nombre]): # usually the first line of the lyrics
            nombre = row[col_nombre].lower().strip() #if isinstance(row[col_nombre], str) else str(int(row[col_nombre]))
            #print(obra)
            versos = []
            versos.append(str(row[col_versos].strip()))
            dict_title_lyrics[nombre] = versos
        else:
            #dict_title_lyrics[nombre].append('' if pd.isna(row[col_versos]) else row[col_versos])
            if not pd.isna(row[col_versos]):
                dict_title_lyrics[nombre].append(row[col_versos])

    return dict_title_lyrics

def get_dict_file_title(metadata):
    dict_file_title = {}
    df = pd.read_excel(metadata, sheet_name=0)
    for i, row in df.iterrows():
        #print('******', i, row)
        if i >= 4 and not pd.isna(row.iloc[1]):
            dict_file_title[row.iloc[1]] = row.iloc[2].strip().lower()
    return dict_file_title


def get_title_from_xml(xml_file):
    data = m21.converter.parse(xml_file)
    #print(data)
    title = data.metadata.title
    return title


def hit(segmented, gold):
    if len(segmented) <= 0:
        return False
    for i, ls in enumerate(segmented):
        if clean_text(ls) != clean_text(gold[i]):
            return False
    return True

def hit_percentage(segmented, gold, percentage=1):

    verses = 0
    fails = 0

    if len(segmented) <= 0:
        return False
    for i, ls in enumerate(segmented):
        verses +=1
        if (len(gold) > i):
            if DEBUG: 
                escribir_en_fichero (clean_text(ls))
                escribir_en_fichero(clean_text(gold[i]))

            matched = False
            for ver in gold:
                if clean_text(ls) == clean_text(ver):
                    matched = True
            if not matched:
                fails += 1
        else: 
            break
    if (verses-fails)/verses >=percentage:
        if DEBUG: escribir_correcto("Percentage of fail: " + str((verses-fails)/verses) + ' ' + str(percentage))
        return True
    else: 
        if DEBUG: escribir_en_fichero("Percentage of fail: " + str((verses-fails)/verses) + ' ' + str(percentage))
        return False

def clean_text(text):
    return quitar_acentos(text.lower().replace('_', ' ').replace('¡', ' ').replace('!', ' ').translate(str.maketrans('','',string.punctuation)).strip())


def quitar_acentos(palabra):
    return ''.join((c for c in unicodedata.normalize('NFD', palabra) if unicodedata.category(c) != 'Mn'))

def match_with_filename(metadata, dir_music_files, coplas_xls, col_nombre, col_versos):
    dict_title_lyrics = info_from_coplas_xls(coplas_xls, col_nombre, col_versos)
    dict_file_title = get_dict_file_title(metadata)
    dict_title_all = {}

    count_title_no_match = 0

    for filename in os.listdir(dir_music_files):
        if not filename.endswith('.xml'):
            continue
        f = os.path.join(dir_music_files, filename)
        just_name = filename.split('.')[0]
        title = dict_file_title[just_name]
        if title:
            title = title.strip().lower()
            if title in dict_title_lyrics:
                dict_title_all[title] = (dir_music_files + '/' + filename, dict_title_lyrics[title])
            else:
                #print('NO MATCH', title)
                count_title_no_match += 1

    print('FILENAME TITLE MATCHES =', len(dict_title_all))
    print('TITLE BUT NO MATCH =', count_title_no_match)
    return dict_title_all


def match_with_metadata(metadata, dir_music_files, coplas_xls, col_nombre, col_versos):
    dict_title_lyrics = info_from_coplas_xls(coplas_xls, col_nombre, col_versos)
    dict_title_all = {}

    count_no_title = 0
    count_title_no_match = 0

    for filename in os.listdir(dir_music_files):
        if not filename.endswith('.xml'):
            continue
        f = os.path.join(dir_music_files, filename)
        title = get_title_from_xml(f)
        if title:
            title = re.sub(r'^\d+\.\s*', '', title).lower()
            if title in dict_title_lyrics:
                dict_title_all[title] = (dir_music_files + '/' + filename, dict_title_lyrics[title])
            else:
                #print('NO MATCH', title)
                count_title_no_match += 1
        else:
            count_no_title += 1

    print('METADATA TITLE MATCHES =', len(dict_title_all))

    print('XML WITH NO TITLE =', count_no_title)
    print('TITLE BUT NO MATCH =', count_title_no_match)
    return dict_title_all



if __name__ == "__main__":
    reset_fichero()
    dict_title_all = match_with_filename(METADATA_XLS, DIR_XML_FILES, COPLAS_XLS, COL_NOMBRE, COL_VERSOS)
    #dict_title_all = match_with_metadata(METADATA_XLS, DIR_XML_FILES, COPLAS_XLS, COL_NOMBRE, COL_VERSOS)

    count_hits = 0
    for k, v in dict_title_all.items():

        escribir_en_fichero('NEW LYRIC-------------------------------' + '########## FILE' + v[0])
        print('########## FILE', v[0])
        segmented = run_for_file(v[0], RANGE_TEST, result='list', debug=DEBUG)
        #segmented = run_for_file_r(v[0], RANGE_TEST, result='list', debug=DEBUG)
        gold = v[1]
        

        if hit_percentage(segmented, gold, percentage=0.5):
            print('HIT')
            count_hits += 1

            escribir_correcto('!!!HIT:'+ k + '!!!')
            escribir_correcto( 'SEGMENTED:')
            for i in segmented:
                escribir_correcto( i)
            escribir_correcto( 'GOLD:')

            for i in v[1]:
                escribir_correcto( i)

        elif DEBUG:
            print('!!! NO-HIT:', k, '!!!')
            print('SEGMENTED:')
            print(segmented)
            print('GOLD:')
            print(v[1])
        #Write in file to check the errors
            escribir_en_fichero('!!!No-HIT:'+ k + '!!!')
            escribir_en_fichero( 'SEGMENTED:')
            for i in segmented:
                escribir_en_fichero( i)
            escribir_en_fichero( 'GOLD:')

            for i in v[1]:
                escribir_en_fichero( i)


    print('##########')
    print('HITS:', count_hits, format(count_hits / len(dict_title_all), '.0%'))