import music21 as m21
import os
import unicodedata
import string

from escribir_fichero import escribir_en_fichero, escribir_correcto

#DIR = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera'
#FILE = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera/MX-1951-00-VM-00001.musicxml.xml'
#FILE = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera/MX-1951-00-VM-00016.musicxml.xml'
#FILE = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera/MX-1951-00-VM-00093.musicxml.xml'
#FILE = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera/MX-1951-00-VM-00182.musicxml.xml'
#FILE = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera/MX-1956-00-VM-01371.musicxml.xml'
#FILE = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera/MX-1951-00-VM-00048.musicxml.xml'
# 7 + 7 + 7 + 5?
#FILE = '/Users/alerom02/Documents/Proyectos/Mexico/lyricomp/Datos/xml_ptnera/MX-1951-00-VM-00072.musicxml.xml'

# Note: in Spanish, all single-syllable words are stressed, but in some lyrics they may not count as such...
DEBUG = True

SINGLE_CANNOT_END = [
    'a',
    'se',
    'de',
#    'por'
]

def xml_to_list(xml):
    """Convert a music xml file to a list of note events

    Args:
        xml (str or music21.stream.Score): Either a path to a music xml file or a music21.stream.Score

    Returns:
        score (list): A list of note events where each note is specified as
            ``[start, duration, pitch, velocity, label]``
    """

    if isinstance(xml, str):
        xml_data = m21.converter.parse(xml)
    elif isinstance(xml, m21.stream.Score):
        xml_data = xml
    else:
        raise RuntimeError('midi must be a path to a midi file or music21.stream.Score')

    score = []

    for part in xml_data.parts:
        instrument = part.getInstrument().instrumentName

        for note in part.flat.notes:

            if note.isChord:
                start = note.offset
                duration = note.quarterLength

                for chord_note in note.pitches:
                    pitch = chord_note.ps
                    volume = note.volume.realized
                    score.append([start, duration, pitch, volume, instrument])

            else:
                start = note.offset
                duration = note.quarterLength
                pitch = note.pitch.ps
                volume = note.volume.realized
                score.append([start, duration, pitch, volume, instrument])

    score = sorted(score, key=lambda x: (x[0], x[2]))
    return score


def xml_to_lyrics(xml, ties='start'):
    """Convert a music xml file to a list of syllables

    Args:
        xml (str or music21.stream.Score): Either a path to a music xml file or a music21.stream.Score
        ties (str): 'None', 'start', 'all', to add no/just starting/all tied notes

    Returns:
        score (list): A list of syllables and whether they are single, being, middle or end of word
            ``[text, syllabic]``
    """

    if isinstance(xml, str):
        xml_data = m21.converter.parse(xml)
    elif isinstance(xml, m21.stream.Score):
        xml_data = xml
    else:
        raise RuntimeError('midi must be a path to a midi file or music21.stream.Score')

    syllables = []

    for part in xml_data.parts:
        #instrument = part.getInstrument().instrumentName

        for note in part.flat.notes:
            if note.lyrics:
                text = note.lyrics[0].text
                syllabic = note.lyrics[0].syllabic
                if text and syllabic:
                    syllables.append((text, syllabic))

            #TODO: note without lyrics, which cannot be a tied, unless... it is the first of the tie?
            elif not note.isChord and not note.tie:
                if len(syllables) > 0:
                    syllables.append((syllables[-1][0], 'extend'))

            elif not note.isChord and note.tie:
                if (ties == 'start' and note.tie.type == 'start') or ties == 'all':
                    if len(syllables) > 0:
                        syllables.append((syllables[-1][0], 'extend'))

    return syllables
# Función para quitar los acentos de las vocales
def quitar_acentos(palabra):
    return ''.join((c for c in unicodedata.normalize('NFD', palabra) if unicodedata.category(c) != 'Mn'))

def clean_text(text):
    return text.lower().replace('_', ' ').replace('¡', ' ').replace('!', ' ').translate(str.maketrans('','',string.punctuation)).strip()


