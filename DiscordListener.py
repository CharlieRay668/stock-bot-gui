import pickle
import os

DIRECTORY = 'listeners'

class Listener:
    def __init__(self, username, listeners = []):
        self.username = username
        self.listeners = listeners
        self.save_self(DIRECTORY)
    
    def __str__(self):
        string = 'These People: '
        for name in self.listeners:
            string += str(name) + ' '
        string += 'Are listening to : ' + str(self.username)
        return string

    def get_username(self):
        return self.username

    def get_listeners(self):
        return self.listeners
    
    def add_listener(self, listerner):
        self.listeners.append(listerner)
        self.save_self(DIRECTORY)

    def remove_listener(self, listener):
        self.listeners.remove(listener)
        self.save_self(DIRECTORY)

    def save_self(self, directory):
        path = directory + '/' + self.username
        try:
            pickle.dump(self, open(path + '.lstn', 'wb'))
        except:
            os.mkdir(path)
            pickle.dump(self, open(path + '.lstn', 'wb'))
        
    @staticmethod
    def load_listener(directory, name):
        path = directory + '/' + name + '.lstn'
        try:
            return pickle.load(open(path, 'rb'))
        except:
            return '404: Error, Account not found.'
