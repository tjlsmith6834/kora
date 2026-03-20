import io

class FileWrapper(io.BytesIO):
    def __init__(self, file_bytes: bytes, name: str):
        super().__init__(file_bytes)
        self.name = name

    @property
    def file(self):
        return self