# Función para determinar si una palabra es aguda
def es_aguda(palabra, pos):

    palabra = clean_text(palabra)

    if len(palabra) == 0:
        return False
    
    if (pos == "single"):
        return True
    
    # Normalizamos la palabra y quitamos acentos para analizar la última letra
    palabra_sin_acentos = quitar_acentos(palabra)
    
    # Revisamos si tiene tilde en la última sílaba

    vocales = 'aeiouáéíóúü'
    
    # Busca todas las vocales en la palabra
    match = re.findall(r'[{}]'.format(vocales), palabra)

    if len(match) > 0:
        if match[-1] in "áéíóúÁÉÍÓÚ":
            return True
    
    
    # Si no tiene tilde, pero termina en vocal, 'n' o 's', no es aguda
    if palabra_sin_acentos[-1] in "aeiouAEIOU" or palabra_sin_acentos[-1] in "nNsS":
        return False
    
    # Si no termina en vocal, 'n' o 's', es aguda
    return True

def tiene_tilde(palabra):
    for letra in palabra:
        if letra in "áéíóúÁÉÍÓÚ":
            return True
    return False


def contar_silabas(palabra):
    """
    Cuenta el número de sílabas en una palabra basada en las secuencias de vocales.
    """
    palabra = palabra.lower()
    vocales = 'aeiouáéíóúü'
    
    # Encuentra todas las secuencias de vocales
    silabas = re.findall(r'[{}]+'.format(vocales), palabra)

    return len(silabas)

def recuperar_palabra_de_silaba (syllables, posSylaba):
    word = ''
    syl = syllables[posSylaba]
    
    if syl[1] == "single" or syl[1] == "extend" or syl[1] == "single":
        word = syl[0]
    
    if syl[1] == "begin":
        word += syl[0] 
        n = posSylaba + 1
        while n < len(syllables):
            word += syllables[n][0]

            if (syllables[n][1] == 'end'):
                break
            n += 1

    if syl[1] == "end":
        word += syl[0] 
        n = posSylaba - 1
        while n >= 0:
            word = syllables[n][0] + word
            if (syllables[n][1] == 'begin'):
                break
            n -= 1            
    
    if syl[1] == "middle":

        n = posSylaba - 1
        while n >= 0:
            word = syllables[n][0] + word

            if (syllables[n][1] == 'begin'):
                break   
            n -= 1

        word += syl[0] 

        n = posSylaba + 1
        while n < len(syllables):
            word += syllables[n][0]
            if (syllables[n][1] == 'end'):
                break 
            n += 1

    return word

def assemble_lyrics(syllables, breaks=None, options_asy =None, result='str'):
    lyrics = []
    line = ''
    count_sylables = 0
    asymetric = False
    options = ""
    print("breaks: " + str(breaks))
    if "A" in str(breaks):
        option_asy = int(breaks.split("-")[1])
        asymetric = True
        print (options_asy)
        options = options_asy[option_asy] 

    verse = 0
    
    for i, syl in enumerate(syllables):
        if asymetric:
            breaks = options[verse]
            print("breaks in " + str(breaks))
            print(options)
        if syl[0]:
            if syl[1] != 'extend':
                line += syl[0]
                count_sylables+=1
            if syl[1] == 'single' or syl[1] == 'end':
                line += ' '

            if breaks and (syl[1] == 'end' or syl[1] == 'single') and es_aguda(recuperar_palabra_de_silaba(syllables,i), syl[1]) and (count_sylables) % (breaks-1) == 0:
                lyrics.append(line.strip())
                line = ''
                count_sylables=0
                verse += 1
            elif breaks and (count_sylables) % breaks == 0 and (syl[1] == 'end' or syl[1] == 'single'):
                lyrics.append(line.strip())
                line = ''
                count_sylables=0
                verse += 1

    if line:
        lyrics.append(line.strip())

    return '\n'.join(lyrics) if result == 'str' else lyrics




    
