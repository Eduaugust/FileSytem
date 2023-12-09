# [X] - Ao criar o sistema, criar uma HOME
# [X] - Criar um novo usuario (com senha e estar armazenado em um arquivo sem ser 
# texto plano - hash - usuários normais não podem ver o arquivo de usuários)
# [X] - Login no novo usuário
# [X] - Cada arquivo tem um dono e permissões de leitura e escrita
# [] - Chmod (para trocar as permissões dos arquivos/diretórios) 
# [] - Chown (para trocar o dono de um arquivo/diretório) 


import os
from seguranca import Seguranca
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

def checkSeSistemaExiste() -> bool:
    try:
       # Verifica se o arquivo sistema.txt existe
        arquivo = open(FILE, "r")
        arquivo.close()
        return True
    except:
        # Cria arquivo sistema.txt
        arquivo = open(FILE, "w")
        arquivo.close()
        return False
    
if __name__ == "__main__":
    r = checkSeSistemaExiste()
    arquivo = open(FILE, 'r+')
    utils = Utils(arquivo)
    raiz = utils.indexInode2IndexGeral('0')
    df = DirFunctions(arquivo, 'init')
    ff = FileFunctions(arquivo, 'init')
    if not r:
        utils.limparSistema()
        # Cria home
        df.mkdir('mkdir home'.split(), raiz, 'init')
    
    raiz = df.cd('cd home'.split(), raiz, 'x')
    if not isinstance(raiz, str):
        print("Erro: diretório não encontrado")
        exit()
    
    seg = Seguranca(arquivo, utils, df, ff, raiz)
    # Create User or Login
    usuario = seg.createOrLogin()

    
    txt = 'cd ' + usuario
    indexAtualGeral = df.cd(txt.split(), raiz, 'x')
    if not isinstance(indexAtualGeral, str):
        print("Erro: diretório não encontrado")
        exit()
    command = ''
    while True:
        utils = Utils(arquivo)
        df = DirFunctions(arquivo, usuario)
        ff = FileFunctions(arquivo, usuario)
        dir = df.pwd(indexAtualGeral)
        txt = input(dir + ' > ')
        txt = txt.split()
        command = txt[0]
        if command == 'exit':
            break
        elif command == 'clearALL':
            utils.limparSistema()
        elif command == 'mkdir':
            df.mkdir(txt, indexAtualGeral, usuario)
        elif command == 'rmdir':
            df.rmdir(txt, indexAtualGeral)
        elif command == 'ls':
            df.ls(indexAtualGeral)
        elif command == 'cd':
            check = df.cd(txt, indexAtualGeral, 'x')
            if not isinstance(check, str):
                print("Erro: diretório não encontrado")
                continue
            indexAtualGeral = check
        elif command == 'du':
            df.du(txt, indexAtualGeral)
        elif command == 'mv':
            ff.mv(txt, indexAtualGeral)
        elif command == 'ln':
            df.ln(txt, indexAtualGeral)
        elif command == 'touch':
            ff.touch(txt, indexAtualGeral)
        elif command == 'echo':
            ff.echo(txt, indexAtualGeral)
        elif command == 'rm':
            resposta = ff.rm(txt, indexAtualGeral)
            if resposta != '':
                print(resposta)
        elif command == 'cat':
            resposta = ff.cat(txt, indexAtualGeral)
            if resposta != '':
                print(resposta)
        elif command == 'cp':
            ff.cp(txt, indexAtualGeral)
        elif command == 'chmod':
            df.chmod(txt, indexAtualGeral)
        elif command == 'chown':
            df.chown(txt, indexAtualGeral)
        elif command == 'clear':
            os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')
    arquivo.close()
         
