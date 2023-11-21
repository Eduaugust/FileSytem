import datetime

FILE = 'sistema.txt'
ESPACO256MB = 1024 * 1024 * 256 # 256Mb
ESPACO4KB = 4096 # 4kb

QTD_INODE = int(805306368/8965) + 3
TAM_INODE = 256

QTD_POSICOES = int(268435456/1793) + 3

TAM_BLOCO = ESPACO4KB
QTD_BLOCOS = int(536870912/8965)

class iNode:
    # Nome do arquivo/diretório
    # Criador
    # Dono
    # Tamanho
    # Data de criação
    # Data de modificação
    # Permissões de acesso (dono e outros usuários - leitura, escrita, execução)
    # Apontadores para blocos
    # Apontador para eventual outro i-node
    def __init__(self, posicao: str, nomeArquivoDiretorio: str, criador: str, dono: str, tamanho: str, usuarioCriador: str, dataCriacao: str = str(datetime.datetime.now()), dataModificacao: str = str(datetime.datetime.now()), permissoes: str = "drwxr--", apontadoresParaBlocos: str = '', apontadoresOutrosInodes: str = '') -> None:
        self.posicao = posicao, # posicao relativa
        self.nomeArquivoDiretorio = nomeArquivoDiretorio, # 64 caracteres
        self.criador = criador, # 6 caracteres -> index geral
        self.usuarioCriador = usuarioCriador, # 32 caracteres
        self.dono = dono, # 32 caracteres
        self.tamanho = tamanho, # tamanho do arquivo em bytes
        self.dataCriacao = dataCriacao, # 26 caracteres -> data de criação do arquivo
        self.dataModificacao = dataModificacao, # 26 caracteres -> data de modificação do arquivo
        self.permissoes = permissoes, # 7 caracteres permissões de acesso => drwxrwx or frwxr-- to others just leitura
        self.apontadoresParaBlocos = apontadoresParaBlocos, # custo = 5*5 caracteres -> 5 blocos no máximo
        self.apontadoresOutrosInodes = apontadoresOutrosInodes # 5*6 inodes no máximo ->6 caracteres por inode para posicao
        # sobrou 8 caracteres para bater 256

    def __repr__(self) -> str:
        return str(self.nomeArquivoDiretorio) + str(self.criador) + str(self.dono) + str(self.tamanho) + str(self.dataCriacao) + str(self.dataModificacao) + str(self.permissoes) + str(self.apontadoresParaBlocos) + str(self.apontadoresOutrosInodes)
    def __str__(self) -> str:
        text = ''
        text += str(self.nomeArquivoDiretorio[0].ljust(64, '*'))
        text += str(self.criador[0].ljust(6, '*'))
        text += str(self.dono[0].ljust(32, '*'))
        text += str(self.dataCriacao[0].ljust(26, '*'))
        text += str(self.dataModificacao[0].ljust(26, '*'))
        text += str(self.permissoes[0].ljust(7, '*'))
        text += str(self.apontadoresParaBlocos[0].ljust(25, '*')) if self.apontadoresParaBlocos else ''.ljust(25, '*')
        text += str(self.apontadoresOutrosInodes.ljust(30, '*')) if self.apontadoresOutrosInodes else ''.ljust(30, '*')
        text += str(self.usuarioCriador[0].ljust(32, '*'))
        return text
    # set name
    def setName(self, newName: str) -> None:
        self.nomeArquivoDiretorio = tuple([newName])
    
    def setCriador(self, newCriador: str) -> None:
        self.criador =  tuple([newCriador])
    
    def setBloco(self, newBloco: str) -> None:
        self.apontadoresParaBlocos = tuple([newBloco])
    
    def setDataModificacao(self) -> None:
        self.dataModificacao = tuple([str(datetime.datetime.now())])