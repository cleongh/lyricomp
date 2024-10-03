import music21 as m21
import os

DIR = '/Users/hugo/invs/projetos/2023_EA_DIGIFOLK/xml_ptnera'
#FILE = '/Users/hugo/invs/projetos/2023_EA_DIGIFOLK/xml_ptnera/MX-1951-00-VM-00001.musicxml.xml'
#FILE = '/Users/hugo/invs/projetos/2023_EA_DIGIFOLK/xml_ptnera/MX-1951-00-VM-00016.musicxml.xml'
#FILE = '/Users/hugo/invs/projetos/2023_EA_DIGIFOLK/xml_ptnera/MX-1951-00-VM-00093.musicxml.xml'
#FILE = '/Users/hugo/invs/projetos/2023_EA_DIGIFOLK/xml_ptnera/MX-1951-00-VM-00182.musicxml.xml'
#FILE = '/Users/hugo/invs/projetos/2023_EA_DIGIFOLK/xml_ptnera/MX-1956-00-VM-01371.musicxml.xml'
FILE = '/Users/hugo/invs/projetos/2023_EA_DIGIFOLK/xml_ptnera/MX-1951-00-VM-00048.musicxml.xml'
# 7 + 7 + 7 + 5?
#FILE = '/Users/hugo/invs/projetos/2023_EA_DIGIFOLK/xml_ptnera/MX-1951-00-VM-00072.musicxml.xml'

# Note: in Spanish, all single-syllable words are stressed, but in some lyrics they may not count as such...

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


def assemble_lyrics(syllables, breaks=None, result='str'):
    lyrics = []

    line = ''
    for i, syl in enumerate(syllables):
        if syl[0]:
            if syl[1] != 'extend':
                line += syl[0]
            if syl[1] == 'single' or syl[1] == 'end':
                line += ' '
            if breaks and (i+1) % breaks == 0:
                lyrics.append(line.strip())
                line = ''

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
        if debug: print('TEST =', m)
        while x < len(syllables):
            first = syllables[x - m + 1]
            last = syllables[x]

            if debug:
                print('FIRST', x - m + 1, first, '| LAST', x, last)

            # must start with: begin or single
            if first[1] != 'begin' and first[1] != 'single':
                ok = False
                if debug: print('--IMPOSSIBLE START!')
                break

            if last[1] == 'middle' or last[1] == 'begin':
                ok = False
                if debug: print('--IMPOSSIBLE END!')
                break

            # words that should not end lines
            if (last[1] == 'single' and last[0] in SINGLE_CANNOT_END) or ('\xa0' in last[0] and last[0].replace('\xa0', '') in SINGLE_CANNOT_END):
                ok = False
                if debug: print('--IMPOSSIBLE END!')
                break

            x += m
        if ok:
            if debug: print('OK', m)
            #print(len(syllables) % m)
            possible.append(m)

    #sorted_by_syllables_left = sorted(possible, key=lambda x: len(syllables) % x)
    sorted_by_syllables_left = sorted(possible, key=lambda x: len(syllables))
    return sorted_by_syllables_left


def run_for_file(file, range, result='list', debug=False):
    xml_data = m21.converter.parse(file)
    syllables = xml_to_lyrics(xml_data)
    print(len(syllables), syllables)
    print(assemble_lyrics(syllables))

    if len(syllables) == 0:
        print('-- No syllables')
        return

    possible = test_meters(syllables, range, discard_non_divisble=True, debug=debug)
    if len(possible) == 0:
        syllables = xml_to_lyrics(xml_data, ties='all')
        possible = test_meters(syllables, range, discard_non_divisble=True, debug=debug)

    print('POSSIBLE', possible)

    #for p in possible:
    #    print('POSSIBLE', p)
    #    print(lyrics_to_str(syllables, p))

    return assemble_lyrics(syllables, breaks=possible[0], result=result) if len(possible) > 0 else []


'''
if __name__ == "__main__":
    #run_for_file(FILE, debug=True)

    for filename in os.listdir(DIR):

        if not filename.endswith('.xml'):
            continue

        print('##########', filename)
        f = os.path.join(DIR, filename)
        lyrics = run_for_file(f)
        print(lyrics)
'''