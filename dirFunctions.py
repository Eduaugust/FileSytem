# - [x] Criar diretório (mkdir diretorio)
# - [x] Remover diretório (rmdir diretorio) - só funciona se diretório estiver vazio
# - [x] Listar o conteúdo de um diretório (ls diretório)
# - [x] Trocar de diretório (cd diretorio)
# - [x] Não esquecer dos arquivos especiais . e .. 
# - [x] Renomear/mover diretório (mv diretorio1 diretorio2)
# - [x] Criar links entre diretório (ln -s arquivoOriginal link)

import time
from typing import List
from utils import *
from iNode import *

FILE = 'sistema.txt'
ESPACO256MB = 1024 * 1024 * 256 # 256Mb
ESPACO4KB = 4096 # 4kb

QTD_INODE = int(805306368/8965) + 4
TAM_INODE = 256

QTD_POSICOES = int(268435456/1793) + 3

TAM_BLOCO = ESPACO4KB
QTD_BLOCOS = int(536870912/8965)

class DirFunctions:
    def __init__(self, arquivo: TextIOWrapper) -> None:
        self.arquivo = arquivo
        self.utils = Utils(arquivo)

    def mkdir(self, txt: List[str], indexAtualGeral: str) -> None:
        if len(txt) != 2:
            print("Erro: mkdir <nomeDiretorio>")
            return
        nome = txt[1]
        if nome == '.' or nome == '..' or self.utils.hasAnyAsterisco(nome):
            print("Erro: nome de diretório inválido")
            return
        
        # Verifica se o nome já esta em uso
        nome = nome.split('/')
        nomeNovoInode = nome.pop(-1)
        if len(nome) == 0:
            novoLugarGeral = indexAtualGeral
        else:
            novoLugarGeral = self.cd(['cd', ''.join(nome)], indexAtualGeral)
        # check if is not a str instance
        if not isinstance(novoLugarGeral, str):
            return
        
        if self.utils.procuraInodeFilho(nomeNovoInode, indexAtualGeral=novoLugarGeral) != '':
            print("Erro: nome de diretório já em uso")
            return
        
        # Procura espaço vazio no sistema para o iNode do diretório
        indexInodeCriadoGeral = self.utils.procuraVaga(True)

        # Cria Inode
        inode = iNode(self.utils.indexGeral2IndexInode(indexInodeCriadoGeral), nomeNovoInode, novoLugarGeral, "usuario", '')

        indexCriadoRelativo = self.utils.indexGeral2IndexInode(indexInodeCriadoGeral)

        # adiciona novo diretorio como filho no pai
        self.utils.adicionaFilhoNoPaiInode(novoLugarGeral, indexCriadoRelativo)

        # Insere inode raiz no index encontrado
        self.utils.inserirInodeEmPosicaoValida(int(indexCriadoRelativo), str(inode))

    def rmdir(self, txt: List[str], indexAtualGeral: str) -> bool:
        if len(txt) != 2:
            print("Erro: rmdir <nomeDiretorio>")
            return False
        nome = txt[1]

        # Verifica se o nome já esta em uso
        IndexGeralToRemove = self.cd(['cd', nome], indexAtualGeral)
        if not isinstance(IndexGeralToRemove, str):
            return False
        
        # Verifica se o diretório está vazio
        filhos = self.utils.retornaInodeTotalExtensao(IndexGeralToRemove)
        if len(filhos) > 0:
            print("Erro: diretório não está vazio")
            return False

        # Remove associação no pai
        self.utils.removeFilhoNoPaiInode(IndexGeralToRemove)

        # Remove inode do diretório
        self.utils.removerInode(IndexGeralToRemove)
        
        return True

    def ls(self, indexAtualGeral: str) -> None:
        # Procura inode do diretório
        listaInodes = self.utils.retornaInodeTotalExtensao(indexAtualGeral)
        for inode in listaInodes:
            print(inode.nomeArquivoDiretorio[0].replace('*', ''))

    def cd(self, txt: List[str], indexAtualGeral: str, wantJustDir: bool = True) -> str | bool:
        if len(txt) != 2:
            print("Erro: cd <nomeDiretorio>")
            return False
        nome = txt[1]
        if nome[0] != '/':
            # se for caminho relativo
            nome = nome.split('/')
            tmpIndexAtualGeral = indexAtualGeral
            for index, nomeInode in enumerate(nome):
                # Procura inode do diretório
                if nomeInode == '':
                    continue
                inodeEncontradoGeral = self.utils.procuraInodeFilho(nomeInode, indexAtualGeral=tmpIndexAtualGeral)
                if inodeEncontradoGeral == '':
                    if index == 0:
                        print("Erro: diretório não encontrado")
                    return False
                tmpIndexAtualGeral = inodeEncontradoGeral
            tmpInode = self.utils.retornaInodeEstrutura(tmpIndexAtualGeral)
            if tmpInode.permissoes[0][0] != 'd' and wantJustDir:
                print("Erro: não é um diretório")
                return False
            if tmpInode.permissoes[0][0] == 'd' and not wantJustDir:
                return False
            return tmpIndexAtualGeral
        else:
            # cd absoluto
            raiz = self.utils.indexInode2IndexGeral('0')
            nome = nome.split('/')
            tmpIndexAtualGeral = raiz
            for nomeInode in nome:
                # Procura inode do diretório
                if nomeInode == '':
                    continue
                inodeEncontradoGeral = self.utils.procuraInodeFilho(nomeInode, indexAtualGeral=tmpIndexAtualGeral)
                if inodeEncontradoGeral == '':
                    print("Erro: diretório não encontrado 2")
                    return False
                tmpIndexAtualGeral = inodeEncontradoGeral
            tmpInode = self.utils.retornaInodeEstrutura(tmpIndexAtualGeral)
            if tmpInode.permissoes[0][0] != 'd' and wantJustDir:
                print("Erro: não é um diretório")
                return False
            if tmpInode.permissoes[0][0] == 'd' and not wantJustDir:
                return False
            return tmpIndexAtualGeral

    def pwd(self, indexAtualGeral: str) -> str:
        inode = self.utils.retornaInodeEstrutura(indexAtualGeral)
        nome = inode.nomeArquivoDiretorio[0].replace('*', '')
        if nome == 'root':
            return '/'
        # fazer recursivo e no fim retornar todos os nomes do caminho separados por /
        caminhoCriador = inode.criador[0].replace('*', '')
        return self.pwd(caminhoCriador) + nome + '/' 

    def ln(self, txt: List[str], indexAtualGeral: str) -> None:
        # Criar links entre diretório (ln -s arquivoOriginal link)
        if txt[1] != '-s':
            print("Erro: ln -s <arquivoOriginal> <link>")
        # Funções para organizar
        localizacaoInicial = txt[2]
        localizacaoFinal = txt[3]

        indexGeralInicio = self.cd(['cd', localizacaoInicial], indexAtualGeral, False)
        if not isinstance(indexGeralInicio, str):
            indexGeralInicio = self.cd(['cd', localizacaoInicial], indexAtualGeral)
            if not isinstance(indexGeralInicio, str):
                return

        # Verifica se a ultima localizacao existe
        indexGeralFim = self.cd(['cd', localizacaoFinal], indexAtualGeral)
        if not isinstance(indexGeralFim, str):
            return
        
        # Verifica se há uma pasta com o mesmo nome
        nome = localizacaoInicial.split('/').pop(-1)
        existeUltimaLocalizacao = self.utils.procuraInodeFilho(nome, indexAtualGeral=indexGeralFim)
        if existeUltimaLocalizacao != '':
            print("Erro: nome de já em uso")
            return
        
        # Faz o link
        self.utils.adicionaFilhoNoPaiInode(indexGeralFim, self.utils.indexGeral2IndexInode(indexGeralInicio))

        print("Link criado com sucesso")
        return