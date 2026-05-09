from abc import ABC, abstractmethod

# Base class for vision extraction 
class BaseVisionProvider(ABC):
    @abstractmethod
    async def extract(self,image_base64:str, mime_type:str)->dict:
        pass