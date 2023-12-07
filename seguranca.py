from dirFunctions import DirFunctions
from fileFunctions import FileFunctions
from utils import Utils


class Seguranca:
    def __init__(self, arquivo, utils: Utils, df: DirFunctions, ff: FileFunctions, listUser: list):
        self.arquivo = arquivo
        self.listUser = listUser
        print('listUser', listUser)

    def createOrLogin(self) -> None:
        print("Welcome to system.")
        while True:
            print("1 - Create User")
            print("2 - Login")
            createLogin = input()
            if createLogin == '1':
                self.createUser()
            if createLogin == '2':
                self.utils.login()
                break

    def createUser(self) -> None:
        print("Create User")
        print("Username: ")
        username = input()
        print("Password: ")
        password = input()
        print("Confirm Password: ")
        confirmPassword = input()
        if password != confirmPassword:
            print("Password and Confirm Password are not equal.")
            return
        if username in self.listUser:
            print("User already exists.")
            return
        self.createUserInode(username, password)