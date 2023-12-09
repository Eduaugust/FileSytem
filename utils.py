from io import TextIOWrapper
import time
from typing import List
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

class Utils:
    def __init__(self, arquivo: TextIOWrapper) -> None:
        self.arquivo = arquivo

    def hasAnyAsterisco(self, txt: str) -> bool:
        if txt.find('*') != -1:
            return True
        return False

    def escreverArquivo(self, texto: str) -> None:
        arquivo = self.arquivo
        arquivo.seek(0)
        arquivo.write(texto)

    def checaSePosicaoEstaAlocada(self, indexGeral: str) -> bool:
        arquivo = self.arquivo
        arquivo.seek(int(indexGeral))
        txt = arquivo.read(1)
        if txt[0] == '0':
            return False
        return True

    def desalocaPosicao(self, indexGeral: str) -> None:
        self.escreverArquivoPerIndex('0', int(indexGeral))

    def alocaPosicao(self, indexGeral: str) -> None:
        self.escreverArquivoPerIndex('1', int(indexGeral))
    
    def retornaTamanhoArquivo(self, indexAtualGeral: str) -> int:
        conteudo = self.lerArquivoPerIndex(int(indexAtualGeral))
        return len(conteudo)
    
    def retornaTamanhoPasta(self, indexAtualGeral: str) -> int:
        inodesFilhos = self.retornaInodeTotalExtensao(indexAtualGeral)
        tamanho = 0

        for inode in inodesFilhos:
            # Se o inode for um arquivo, ler conteudo e retornar tamanho
            if inode.permissoes[0][0] == 'f':
                tamanho += self.retornaTamanhoArquivo(self.indexInode2IndexGeral(inode.posicao[0]))
            else:
                tamanho += self.retornaTamanhoPasta(self.indexInode2IndexGeral(inode.posicao[0]))
        return tamanho

    def retornaInodeTotalExtensao(self, indexAtualGeral: str) -> List[iNode]:
        startTimer = time.time()
        inodePai = self.retornaInodeEstrutura(indexAtualGeral)
        listApontadores = list(inodePai.apontadoresOutrosInodes)
        listaInodesFilhos = []
        count = 0
        for i in range(0, len(listApontadores), 6):
            count += 1
            filho = ''
            for j in range(i, i + 6):
                filho += listApontadores[j]
            if self.hasAnyAsterisco(filho):
                continue
            filhoGeral = self.indexInode2IndexGeral(filho)
            if self.checaSePosicaoEstaAlocada(filhoGeral) == False:
                continue
            inodeFilho = self.retornaInodeEstrutura(filhoGeral)
            if count == 5:
                listaExtensao = self.retornaInodeTotalExtensao(filhoGeral)
                listaInodesFilhos += listaExtensao
            else:
                listaInodesFilhos.append(inodeFilho)
        return listaInodesFilhos

    def lerArquivoPerIndex(self, indexGeral: int) -> str:
        inode = self.retornaInodeEstrutura(str(indexGeral))
        listApontadores = list(inode.apontadoresParaBlocos[0])
        txt = ''
        # for para ler todos os blocos e concatenar
        for i in range(0, len(listApontadores), 5):
            bloco = ''
            for j in range(i, i + 5):
                bloco += listApontadores[j]
            if self.hasAnyAsterisco(bloco):
                continue
            blocoGeral = self.indexBloco2IndexGeral(bloco)
            if self.checaSePosicaoEstaAlocada(bloco) == False:
                continue
            txt += self.lerBlocoPerIndex(int(blocoGeral))
        # for para ler o inode de extensao e chamar novamente a função de forma recursiva
        listApontadores = list(inode.apontadoresOutrosInodes)
        for i in range(0, len(listApontadores), 6):
            inode = ''
            for j in range(i, i + 6):
                inode += listApontadores[j]
            if self.hasAnyAsterisco(inode):
                continue
            if self.checaSePosicaoEstaAlocada(self.indexInode2IndexGeral(inode)) == False:
                continue

            indexGeral = int(self.indexInode2IndexGeral(inode))
            i = self.retornaInodeEstrutura(str(indexGeral))

            txt += self.lerArquivoPerIndex(indexGeral)

        return txt

    def lerBlocoPerIndex(self, indexGeral: int) -> str:
        arquivo = self.arquivo
        arquivo.seek(indexGeral)
        txt = arquivo.read(ESPACO4KB)
        return txt.replace('*', '')

    def retornaInodeEstrutura(self, indexInodeGeral: str) -> iNode:
        arquivo = self.arquivo
        startTime = time.time()
        arquivo.seek(int(indexInodeGeral))
        txt = arquivo.read(256)
        # print('txt', txt[0: 219], txt[154])
        nomeArquivoDiretorio = txt[0:64]
        criador = txt[64:70]
        dono = txt[70:102]
        tamanho = ''
        dataCriacao = txt[102:128]
        dataModificacao = txt[128:154]
        permissoes = txt[154:161]
        apontadoresParaBlocos = txt[161:186]
        apontadoresOutrosInodes = txt[186:216]
        usuarioCriador = txt[216:248]
        inode = iNode(
            self.indexGeral2IndexInode(indexInodeGeral),
            nomeArquivoDiretorio, 
            criador, 
            dono, 
            tamanho, 
            usuarioCriador,
            dataCriacao, 
            dataModificacao, 
            permissoes, 
            apontadoresParaBlocos, 
            apontadoresOutrosInodes,
        )
        return inode

    def localizacaoInodePai(self, indexAtualGeral: str) -> str: # indexInodeGeral do pai
        inode = self.retornaInodeEstrutura(indexAtualGeral)
        return inode.criador[0]

    def procuraInodeFilho(self, nome: str, indexAtualGeral: str) -> str: # retorna posicao Geral 
        # TODO: verificar se o nome é um arquivo ou um diretório, segundo um parâmetro
        # Alterar toda função para utilizar a funçõ retornaTotalInodeExtensao
        inodesFilhos = self.retornaInodeTotalExtensao(indexAtualGeral)
        inodePai = self.retornaInodeEstrutura(indexAtualGeral)
        if nome == '.':
            return indexAtualGeral
        if nome == '..':
            if indexAtualGeral == self.indexInode2IndexGeral('0'):
                return indexAtualGeral
            return inodePai.criador[0].replace('*', '')
        for filho in inodesFilhos:
            if filho.nomeArquivoDiretorio[0].replace('*', '') == nome:
                return self.indexInode2IndexGeral(filho.posicao[0]) 
        return ''

    def adicionaFilhoNoPaiInode(self, indexAtualGeral: str, indexInodeFilhoPosicao: str) -> None:
        inodePai = self.retornaInodeEstrutura(indexAtualGeral)
        check = self.verificaApontadorInodeEstaCheio(indexAtualGeral)
        if check == True:
            inodePai = self.adicionaExtensaoNoPaiInode(indexAtualGeral, inodePai, 4*6)
            self.adicionaFilhoNoPaiInode(self.indexInode2IndexGeral(inodePai.posicao[0]), indexInodeFilhoPosicao)
        else:
            tmpApontadores = list(inodePai.apontadoresOutrosInodes)
            indexInodeFilhoPosicao = indexInodeFilhoPosicao.rjust(6, '0')
            for i in range(6):
                tmpApontadores[check + i] = indexInodeFilhoPosicao[i]
            inodePai.apontadoresOutrosInodes = "".join(tmpApontadores)
            self.escreverArquivoPerIndex(str(inodePai), int(indexAtualGeral))
            self.alocaPosicao(indexInodeFilhoPosicao)

    def adicionaExtensaoNoPaiInode(self, indexAtualGeral: str, inodePai: iNode, posicaoExtensaoNosApontadores: int) -> iNode:
        check = posicaoExtensaoNosApontadores

        # Lista de apontadores do pai
        tmpApontadores = list(inodePai.apontadoresOutrosInodes)

        # Verifica se já existe uma extensão
        extensao = inodePai.apontadoresOutrosInodes[check: check + 6]
        if self.hasAnyAsterisco(extensao) == False and self.checaSePosicaoEstaAlocada(extensao) == True:
            return self.retornaInodeEstrutura(self.indexInode2IndexGeral(extensao))
        # Procura vaga
        indexInodeCriadoGeral = self.procuraVaga(True)
        indexInodeCriadoRelativo = self.indexGeral2IndexInode(indexInodeCriadoGeral)

        # Cria um inode vazio
        inode = iNode(indexInodeCriadoRelativo, '', '', '', '', '', '', '', '', '')
        self.inserirInodeEmPosicaoValida(int(indexInodeCriadoRelativo), str(inode))
        
        # Adiciona apontador no filho
        indexInodeFilhoPosicao = indexInodeCriadoRelativo.rjust(6, '0')
        for i in range(6):
            tmpApontadores[check + i] = indexInodeFilhoPosicao[i]
        inodePai.apontadoresOutrosInodes = "".join(tmpApontadores)
        self.escreverArquivoPerIndex(str(inodePai), int(indexAtualGeral))
        novoInodePai = self.retornaInodeEstrutura(indexInodeCriadoGeral)
        return novoInodePai

    def removeFilhoNoPaiInode(self, indexInodeFilhoGeral: str) -> None:
        inodeFilho = self.retornaInodeEstrutura(indexInodeFilhoGeral)
        indexAtualGeral: str = inodeFilho.criador[0].replace('*', '')
        inodePai = self.retornaInodeEstrutura(indexAtualGeral)
        tmpApontadores = list(inodePai.apontadoresOutrosInodes)
        for i in range(0, len(tmpApontadores), 6):
            filho = ''
            for j in range(i, i + 6):
                filho += tmpApontadores[j]
            if self.hasAnyAsterisco(filho):
                continue
            if self.checaSePosicaoEstaAlocada(self.indexInode2IndexGeral(filho)) == False:
                continue
            if self.indexInode2IndexGeral(filho) == indexInodeFilhoGeral:
                for j in range(i, i + 6):
                    tmpApontadores[j] = '*'
                break
        inodePai.apontadoresOutrosInodes = "".join(tmpApontadores)
        self.escreverArquivoPerIndex(str(inodePai), int(indexAtualGeral))

    def verificaApontadorInodeEstaCheio(self, indexAtualGeral: str) -> int | bool:
        inode = self.retornaInodeEstrutura(indexAtualGeral)
        listApontadores = list(inode.apontadoresOutrosInodes)
        for i in range(0, len(listApontadores) - 6, 6):
            inodeFilho = ''
            for j in range(i, i + 6):
                inodeFilho += listApontadores[j]
            if self.hasAnyAsterisco(inodeFilho):
                return i 
            if self.checaSePosicaoEstaAlocada(self.indexInode2IndexGeral(inodeFilho)) == False:
                return i
        return True

    def adicionaBlocoNoInode(self, indexAtualGeral: str, indexBlocoGeral: str) -> None:
        inodePai = self.retornaInodeEstrutura(indexAtualGeral)
        check = self.verificaApontadorBlocoEstaCheio(inodePai)
        if isinstance(check, bool):
            # Se true, quer dizer que apontadores para blocos no inode estão cheios
            checkInodeCheio = self.verificaApontadorInodeEstaCheio(indexAtualGeral) # Retorna o index do apontador para inode que esta vazio ou True
            if isinstance(checkInodeCheio, bool):
                # Se entrar aqui quer dizer que apontadores para outros inodes esta cheio e devemos chamar recursivamente passando um apontador do inode pai
                self.adicionaBlocoNoInode(self.indexInode2IndexGeral(inodePai.apontadoresOutrosInodes[0:6]), indexBlocoGeral)
            else:
                # Se entrar aqui quer dizer que apontadores para outros inodes não esta cheio e devemos adicionar um novo inode para extender os blocos
                novoInode = self.adicionaExtensaoNoPaiInode(indexAtualGeral, inodePai, 0)
                self.adicionaBlocoNoInode(self.indexInode2IndexGeral(novoInode.posicao[0]), indexBlocoGeral)
        else:
            # Significa que dentro do check há qual lugar devemos colocar o index do bloco
            tmpApontadores = list(inodePai.apontadoresParaBlocos[0])
            indexBlocoRelativo = self.indexGeral2IndexBloco(indexBlocoGeral)
            indexBlocoRelativo = indexBlocoRelativo.rjust(5, '0')
            for i in range(len(indexBlocoRelativo)):
                tmpApontadores[check + i] = indexBlocoRelativo[i]
            inodePai.setBloco("".join(tmpApontadores))
            self.alocaPosicao(indexBlocoRelativo)
            self.escreverArquivoPerIndex(str(inodePai), int(indexAtualGeral))

    def verificaApontadorBlocoEstaCheio(self, inode: iNode) -> int | bool:
        listApontadoresBlocos = list(inode.apontadoresParaBlocos[0])
        for i in range(0, len(listApontadoresBlocos), 5):
            bloco = ''
            for j in range(i, i + 5):
                bloco += listApontadoresBlocos[j]
            if self.hasAnyAsterisco(bloco):
                return i
            if self.checaSePosicaoEstaAlocada(self.indexBloco2IndexGeral(bloco)) == False:
                return i
        return True

    def indexGeral2IndexInode(self, indexGeral: str) -> str:
        indexGeralInt = int(indexGeral)
        return str((indexGeralInt - QTD_POSICOES) // TAM_INODE)

    def indexInode2IndexGeral(self, indexInode: str or int) -> str:
        indexInodeInt = int(indexInode)
        return str(indexInodeInt * TAM_INODE + QTD_POSICOES)

    def indexGeral2IndexBloco(self, indexGeral: str) -> str:
        indexGeralInt = int(indexGeral)
        return str((indexGeralInt - QTD_INODE - QTD_INODE * TAM_INODE) // TAM_BLOCO)

    def indexBloco2IndexGeral(self, indexBloco: str) -> str:
        indexBlocoInt = int(indexBloco)
        return str(indexBlocoInt * TAM_BLOCO + QTD_INODE + QTD_INODE * TAM_INODE)

    def procuraVaga(self, isInode: bool) -> str:
        arquivo = self.arquivo
        if isInode:
            arquivo.seek(0)
            texto = arquivo.read(QTD_INODE)
            for i in range(QTD_INODE):
                if texto[i] == '0':
                    self.escreverArquivoPerIndex('1', i)
                    return self.indexInode2IndexGeral(str(i))
            return '' 
        else:
            arquivo.seek(QTD_INODE)
            texto = arquivo.read(QTD_POSICOES - QTD_INODE)
            for i in range(QTD_POSICOES - QTD_INODE):
                if texto[i] == '0':
                    indexGeralBloco = i + QTD_INODE
                    self.escreverArquivoPerIndex('1', indexGeralBloco)
                    return self.indexBloco2IndexGeral(str(indexGeralBloco))
            return ''

    def removerInode(self, indexGeral: str) -> None:
        # TODO: remover todos os arquivos e inodes associados a ele
        indexEspecificoPosicao = int(self.indexGeral2IndexInode(indexGeral))
        self.escreverArquivoPerIndex('0', indexEspecificoPosicao)
        self.escreverArquivoPerIndex(''.ljust(256, '*'), int(indexGeral))

    def inserirInodeEmPosicaoValida(self, indexRelativo: int, inode: str) -> bool:
        if indexRelativo < 0 or indexRelativo > QTD_INODE:
            return False
        indexGeral = int(self.indexInode2IndexGeral(str(indexRelativo)))
        self.alocaPosicao(str(indexRelativo))
        self.escreverArquivoPerIndex(inode, indexGeral)
        return True

    def inserirBlocoEmPosicaoValida(self, index: int, bloco: str) -> bool:
        if index < 0 or index > QTD_BLOCOS:
            return False

        texto = bloco.ljust(ESPACO4KB, '*')
        self.escreverArquivoPerIndex(texto, int(self.indexBloco2IndexGeral(str(index))))
        return True
    
    def verificaPermissao(self, usuario: str, permissao: str, dono: str, permissoes: str) -> bool:
        usuario = usuario.replace('*', '')
        dono = dono.replace('*', '')
        if usuario == 'init' or permissao == '-':
            return True
        # Verifica permissão
        dicionarioPermissoes = {'r': 1, 'w': 2, 'x': 3}
        for p in permissao:
            if p == 'd' and usuario == dono:
                return True
            permissaoInt = dicionarioPermissoes[p]
            if usuario != dono and permissoes[permissaoInt + 3] == '-':
                return False
            if usuario == dono and permissoes[permissaoInt] == '-':
                return False
        return True


    def limparSistema(self) -> None:
        texto = list("*" * ESPACO256MB) # 256Mb sendo o tamanho do arquivo

        # Libera tudo
        texto[0: QTD_POSICOES] = "0" * QTD_POSICOES
        self.escreverArquivo("".join(texto))

        # Procura espaço para colocar a raiz
        indexGeral = self.procuraVaga(True)
        
        # Cria inode raiz
        inode = iNode(self.indexGeral2IndexInode(indexGeral), "root", self.indexInode2IndexGeral('1'), "init", '0', usuarioCriador="init")

        text = str(inode)

        # Insere inode raiz no index encontrado
        self.inserirInodeEmPosicaoValida(int(self.indexGeral2IndexInode(indexGeral)), text)
    
    def atualizaDataModificacao(self, indexArquivoGeral: str) -> None:
        inode = self.retornaInodeEstrutura(indexArquivoGeral)
        inode.setDataModificacao()
        self.escreverArquivoPerIndex(str(inode), int(indexArquivoGeral))

    def escreverArquivoPerIndex(self, texto: str, indexGeral: int) -> None:
        arquivo = self.arquivo
        arquivo.seek(indexGeral)
        arquivo.write(texto)
