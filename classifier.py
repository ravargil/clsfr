import os
import datetime
from datetime import datetime
from abc import ABCMeta, abstractmethod
from PIL import Image
import imghdr

class BaseFileSelector:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_files(self): raise NotImplementedError

    @abstractmethod
    def get_dirs(self): raise NotImplementedError

    @abstractmethod
    def generate_file_key(self, file_path): raise NotImplementedError


class DateFilesSelector(BaseFileSelector):

    str_format = "%Y-%m-%d"
    def __init__(self, classification_strategy="day", *args, **kwargs):
        if ("month" == classification_strategy.lower()):
            self.str_format = "%Y-%m"
        if ("year" == classification_strategy.lower()):
            self.str_format = "%Y"
        return super().__init__(*args, **kwargs)

    def get_files(self, current_dir):
        return [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))]

    def get_dirs(self, current_dir):
        return [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]

    def generate_file_key(self, file_path): 
        modified_timestamp = os.path.getmtime(os.path.abspath(file_path))
        date = datetime.fromtimestamp(modified_timestamp)
        return date.strftime(self.str_format)

class ExifDateFilesSelector(DateFilesSelector):

    # https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif/datetimeoriginal.html
    exif_date_time_original_tag = 0x9003
    exif_date_time_format = "%Y:%m:%d %H:%M:%S"

    def __init__(self, classification_strategy='day', *args, **kwargs):
        return super().__init__(classification_strategy=classification_strategy, *args, **kwargs)

    def generate_file_key(self, file_path):
        full_path = os.path.abspath(file_path)
        is_img = imghdr.what(full_path)
        # check if is image: is_img will be None if this is not an image
        if not is_img:
            return super().generate_file_key(file_path)

        try:
            with Image.open(full_path) as im:
                exif = im._getexif()
        except IOError:
            # if the given path is not an image, return the super's key
            return super().generate_file_key(file_path)

        # if image exif doesn't contain the date taken property, return the super's key
        if not (self.exif_date_time_original_tag in exif):
            return super().generate_file_key(file_path)

        original_date_str = exif[0x9003]
        date = datetime.strptime(original_date_str, self.exif_date_time_format)
        return date.strftime(self.str_format)

class FilesClassifier:

    def __init__(self, files_selector: BaseFileSelector):
        self.__files_dict = dict()
        self.__files_selector = files_selector

    def classify(self, rootdir: str):
        self.__files_dict.clear()
        self.__classify(rootdir)    

    def __iter__(self):
        for key in self.__files_dict:
            arr = self.__files_dict[key]
            for item in arr:
                yield (key, item)

    def __next__(self):
        self.next()

    def __classify(self, current_dir):
        
        if ((not os.path.isdir(current_dir)) or (not (os.path.exists(current_dir))) ):
            return
        os.chdir(current_dir)
        
        only_files = self.__files_selector.get_files(current_dir)
        only_dirs = self.__files_selector.get_dirs(current_dir)
        self.__process_files__(only_files)
        
        for item in only_dirs:
            self.__classify(current_dir + "\\" + item)

    def __process_files__(self, only_files):
        for f in only_files:
            dir_name = self.__files_selector.generate_file_key(f)
            #if not found, addit:
            if (not(dir_name in self.__files_dict)):
                self.__files_dict[dir_name] = []
            self.__files_dict[dir_name].append(os.path.abspath(f))

