from dirFunctions import DirFunctions
from fileFunctions import FileFunctions
from utils import Utils
import hashlib

class Seguranca:
    """
    Classe responsável por lidar com a segurança do sistema.
    """

    def __init__(self, arquivo, utils: Utils, df: DirFunctions, ff: FileFunctions, homeLocation: str):
        """
        Inicializa uma nova instância da classe Seguranca.

        Args:
            arquivo: O arquivo a ser manipulado.
            utils: Uma instância da classe Utils.
            df: Uma instância da classe DirFunctions.
            ff: Uma instância da classe FileFunctions.
            homeLocation: O local inicial do sistema.
        """
        self.arquivo = arquivo
        self.utils = utils
        self.df = df
        self.ff = ff
        self.homeLocation = homeLocation

    def createOrLogin(self) -> str:
        """
        Cria um novo usuário ou realiza o login de um usuário existente.

        Returns:
            O nome de usuário do usuário logado.
        """
        print("Welcome to system.")
        while True:
            print("1 - Create User")
            print("2 - Login")
            createLogin = input()
            if createLogin == '1':
                self.createUser()
            if createLogin == '2':
                while True:
                    result = self.login()
                    if result != False and result != True: 
                        return result

    def createUser(self) -> None:
        """
        Cria um novo usuário.
        """
        print("Create User")
        print("Username: ")
        username = input()
        listUser = self.df.ls(self.homeLocation, True)
        if ' ' in username or username in listUser or username == '' or username == 'init' or self.utils.hasAnyAsterisco(username):
            print("Invalid username.")
            return
        print("Password: ")
        password = input()
        print("Confirm Password: ")
        confirmPassword = input()
        if password != confirmPassword:
            print("Password and Confirm Password are not equal.")
            return
        self.createUserInode(username, password)
    
    def login(self) -> bool | str:
        """
        Realiza o login de um usuário existente.

        Returns:
            O nome de usuário do usuário logado ou False se o login falhar.
        """
        print("Login")
        listUser = self.df.ls(self.homeLocation, True)
        print("List of users: ", listUser)
        print("Username: ")
        username = input()
        print("Password: ")
        password = input()
        if username not in listUser:
            print("User not found.")
            return False
        response = self.verify_password(username, password)
        if response == False: 
            return False
        print("Login successful.")
        return response
    
    def createUserInode(self, username: str, password: str) -> None:
        """
        Cria um novo inode para o usuário.

        Args:
            username: O nome de usuário do novo usuário.
            password: A senha do novo usuário.
        """
        # Create folder with username
        txt = 'mkdir ' + username
        self.df.mkdir(txt.split(), self.homeLocation, username)

        # Hashing password
        hash = self.hash_password(password)
        
        # Create file with password
        txt = f'echo "{hash}" > {username}/password'
        self.ff.echo(txt.split(), self.homeLocation)

        # Altera o dono do arquivo
        # txt = f'chown {username} {username}/password'

        # Altera as permissões do arquivo
        txt = f'chmod 60 {username}/password'
        self.df.chmod(txt.split(), self.homeLocation)
    
    def hash_password(self,password: str) -> str:
        """
        Gera o hash da senha fornecida.

        Args:
            password: A senha a ser hasheada.

        Returns:
            O hash da senha.
        """
        # Cria um novo objeto sha256
        sha_signature = hashlib.sha256(password.encode()).hexdigest()
        return sha_signature
    
    def check_password(self, hashed_password: str, user_password: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash fornecido.

        Args:
            hashed_password: O hash da senha armazenado.
            user_password: A senha fornecida pelo usuário.

        Returns:
            True se a senha corresponder ao hash, False caso contrário.
        """
        user_password_hash = hashlib.sha256(user_password.encode()).hexdigest()
        return user_password_hash == hashed_password
    
    def verify_password(self, username: str, password: str) -> bool | str:
        """
        Verifica se a senha fornecida corresponde à senha armazenada para o usuário.

        Args:
            username: O nome de usuário do usuário.
            password: A senha fornecida pelo usuário.

        Returns:
            O nome de usuário do usuário logado se a senha corresponder, False caso contrário.
        """
        # Get the hashed password from the file
        txt = f'cat /home/{username}/password'
        hashed_password = self.ff.cat(txt.split(), self.homeLocation)

        # Check if the provided password matches the hashed password
        if self.check_password(hashed_password, password):
            return username
        else:
            print("Password is incorrect")
            return False
