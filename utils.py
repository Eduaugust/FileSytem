from operator import index
import time
from typing import List

from numpy import False_

from iNode import *

FILE = 'sistema.txt'
ESPACO256MB = 1024 * 1024 * 256 # 256Mb
ESPACO4KB = 4096 # 4kb


QTD_INODE = int(805306368/8965) + 3
TAM_INODE = 256

QTD_POSICOES = int(268435456/1793) + 3

TAM_BLOCO = ESPACO4KB
QTD_BLOCOS = int(536870912/8965)

# print(QTD_BLOCOS + QTD_INODE, QTD_POSICOES)

# Medindo qual a diferença de espaço tem somando tudo e com 256Mb
# print(ESPACO256MB - (QTD_INODE * TAM_INODE + QTD_POSICOES + QTD_BLOCOS * TAM_BLOCO))

def hasAnyAsterisco(txt: str) -> bool:
    if txt.find('*') != -1:
        return True
    return False

def escreverArquivo(texto: str) -> None:
    arquivo = open(FILE, "w")
    arquivo.write(texto)
    arquivo.close()

def lerArquivo() -> str:
    arquivo = open(FILE, "r")
    txt = arquivo.read()
    arquivo.close()
    return txt

def checaSePosicaoEstaAlocada(indexGeral: str) -> bool:
    arquivo = open(FILE, "r")
    arquivo.seek(int(indexGeral))
    txt = arquivo.read()
    arquivo.close()
    if txt[0] == '0':
        return False
    return True

def desalocaPosicao(indexGeral: str) -> None:
    escreverArquivoPerIndex('0', int(indexGeral))

def alocaPosicao(indexGeral: str) -> None:
    escreverArquivoPerIndex('1', int(indexGeral))

def retornaInodeTotalExtensao(indexAtualGeral: str) -> List[iNode]:
    startTimer = time.time()
    inodePai = retornaInodeEstrutura(indexAtualGeral)
    listApontadores = list(inodePai.apontadoresOutrosInodes)
    listaInodesFilhos = []
    count = 0
    for i in range(0, len(listApontadores), 6):
        count += 1
        filho = ''
        for j in range(i, i + 6):
            filho += listApontadores[j]
        if hasAnyAsterisco(filho):
            continue
        filhoGeral = indexInode2IndexGeral(filho)
        if checaSePosicaoEstaAlocada(filhoGeral) == False:
            continue
        inodeFilho = retornaInodeEstrutura(filhoGeral)
        if count == 5:
            listaExtensao = retornaInodeTotalExtensao(filhoGeral)
            listaInodesFilhos += listaExtensao
        else:
            listaInodesFilhos.append(inodeFilho)
    endTimer = time.time()
    # print('Tempo de execução: ', endTimer - startTimer)
    return listaInodesFilhos

def lerArquivoPerIndex(indexGeral: int) -> str:
    inode = retornaInodeEstrutura(str(indexGeral))
    listApontadores = list(inode.apontadoresParaBlocos[0])
    txt = ''
    # for para ler todos os blocos e concatenar
    for i in range(0, len(listApontadores), 5):
        bloco = ''
        for j in range(i, i + 5):
            bloco += listApontadores[j]
        if hasAnyAsterisco(bloco):
            continue
        blocoGeral = indexBloco2IndexGeral(bloco)
        if checaSePosicaoEstaAlocada(bloco) == False:
            continue
        txt += lerBlocoPerIndex(int(blocoGeral))
    # for para ler o inode de extensao e chamar novamente a função de forma recursiva
    listApontadores = list(inode.apontadoresOutrosInodes)
    for i in range(0, len(listApontadores), 6):
        inode = ''
        for j in range(i, i + 6):
            inode += listApontadores[j]
        if hasAnyAsterisco(inode):
            continue
        if checaSePosicaoEstaAlocada(indexInode2IndexGeral(inode)) == False:
            continue

        indexGeral = int(indexInode2IndexGeral(inode))
        i = retornaInodeEstrutura(str(indexGeral))

        txt += lerArquivoPerIndex(indexGeral)

    return txt