def test_meters(syllables, test, discard_non_divisble=False, debug=False):
    possible = []

    if discard_non_divisble:
        test = [t for t in test if len(syllables) % t == 0] # >1?

    for m in test:
        x = (m-1)
        ok = True
        if debug: escribir_en_fichero('TEST =' + str(m))
        while x < len(syllables):
            first = syllables[x - m + 1]
            aguda = False
            
            add = 0
            for i in range(x - m + 1, x):
                if len(syllables) > i:
                    if (syllables[i][1] == 'extend'):
                        add+=1
            
            print (add)
            x+=add
            if (x>=len(syllables)):
                x=len(syllables)-1
                
            if ((syllables[x-1][1] == 'end' or syllables[x-1][1] == 'single') and es_aguda(recuperar_palabra_de_silaba(syllables,x-1), syllables[x-1][1])):
                aguda = True
                x=x-1


            last = syllables[x]


            if debug:
                escribir_en_fichero('FIRST ' +  str(x - m + 1) + ' ' +  first[0] + '| LAST' + str(x) + ' '+ last[0])

            if  first[1] == 'extend':
                break

            # must start with: begin or single
            if first[1] != 'begin' and first[1] != 'single':
                ok = False
                if debug: escribir_en_fichero('--IMPOSSIBLE START!')
                break

            if last[1] == 'middle' or last[1] == 'begin':
                ok = False
                if debug: escribir_en_fichero('--IMPOSSIBLE END! MoB')
                break
            # words that should not end lines
            if (last[1] == 'single' and last[0] in SINGLE_CANNOT_END) or ('\xa0' in last[0] and last[0].replace('\xa0', '') in SINGLE_CANNOT_END):
                ok = False
                if debug: escribir_en_fichero('--IMPOSSIBLE END!')
                break
            
            if (not aguda) and es_aguda(recuperar_palabra_de_silaba(syllables,x), syllables[x][1]):
                ok = False
                if debug: 
                    escribir_en_fichero('--IMPOSSIBLE END BECAUSE AGUDA!')
                    escribir_en_fichero(recuperar_palabra_de_silaba(syllables,x))
                    escribir_en_fichero("Es aguda: " + str(es_aguda(recuperar_palabra_de_silaba(syllables,x), syllables[x][1])))
                break
            #if (aguda):
            #    x += m -1
            #else:
            x += m
        if ok:
            if debug: escribir_en_fichero('OK' + str(m))
            #print(len(syllables) % m)
            possible.append(m)

    sorted_by_syllables_left = sorted(possible, key=lambda x: len(syllables) % x)
    #sorted_by_syllables_left = sorted(possible, key=lambda x: len(syllables))
    return sorted_by_syllables_left

