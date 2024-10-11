
FILE_EXPORT = "Errores"

def escribir_en_fichero(texto):
    with open(FILE_EXPORT + ".txt", 'a', encoding='utf-8') as f:
        f.write(texto + '\n') 


def reset_fichero():
    with open(FILE_EXPORT + ".txt", 'w', encoding='utf-8') as f:
        f.write("" + '\n')  