def lerBlocoPerIndex(indexGeral: int) -> str:
    arquivo = open(FILE, "r")
    arquivo.seek(indexGeral)
    txt = arquivo.read()
    arquivo.close()
    return txt[0: ESPACO4KB].replace('*', '')

def retornaInodeEstrutura(indexInodeGeral: str) -> iNode:
    arquivo = open(FILE, "r")
    arquivo.seek(int(indexInodeGeral))
    txt = arquivo.read()
    # print('txt', txt[0: 219], txt[154])
    arquivo.close()
    nomeArquivoDiretorio = txt[0:64]
    criador = txt[64:70]
    dono = txt[70:102]
    tamanho = ''
    dataCriacao = txt[102:128]
    dataModificacao = txt[128:154]
    permissoes = txt[154:161]
    apontadoresParaBlocos = txt[161:186]
    apontadoresOutrosInodes = txt[186:216]
    inode = iNode(
        indexGeral2IndexInode(indexInodeGeral),
        nomeArquivoDiretorio, 
        criador, 
        dono, 
        tamanho, 
        dataCriacao, 
        dataModificacao, 
        permissoes, 
        apontadoresParaBlocos, 
        apontadoresOutrosInodes,
    )
    return inode

def localizacaoInodePai(indexAtualGeral: str) -> str: # indexInodeGeral do pai
    inode = retornaInodeEstrutura(indexAtualGeral)
    return inode.criador[0]

def procuraInodeFilho(nome: str, indexAtualGeral: str) -> str: # retorna posicao Geral 
    # TODO: verificar se o nome é um arquivo ou um diretório, segundo um parâmetro
    # Alterar toda função para utilizar a funçõ retornaTotalInodeExtensao
    inodesFilhos = retornaInodeTotalExtensao(indexAtualGeral)
    inodePai = retornaInodeEstrutura(indexAtualGeral)
    if nome == '.':
        return indexAtualGeral
    if nome == '..':
        if indexAtualGeral == indexInode2IndexGeral('0'):
            return indexAtualGeral
        return inodePai.criador[0].replace('*', '')
    for filho in inodesFilhos:
        if filho.nomeArquivoDiretorio[0].replace('*', '') == nome:
            return indexInode2IndexGeral(filho.posicao[0]) 
    return ''

def adicionaFilhoNoPaiInode(indexAtualGeral: str, indexInodeFilhoPosicao: str) -> None:
    inodePai = retornaInodeEstrutura(indexAtualGeral)
    check = verificaApontadorInodeEstaCheio(indexAtualGeral)
    if check == True:
        inodePai = adicionaExtensaoNoPaiInode(indexAtualGeral, inodePai, 4*6)
        adicionaFilhoNoPaiInode(indexInode2IndexGeral(inodePai.posicao[0]), indexInodeFilhoPosicao)
    else:
        tmpApontadores = list(inodePai.apontadoresOutrosInodes)
        indexInodeFilhoPosicao = indexInodeFilhoPosicao.rjust(6, '0')
        for i in range(6):
            tmpApontadores[check + i] = indexInodeFilhoPosicao[i]
        inodePai.apontadoresOutrosInodes = "".join(tmpApontadores)
        escreverArquivoPerIndex(str(inodePai), int(indexAtualGeral))
        alocaPosicao(indexInodeFilhoPosicao)

def adicionaExtensaoNoPaiInode(indexAtualGeral: str, inodePai: iNode, posicaoExtensaoNosApontadores: int) -> iNode:
    check = posicaoExtensaoNosApontadores

    # Lista de apontadores do pai
    tmpApontadores = list(inodePai.apontadoresOutrosInodes)

    # Verifica se já existe uma extensão
    extensao = inodePai.apontadoresOutrosInodes[check: check + 6]
    if hasAnyAsterisco(extensao) == False and checaSePosicaoEstaAlocada(extensao) == True:
        return retornaInodeEstrutura(indexInode2IndexGeral(extensao))
    # Procura vaga
    indexInodeCriadoGeral = procuraVaga(True)
    indexInodeCriadoRelativo = indexGeral2IndexInode(indexInodeCriadoGeral)

    # Cria um inode vazio
    inode = iNode(indexInodeCriadoRelativo, '', '', '', '', '', '', '', '', '')
    inserirInodeEmPosicaoValida(int(indexInodeCriadoRelativo), str(inode))
    
    # Adiciona apontador no filho
    indexInodeFilhoPosicao = indexInodeCriadoRelativo.rjust(6, '0')
    for i in range(6):
        tmpApontadores[check + i] = indexInodeFilhoPosicao[i]
    inodePai.apontadoresOutrosInodes = "".join(tmpApontadores)
    escreverArquivoPerIndex(str(inodePai), int(indexAtualGeral))
    novoInodePai = retornaInodeEstrutura(indexInodeCriadoGeral)
    return novoInodePai

