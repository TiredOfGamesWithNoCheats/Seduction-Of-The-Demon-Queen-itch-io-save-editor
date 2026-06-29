from godot_crypto import GodotCrypto
from config_parser import GodotConfig


class SaveFile:

    def __init__(self):
        self.filename = None
        self.config = None

    @classmethod
    def load(cls, filename):

        self = cls()

        self.filename = filename

        plaintext = GodotCrypto.load(filename)

        self.config = GodotConfig.loads(
            plaintext.decode("utf-8")
        )

        return self

    def save(self):

        text = self.config.dumps()

        GodotCrypto.save(
            self.filename,
            text.encode("utf-8")
        )