def test_asymetric_meters(syllables, test, discard_non_divisble=False, debug=False):
    possible = []

    #return possible
    if discard_non_divisble:
        test = [t for t in test if len(syllables) % t == 0] # >1?

    verse=0
    option = 0
    for y in test:
        ok = False
        if (len(y)>verse):
            m = y[verse]
        else: 
            y[len(y)-1]
        #for m in y:

        x = (m-1)
        ok = True
        if debug: 
            escribir_en_fichero('TEST ASY=' + "A-" + str(option) + ": " + str(y))
        while x < len(syllables):

            first = syllables[x - m + 1]
            aguda = False
            if debug: 
                escribir_en_fichero('M: ' + str(m))
            add = 0
            for i in range(x - m + 1, x):
                if len(syllables) > i:
                    if (syllables[i][1] == 'extend'):
                        add+=1
            
            print (add)
            x+=add
            if (x>=len(syllables)):
                x=len(syllables)-1
                
            if ((syllables[x-1][1] == 'end' or syllables[x-1][1] == 'single') and es_aguda(recuperar_palabra_de_silaba(syllables,x-1), syllables[x-1][1])):
                aguda = True
                x=x-1


            last = syllables[x]


            if debug:
                escribir_en_fichero('FIRST ' +  str(x - m + 1) + ' ' +  first[0] + '| LAST' + str(x) + ' '+ last[0])

            if  first[1] == 'extend':
                break

            # must start with: begin or single
            if first[1] != 'begin' and first[1] != 'single':
                ok = False
                if debug: escribir_en_fichero('--IMPOSSIBLE START!')
                break

            if last[1] == 'middle' or last[1] == 'begin':
                ok = False
                if debug: escribir_en_fichero('--IMPOSSIBLE END! MoB')
                break
            # words that should not end lines
            if (last[1] == 'single' and last[0] in SINGLE_CANNOT_END) or ('\xa0' in last[0] and last[0].replace('\xa0', '') in SINGLE_CANNOT_END):
                ok = False
                if debug: escribir_en_fichero('--IMPOSSIBLE END!')
                break
            
            if (not aguda) and es_aguda(recuperar_palabra_de_silaba(syllables,x), syllables[x][1]):
                ok = False
                if debug: 
                    escribir_en_fichero('--IMPOSSIBLE END BECAUSE AGUDA!')
                    escribir_en_fichero(recuperar_palabra_de_silaba(syllables,x))
                    escribir_en_fichero("Es aguda: " + str(es_aguda(recuperar_palabra_de_silaba(syllables,x), syllables[x][1])))
                break
            #if (aguda):
            #    x += m -1
            #else:
            verse+=1
            if (len(y)>verse):
                m = y[verse]
            else: 
                y[len(y)-1]
            x += m


        if ok:
            if debug: escribir_en_fichero('OK' + str(option))
            #print(len(syllables) % m)
            possible.append("A-" + str(option))

        option +=1
    sorted_by_syllables_left = sorted(possible, key=lambda x: len(syllables))
    #sorted_by_syllables_left = sorted(possible, key=lambda x: len(syllables))
    return sorted_by_syllables_left

def run_for_file(file, range, options_asy, result='list', debug=False):
    xml_data = m21.converter.parse(file)
    syllables = xml_to_lyrics(xml_data)
    print(len(syllables), syllables)
    print(assemble_lyrics(syllables, len(syllables), options_asy))

    #escribir_en_fichero("Sylables: " + str(len(syllables)))

    if debug:
        
        syllables_To_debug = ''
        for i in syllables:
            syllables_To_debug += "[" + i[0] +"] "
        escribir_en_fichero(syllables_To_debug)
        syllables_To_debug = ''
        for i in syllables:
            syllables_To_debug += "[" + i[0] + ',' + i[1] + "] "
        escribir_en_fichero(syllables_To_debug)

    if len(syllables) == 0:
        print('-- No syllables')
        return

    possible = test_meters(syllables, range, discard_non_divisble=False, debug=debug)
    possible_asy = test_asymetric_meters(syllables, options_asy, discard_non_divisble=False, debug=debug)
   
    if len(possible_asy) > 0:
        escribir_correcto('Selected possible  asy: ' )
        for a in possible_asy:
            escribir_correcto(a)

    if len(possible) == 0:
        syllables = xml_to_lyrics(xml_data, ties='all')
        possible = test_meters(syllables, range, discard_non_divisble=True, debug=debug)

    if debug:
        possible_txt = ''
        for i in possible:
            possible_txt += str(i) + ','
        for i in possible_asy:
            possible_txt += str(i) + ','
        escribir_en_fichero('POSSIBLE ASY'+ possible_txt)

    pos_max_rima = rymeFilter(syllables, possible, possible_asy, options_asy, result, debug)

    
    escribir_correcto('Selected possible '+ str(pos_max_rima))
    return assemble_lyrics(syllables, breaks=pos_max_rima,options_asy = options_asy, result=result) if len(possible) > 0 else []
        
import re