def removeFilhoNoPaiInode(indexInodeFilhoGeral: str) -> None:
    inodeFilho = retornaInodeEstrutura(indexInodeFilhoGeral)
    indexAtualGeral: str = inodeFilho.criador[0].replace('*', '')
    inodePai = retornaInodeEstrutura(indexAtualGeral)
    tmpApontadores = list(inodePai.apontadoresOutrosInodes)
    for i in range(0, len(tmpApontadores), 6):
        filho = ''
        for j in range(i, i + 6):
            filho += tmpApontadores[j]
        if hasAnyAsterisco(filho):
            continue
        if checaSePosicaoEstaAlocada(indexInode2IndexGeral(filho)) == False:
            continue
        if indexInode2IndexGeral(filho) == indexInodeFilhoGeral:
            for j in range(i, i + 6):
                tmpApontadores[j] = '*'
            break
    inodePai.apontadoresOutrosInodes = "".join(tmpApontadores)
    escreverArquivoPerIndex(str(inodePai), int(indexAtualGeral))

def verificaApontadorInodeEstaCheio(indexAtualGeral: str) -> int | bool:
    inode = retornaInodeEstrutura(indexAtualGeral)
    listApontadores = list(inode.apontadoresOutrosInodes)
    for i in range(0, len(listApontadores) - 6, 6):
        inodeFilho = ''
        for j in range(i, i + 6):
            inodeFilho += listApontadores[j]
        if hasAnyAsterisco(inodeFilho):
            return i 
        if checaSePosicaoEstaAlocada(indexInode2IndexGeral(inodeFilho)) == False:
            return i
    return True

def adicionaBlocoNoInode(indexAtualGeral: str, indexBlocoGeral: str) -> None:
    inodePai = retornaInodeEstrutura(indexAtualGeral)
    check = verificaApontadorBlocoEstaCheio(inodePai)
    if isinstance(check, bool):
        # Se true, quer dizer que apontadores para blocos no inode estão cheios
        checkInodeCheio = verificaApontadorInodeEstaCheio(indexAtualGeral) # Retorna o index do apontador para inode que esta vazio ou True
        if isinstance(checkInodeCheio, bool):
            # Se entrar aqui quer dizer que apontadores para outros inodes esta cheio e devemos chamar recursivamente passando um apontador do inode pai
            adicionaBlocoNoInode(indexInode2IndexGeral(inodePai.apontadoresOutrosInodes[0:6]), indexBlocoGeral)
        else:
            # Se entrar aqui quer dizer que apontadores para outros inodes não esta cheio e devemos adicionar um novo inode para extender os blocos
            novoInode = adicionaExtensaoNoPaiInode(indexAtualGeral, inodePai, 0)
            adicionaBlocoNoInode(indexInode2IndexGeral(novoInode.posicao[0]), indexBlocoGeral)
    else:
        # Significa que dentro do check há qual lugar devemos colocar o index do bloco
        tmpApontadores = list(inodePai.apontadoresParaBlocos[0])
        indexBlocoRelativo = indexGeral2IndexBloco(indexBlocoGeral)
        indexBlocoRelativo = indexBlocoRelativo.rjust(5, '0')
        for i in range(len(indexBlocoRelativo)):
            tmpApontadores[check + i] = indexBlocoRelativo[i]
        inodePai.setBloco("".join(tmpApontadores))
        alocaPosicao(indexBlocoRelativo)
        escreverArquivoPerIndex(str(inodePai), int(indexAtualGeral))

