# - [x] Criar arquivo (touch arquivo)
# - [x] Remover arquivo (rm arquivo)
# - [x] Criar um arquivo já adicionando conteúdo (echo "conteúdo legal" > arquivo)
# - [x] Adicionar conteúdo a um arquivo existente ou criá-lo caso não exista (echo "conteudo legal" >> arquivo)
# - [x] Ler arquivo (cat arquivo)
# - [x] Copiar arquivo (cp arquivo1 arquivo2)
# - [x] Renomear/mover arquivo (mv arquivo1 arquivo2)
# - [x] Criar links entre arquivos (ln -s arquivoOriginal link)

from typing import List
from dirFunctions import DirFunctions
from iNode import *
from utils import *

FILE = 'sistema.txt'
ESPACO256MB = 1024 * 1024 * 256 # 256Mb
ESPACO4KB = 4096 # 4kb

QTD_INODE = int(805306368/8965) + 3
TAM_INODE = 256

QTD_POSICOES = int(268435456/1793) + 3

TAM_BLOCO = ESPACO4KB
QTD_BLOCOS = int(536870912/8965)

class FileFunctions:
    def __init__(self, arquivo: TextIOWrapper) -> None:
        self.arquivo = arquivo
        self.df = DirFunctions(arquivo=self.arquivo)
        self.utils = Utils(arquivo=self.arquivo)

    def touch(self, txt: List[str], indexAtualGeral: str) -> str:
        # Checa se o comando foi digitado corretamente
        if len(txt) != 2:
            print("Erro: touch <nomeArquivo>")
            return ''
        nome = txt[1]
        if nome == '.' or nome == '..' or self.utils.hasAnyAsterisco(nome):
            print("Erro: nome de arquivo inválido")
            return ''
        
        pasta = nome.split('/')
        nomeArquivo = pasta.pop(-1)
        if nomeArquivo == '':
            nomeArquivo = pasta.pop(-1)
        pasta = ''.join(pasta)
        if len(pasta) == 0:
            pasta = './'
        
        # Verifica se o caminho existe
        indexPasta = self.df.cd(['cd', pasta], indexAtualGeral)
        if not isinstance(indexPasta, str):
            return ''
        
        
        # Verifica se o nome já esta em uso
        filhoAchado = self.utils.procuraInodeFilho(nomeArquivo, indexAtualGeral=indexPasta)
        if filhoAchado != '':
            inodeFilhoEcontrado = self.utils.retornaInodeEstrutura(filhoAchado)
            if inodeFilhoEcontrado.permissoes[0] == 'f':
                print("Erro: nome de arquivo já em uso")
                return ''
            
        # Procura espaço vazio no sistema para o iNode do arquivo
        indexInodeCriadoGeral = self.utils.procuraVaga(True)

        # Cria Inode
        indexCriadoRelativo = self.utils.indexGeral2IndexInode(indexInodeCriadoGeral)
        inode = iNode(indexCriadoRelativo, nomeArquivo, indexPasta, "usuario", '', permissoes="frwxr--")


        # adiciona novo arquivo como filho no pai
        self.utils.adicionaFilhoNoPaiInode(indexPasta, indexCriadoRelativo)    

        # Insere inode raiz no index encontrado
        self.utils.inserirInodeEmPosicaoValida(int(indexCriadoRelativo), str(inode))

        return indexInodeCriadoGeral
        
    def rm(self, txt: List[str], indexAtualGeral: str) -> str:
        if len(txt) != 2:
            return "Erro: rm <nomeArquivo>"
        nome = txt[1]
        if nome == '.' or nome == '..' or self.utils.hasAnyAsterisco(nome):
            return "Erro: nome de arquivo inválido"
        
        pasta = nome.split('/')
        nomeArquivo = pasta.pop(-1)
        if nomeArquivo == '':
            nomeArquivo = pasta.pop(-1)
        pasta = ''.join(pasta)
        if len(pasta) == 0:
            pasta = './'

        # Verifica se o caminho existe
        indexPasta = self.df.cd(['cd', pasta], indexAtualGeral)
        if not isinstance(indexPasta, str):
            return "Erro: caminho não encontrado"
        
        filhoAchado = self.utils.procuraInodeFilho(nomeArquivo, indexAtualGeral=indexPasta)
        if filhoAchado == '':
            return 'Erro: arquivo não encontrado'
        
        inodeFilhoEcontrado = self.utils.retornaInodeEstrutura(filhoAchado)
        if inodeFilhoEcontrado.permissoes[0][0] == 'd':
            return 'Erro: arquivo é um diretório'
        # Remove o arquivo do pai
        self.utils.removeFilhoNoPaiInode(filhoAchado)
        
        # Remove o arquivo do sistema
        self.utils.removerInode(filhoAchado)

        return ''

    def echo(self, txt: List[str], indexAtualGeral: str) -> None:
        # Checa se o comando foi digitado corretamente
        conteudo = txt[1:-2]
        conteudo = ' '.join(conteudo)
        if (txt[-2] != '>' and txt[-2] != '>>') or conteudo[0] != '"' or conteudo[-1] != '"':
            print('Erro: echo "<conteudo>" > <nomeArquivo>')
            return
        nome = txt[-1]
        if nome == '.' or nome == '..' or self.utils.hasAnyAsterisco(nome):
            print("Erro: nome de arquivo inválido")
            return
        
        # Remove as aspas do conteudo apenas do inicio e do fim
        conteudo = conteudo[1:-1]
        
        # Verifica se o caminho existe
        pasta = nome.split('/')
        nomeArquivo = pasta.pop(-1)
        if nomeArquivo == '':
            nomeArquivo = pasta.pop(-1)
        pasta = ''.join(pasta)
        if len(pasta) == 0:
            pasta = './'
        
        
        antesFor = time.time()
        
        # Verifica se o arquivo ja existe
        indexPasta = self.df.cd(['cd', pasta], indexAtualGeral)
        if not isinstance(indexPasta, str):
            return
        # achou uma pasta com o mesmo nome
        indexArquivoGeral = self.df.cd(['cd', nome], indexAtualGeral, False)
        if txt[-2] == '>' or not isinstance(indexArquivoGeral, str):
            # Sobrescreve o artigo
            self.rm(['rm', nome], indexAtualGeral)
            # Crindo arquivo 
            indexArquivoGeral = self.touch(['touch', nome], indexAtualGeral)
            if indexArquivoGeral == '':
                return
        else:
            # Adiciona conteudo ao fim arquivo
            
            # Ler o conteudo do arquivo 
            indexArquivoGeral = self.df.cd(['cd', nome], indexAtualGeral, False)
            if not isinstance(indexArquivoGeral, str):
                return
            textoAdc = self.utils.lerArquivoPerIndex(int(indexArquivoGeral))
            textoAdc = textoAdc.replace('\x00', '')
            conteudo = str(textoAdc + conteudo)
        
        # print(time.time() - antesFor, 'antesFor')
        
        # Separa o conteudo em um vetor onde cada posição tem 4kb
        conteudoSeparado: List[str] = []
        for i in range(0, len(conteudo), ESPACO4KB):
            conteudoSeparado.append(conteudo[i:i+ESPACO4KB])
        
        # Enquanto ainda tiver conteudo para escrever, cria um bloco e aponta pro pai
        fo = time.time()
        for i in range(len(conteudoSeparado)):
            # Achando bloco vazio
            indexBlocoVazio = self.utils.procuraVaga(isInode=False)

            # Escrevendo conteudo no bloco
            self.utils.escreverArquivoPerIndex(conteudoSeparado[i], int(indexBlocoVazio))

            # Adicionando bloco no inode
            self.utils.adicionaBlocoNoInode(indexArquivoGeral, indexBlocoVazio)
        # print(time.time() - fo, 'for')

    def cat(self, txt: List[str], indexAtualGeral: str) -> str:
        if len(txt) != 2:
            print("Erro: cat <nomeArquivo>")
            return ''
        nome = txt[1]
        if nome == '.' or nome == '..' or self.utils.hasAnyAsterisco(nome):
            print("Erro: nome de arquivo inválido")
            return ''
        
        # Verifica se o caminho existe
        pasta = nome.split('/')
        nomeArquivo = pasta.pop(-1)
        if nomeArquivo == '':
            nomeArquivo = pasta.pop(-1)
        pasta = ''.join(pasta)
        if len(pasta) == 0:
            pasta = './'
        
        # Verifica se o arquivo ja existe
        indexPasta = self.df.cd(['cd', pasta], indexAtualGeral)
        if isinstance(indexPasta, str):
        
            # achou uma pasta com o mesmo nome
            indexArquivo = self.df.cd(['cd', nome], indexAtualGeral, False)
            if not isinstance(indexArquivo, str):
                print("Erro: arquivo não encontrado")
                return ''

            # Lendo o arquivo
            conteudo = self.utils.lerArquivoPerIndex(int(indexArquivo))
            return conteudo
        return ''

    def cp(self, txt: List[str], indexAtualGeral: str) -> None:
        if len(txt) != 3:
            print("Erro: cp <nomeArquivo> <nomeArquivo2>")
            return
        nome = txt[1]
        if nome == '.' or nome == '..' or self.utils.hasAnyAsterisco(nome):
            print("Erro: nome de arquivo inválido")
            return
        
        # Verifica se o caminho existe
        pasta = nome.split('/')
        nomeArquivo = pasta.pop(-1)
        if nomeArquivo == '':
            nomeArquivo = pasta.pop(-1)
        pasta = ''.join(pasta)
        if len(pasta) == 0:
            pasta = './'
        
        # Verifica se o arquivo ja existe
        indexPasta = self.df.cd(['cd', pasta], indexAtualGeral)
        if not isinstance(indexPasta, str):
            return
        # achou uma pasta com o mesmo nome
        indexArquivo = self.df.cd(['cd', nomeArquivo], indexPasta, False)
        if not isinstance(indexArquivo, str):
            return
        
        # Conteudo do arquivo original
        conteudo = self.utils.lerArquivoPerIndex(int(indexArquivo))
        conteudo.replace('\x00', '')

        # Cria novo arquivo com o conteudo do original
        self.echo(['echo', '"' + conteudo + '"', '>', txt[2]], indexPasta)

    def mv(self, txt: List[str], indexAtualGeral: str) -> None:
        # Funções para organizar
        localizacaoInicial = txt[1]
        localizacaoFinal = txt[2].split('/')
        ultimaPasta = localizacaoFinal.pop(-1)
        if ultimaPasta == '':
            ultimaPasta = localizacaoFinal.pop(-1)
            if localizacaoFinal == '':
                localizacaoFinal = '/.'
        localizacaoFinal = ''.join(localizacaoFinal)
        if localizacaoFinal == '':
            localizacaoFinal = './'

        indexGeralNovoInode = self.df.cd(['cd', localizacaoFinal], indexAtualGeral)
        if not isinstance(indexGeralNovoInode, str):
            return

        indexGeralInodeAntigoFile = self.df.cd(['cd', localizacaoInicial], indexAtualGeral, False)
        if isinstance(indexGeralInodeAntigoFile, str):
            self.mvFiles(self.utils.retornaInodeEstrutura(indexGeralInodeAntigoFile), indexGeralNovoInode, ultimaPasta)
            return
        indexGeralInodeAntigo = self.df.cd(['cd', localizacaoInicial], indexAtualGeral)
        if not isinstance(indexGeralInodeAntigo, str):
        
            return
        
        # Verifica se a ultima localizacao existe
        existeUltimaLocalizacao = self.utils.procuraInodeFilho(ultimaPasta, indexAtualGeral=indexGeralNovoInode)
        inode = self.utils.retornaInodeEstrutura(indexGeralInodeAntigo)

        # Se ultima localizacao for um diretorio existente, mover o arquivo para dentro dele
        if existeUltimaLocalizacao != '':
            indexGeralNovoInode = self.df.cd(['cd', ultimaPasta], indexGeralNovoInode)
            if not isinstance(indexGeralNovoInode, str):
                return
        else:
            inode.setName(ultimaPasta)
        # Remover o inode do pai antigo
        self.utils.removeFilhoNoPaiInode(indexGeralInodeAntigo)

        # Adicionar o inode no novo pai
        self.utils.adicionaFilhoNoPaiInode(indexGeralNovoInode, self.utils.indexGeral2IndexInode(indexGeralInodeAntigo))

        # Seta o criador como pai no filho
        inode.setCriador(indexGeralNovoInode)
        self.utils.escreverArquivoPerIndex(str(inode), int(indexGeralInodeAntigo))
        return

    def mvFiles(self, inodeOrigem: iNode, indexDestino: str, novoNomeArquivo: str) -> None:
        indexOrigemArquivo = self.utils.indexInode2IndexGeral(inodeOrigem.posicao[0]  )  
        nomeInode = inodeOrigem.nomeArquivoDiretorio[0].replace('*', '')
        criadorInode = inodeOrigem.criador[0].replace('*', '')
        # Conteúdo do arquivo original
        conteudo = self.utils.lerArquivoPerIndex(int(indexOrigemArquivo))
        conteudo.replace('\x00', '')

        # Cria novo arquivo com o conteúdo do original
        self.echo(['echo', '"' + conteudo + '"', '>', novoNomeArquivo], indexDestino)



        # Remove o arquivo original
        self.rm(['rm',nomeInode], criadorInode)
