from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Value
from multiprocessing import current_process
import time, random

class Table():
    def __init__(self,NPHIL,manager):
        self.NPHIL = NPHIL
        self.phil = manager.list([False]*NPHIL) # phil[i] <=> el filosofo i esta comiendo
        self.current_phil = None # filosofo actual
        self.eating = Value('i', 0) # la cantidad de filosofos que estan comiendo
        self.times_eating = 0 # para comprobar cuantas veces come cada uno
        self.mutex = Lock()
        self.free_fork = Condition(self.mutex) # si los de la derecha y la izquierda estan comiendo
    
    def lr_not_eating(self): # devuelve si el de la izq y la dr estan comiendo
        i = self.current_phil
        ir = i-1
        il = (i+1) % self.NPHIL
        return not self.phil[ir] and not self.phil[il]
    
    def set_current_phil(self,phil): # phil es num en philosopher_task
        self.current_phil = phil
    
    def wants_eat(self,num):
        self.mutex.acquire()
        self.set_current_phil(num)
        self.free_fork.wait_for(self.lr_not_eating)
        self.phil[self.current_phil] = True
        self.eating.value = self.eating.value + 1
        self.times_eating += 1
        #print(f"Philosofer {self.current_phil} has been eating {self.times_eating.value} times")
        self.mutex.release()
    
    def wants_think(self,num):
        self.mutex.acquire()
        self.set_current_phil(num)
        self.phil[self.current_phil] = False
        self.eating.value = self.eating.value - 1
        self.free_fork.notify_all()
        self.mutex.release()


    
class CheatMonitor():
    def __init__(self):
        self.eating = Value('i',0)
        self.mutex = Lock()
        self.other_eating = Condition(self.mutex)
    
    def is_eating(self,num):
        self.mutex.acquire()
        self.other_eating.notify()
        self.eating.value = self.eating.value + 1
        self.mutex.release()
    
    def other_is_eating(self):
        return self.eating.value > 1 # hay que esperar a que el otro este tambien comiendo

    def wants_think(self,num):
        self.mutex.acquire()
        #print(f"Quiere dejar de comer {num} ({self.eating.value})")
        self.other_eating.wait_for(self.other_is_eating)
        self.eating.value = self.eating.value - 1
        self.mutex.release()




class AnticheatTable():
    def __init__(self,NPHIL,manager):
        self.NPHIL = NPHIL
        self.phil = manager.list([False]*NPHIL) # phil[i] <=> el filosofo i esta comiendo
        self.hungry = manager.list([False]*NPHIL) # hungry[i] <=> el filosofo i no esta comiendo pero quiere comer
        self.current_phil = None # filosofo actual
        self.eating = Value('i', 0) # la cantidad de filosofos que estan comiendo
        self.times_eating = 0 # para comprobar cuantas veces come cada uno
        self.mutex = Lock()
        self.free_fork = Condition(self.mutex) # si los de la derecha y la izquierda estan comiendo
        self.chungry = Condition(self.mutex)
    
    def lr_not_eating(self): # devuelve si el de la izq y la dr estan comiendo
        i = self.current_phil
        ir = i-1
        il = (i+1) % self.NPHIL
        return not self.phil[ir] and not self.phil[il]
    
    def set_current_phil(self,phil): # phil es num en philosopher_task
        self.current_phil = phil
    
    def right_fork_free(self):
        right_index = (self.current_phil + 1) % self.NPHIL
        return not self.hungry[right_index]
    
    def wants_eat(self,num):
        self.mutex.acquire()
        self.set_current_phil(num)
        self.chungry.wait_for(self.right_fork_free)
        self.hungry[self.current_phil] = True
        self.free_fork.wait_for(self.lr_not_eating)
        self.phil[self.current_phil] = True
        self.eating.value = self.eating.value + 1
        self.times_eating += 1
        self.hungry[self.current_phil] = False
        self.chungry.notify_all()
        #print(f"Philosofer {self.current_phil} has been eating {self.times_eating.value} times")
        self.mutex.release()
    
    def wants_think(self,num):
        self.mutex.acquire()
        self.set_current_phil(num)
        self.phil[self.current_phil] = False
        self.eating.value = self.eating.value - 1
        self.free_fork.notify_all()
        self.mutex.release()
