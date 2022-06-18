from typing import Set
from domain.app import App
import abc


class AppRepository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def getInventory(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def getInventoryAsDto(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def getAppById(self, id: str) -> App:
        raise NotImplementedError