def rymeFilter (syllables, possible, possible_asy, options_asy, result, debug=False):
    ##Filtro por numero de rimas para intentar seleccionar la mejor opción dentro de las posibles. 
    max_rima = -1
    pos_max_rima = 0
    for a in possible:
        num_a_rima = detectar_cualquier_rima(assemble_lyrics(syllables, breaks=a,options_asy= options_asy, result=result))
        if debug :escribir_en_fichero(str(a) + ' ' + str(num_a_rima))
        if num_a_rima > max_rima:
            max_rima = num_a_rima
            pos_max_rima = a
    
    for a in possible_asy:
        num_a_rima = detectar_cualquier_rima(assemble_lyrics(syllables, breaks=a,options_asy = options_asy, result=result))
        if debug :escribir_en_fichero(str(a) + ' ' + str(num_a_rima))
        if num_a_rima > max_rima:
            max_rima = num_a_rima
            pos_max_rima = a

    possiblefiltered= '['
    for i in possible:
       possiblefiltered+= str(i) + ','
    
    if debug: escribir_en_fichero('POSSIBLE filtered '+ possiblefiltered + ']')

    if debug: escribir_en_fichero('Selected possible '+ str(pos_max_rima))
    
    return pos_max_rima

def obtener_silabas(palabra):
    """
    Retorna las últimas dos sílabas de una palabra, utilizando un patrón básico de vocales.
    """
    vocales = 'aeiouáéíóúü'
    palabra = palabra.lower()
    silabas = re.findall(r'[{}]+[^{}]*'.format(vocales, vocales), palabra)
    return silabas[-2:] if len(silabas) >= 2 else silabas

def tipo_rima(verso1, verso2):
    """
    Determina el tipo de rima entre dos versos (asonante o consonante).
    """
    if (len(verso1)==0 or len(verso2) == 0):
        return
    print (verso1, ' ---- ', verso2)
    ultima_palabra1 = verso1.strip().split()[-1]
    ultima_palabra2 = verso2.strip().split()[-1]
    
    silabas1 = obtener_silabas(ultima_palabra1)
    silabas2 = obtener_silabas(ultima_palabra2)
    
    if not silabas1 or not silabas2:
        return "Sin rima"

    # Verifica rima consonante (todas las letras coinciden)
    if silabas1 == silabas2:
        return "Rima consonante"

    # Verifica rima asonante (coinciden solo las vocales)
    vocales1 = ''.join([letra for letra in ''.join(silabas1) if letra in 'aeiouáéíóúü'])
    vocales2 = ''.join([letra for letra in ''.join(silabas2) if letra in 'aeiouáéíóúü'])
   
    vocales1 = quitar_acentos(vocales1)
    vocales2 = quitar_acentos(vocales2)
    
    #if DEBUG:
    #    escribir_en_fichero(verso1 + '-----' + verso2)
    #    escribir_en_fichero ("Rima asonante: "+ vocales1[-1] + ' - ' + vocales2[-1])

    if vocales1[-1] == vocales2[-1]:
        print ("Rima ")
        return "Rima asonante"

    return "Sin rima"

def detectar_cualquier_rima(versos):
    """
    Detecta si al menos dos versos de una lista tienen algún tipo de rima (asonante o consonante).
    Devuelve True si existe al menos una rima y False en caso contrario.
    """


    numero_rimas = 0
    for i in range(len(versos)):
        numero_rimas_loc = 0
        for j in range(len(versos)):
            if i!=j:
                if tipo_rima(versos[i], versos[j]) != "Sin rima":
                    numero_rimas_loc+=1
        if numero_rimas_loc != 0:
            numero_rimas+=1
    
    return numero_rimas


if __name__ == "__main__":
    #run_for_file(FILE, debug=True)

    for filename in os.listdir(DIR):

        if not filename.endswith('.xml'):
            continue

        print('##########', filename)
        f = os.path.join(DIR, filename)
        lyrics = run_for_file(f)
        print(lyrics)