def verificaApontadorBlocoEstaCheio(inode: iNode) -> int | bool:
    listApontadoresBlocos = list(inode.apontadoresParaBlocos[0])
    for i in range(0, len(listApontadoresBlocos), 5):
        bloco = ''
        for j in range(i, i + 5):
            bloco += listApontadoresBlocos[j]
        if hasAnyAsterisco(bloco):
            return i
        if checaSePosicaoEstaAlocada(indexBloco2IndexGeral(bloco)) == False:
            return i
    return True

def indexGeral2IndexInode(indexGeral: str) -> str:
    indexGeralInt = int(indexGeral)
    return str((indexGeralInt - QTD_POSICOES) // TAM_INODE)

def indexInode2IndexGeral(indexInode: str or int) -> str:
    indexInodeInt = int(indexInode)
    return str(indexInodeInt * TAM_INODE + QTD_POSICOES)

def indexGeral2IndexBloco(indexGeral: str) -> str:
    indexGeralInt = int(indexGeral)
    return str((indexGeralInt - QTD_INODE - QTD_INODE * TAM_INODE) // TAM_BLOCO)

def indexBloco2IndexGeral(indexBloco: str) -> str:
    indexBlocoInt = int(indexBloco)
    return str(indexBlocoInt * TAM_BLOCO + QTD_INODE + QTD_INODE * TAM_INODE)

def procuraVaga(isInode: bool) -> str:
    arquivo = open(FILE, "r")
    texto = arquivo.read()
    if isInode:
        for i in range(QTD_INODE):
            if texto[i] == '0':
                escreverArquivoPerIndex('1', i)
                arquivo.close()
                return indexInode2IndexGeral(str(i))
        arquivo.close()
        return '' 
    else:
        for i in range(QTD_INODE, QTD_POSICOES):
            if texto[i] == '0':
                escreverArquivoPerIndex('1', i)
                arquivo.close()
                return indexBloco2IndexGeral(str(i))
        arquivo.close()
        return ''

def removerInode(indexGeral: str) -> None:
    # TODO: remover todos os arquivos e inodes associados a ele
    indexEspecificoPosicao = int(indexGeral2IndexInode(indexGeral))
    escreverArquivoPerIndex('0', indexEspecificoPosicao)
    escreverArquivoPerIndex(''.ljust(256, '*'), int(indexGeral))

def inserirInodeEmPosicaoValida(indexRelativo: int, inode: str) -> bool:
    if indexRelativo < 0 or indexRelativo > QTD_INODE:
        return False
    indexGeral = int(indexInode2IndexGeral(str(indexRelativo)))
    alocaPosicao(str(indexRelativo))
    escreverArquivoPerIndex(inode, indexGeral)
    return True

def inserirBlocoEmPosicaoValida(index: int, bloco: str) -> bool:
    if index < 0 or index > QTD_BLOCOS:
        return False

    texto = bloco.ljust(ESPACO4KB, '*')
    escreverArquivoPerIndex(texto, int(indexBloco2IndexGeral(str(index))))
    return True

def checkSeSistemaExiste() -> None:
    try:
        arquivo = open(FILE, "r")
        arquivo.close()
    except:
        # Cria arquivo sistema.txt
        arquivo = open(FILE, "w")
        arquivo.close()
        limparSistema()

def limparSistema() -> None:
    texto = list("*" * ESPACO256MB) # 256Mb sendo o tamanho do arquivo

    # Libera tudo
    texto[0: QTD_POSICOES] = "0" * QTD_POSICOES
    escreverArquivo("".join(texto))


    # Procura espaço para colocar a raiz
    indexGeral = procuraVaga(True)
    # Cria inode raiz
    
    inode = iNode(indexGeral2IndexInode(indexGeral), "root", indexInode2IndexGeral('1'), "root", '0')

    text = str(inode)

    # Insere inode raiz no index encontrado
    inserirInodeEmPosicaoValida(int(indexGeral2IndexInode(indexGeral)), text)

def escreverArquivoPerIndex(texto: str, indexGeral: int) -> None:
    arquivo = open(FILE, "r+")
    arquivo.seek(indexGeral)
    arquivo.write(texto)
    arquivo.close()