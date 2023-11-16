import os
from utils import *
from dirFunctions import *
from fileFunctions import *

QTD_INODE = int(805306368/8965) + 3
TAM_INODE = 256

QTD_POSICOES = int(268435456/1793) + 3

TAM_BLOCO = ESPACO4KB
QTD_BLOCOS = int(536870912/8965)

FILE = 'sistema.txt'
ESPACO256MB = 1024 * 1024 * 256 # 256Mb
ESPACO4KB = 4096 # 4kb


if __name__ == "__main__":
    checkSeSistemaExiste()
    raiz = indexInode2IndexGeral('0')
    indexAtualGeral = raiz
    command = ''
    dir = pwd(indexAtualGeral)
    while True:
        txt = input(dir + ' > ')
        # if txt has any "*" symbol, print error
        txt = txt.split()
        command = txt[0]
        if command == 'exit':
            break
        elif command == 'clearALL':
            limparSistema()
        elif command == 'mkdir':
            mkdir(txt, indexAtualGeral)
        elif command == 'rmdir':
            rmdir(txt, indexAtualGeral)
        elif command == 'ls':
            ls(indexAtualGeral)
        elif command == 'cd':
            check = cd(txt, indexAtualGeral)
            if not isinstance(check, str):
                continue
            indexAtualGeral = check
            dir = pwd(indexAtualGeral)
        elif command == 'mv':
            mv(txt, indexAtualGeral)
        elif command == 'ln':
            ln(txt, indexAtualGeral)
        elif command == 'touch':
            touch(txt, indexAtualGeral)
        elif command == 'echo':
            echo(txt, indexAtualGeral)
        elif command == 'rm':
            resposta = rm(txt, indexAtualGeral)
            if resposta != '':
                print(resposta)
        elif command == 'cat':
            resposta = cat(txt, indexAtualGeral)
            if resposta != '':
                print(resposta)
        elif command == 'cp':
            cp(txt, indexAtualGeral)
        elif command == 'clear':
            os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')
         