from pyverse import Pyverse

def extract_verse(syllables, poem):
    return poem[:syllables], poem[syllables:]
    
def versification_bt(poem):
    if poem == []:
        yield []
    else:
        for syllables in [8, 11, 16]:
            if len(poem) >= syllables:
                current_verse, rest = extract_verse(syllables, poem)
                for candidate_versification in versification_bt(rest):
                    yield [current_verse] + candidate_versification

def versification(poem):
    return versification_bt(list(filter(lambda x: x != '', Pyverse(poem).syllables.split('-'))))

def beautify_poem(poem_list):
    poem = ''
    for verse in poem_list:
        poem += ' '.join(verse)
        poem += '\n'
    return poem

i = 0
for candidate_versification in versification('con cien cañones por banda viento en popa a toda vela no corta el mar sino vuela'):
    print('versification ', i)
    i += 1
    print(beautify_poem(candidate_versification))
    print('-' * 15)
    
