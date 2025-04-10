from smartcard.util import toHexString
from soundyconsts import *
import desfire


class DummyReader(IUidReader):
    def __init__(self, id, name, atr):
        self._id = id
        self._name = name
        self._atr = atr

    def make_card_id(self, card: Any, default_id: int) -> tuple[int, bool]:
        return self._id, True

    def get_atr(self) -> str:
        return self._atr

    def get_name(self) -> str:
        return self._name


class UidReaderRepo:
    def __init__(self):
        self._atr_map = {}
        self.add_known_cards()

    def add_known_cards(self):
        self._atr_map[ATR_DES_FIRE] = desfire.DESFireUidReader(ATR_DES_FIRE)
        self._atr_map[ATR_E_PERSO] = DummyReader(UidReaderRepo.get_default_id(ATR_E_PERSO), "German national ID card", ATR_E_PERSO)
        self._atr_map[ATR_GIRO] = DummyReader(UidReaderRepo.get_default_id(ATR_GIRO), "German Giro card", ATR_GIRO)
        self._atr_map[ATR_EGK] = DummyReader(UidReaderRepo.get_default_id(ATR_EGK), "German electronic health card", ATR_EGK)

    @staticmethod
    def get_default_id(atr):
        index = 0
        for i in ALL_ATRS:
            if i == atr:
                return index
            else:
                index += 1
        
        raise Exception(f"Unknown atr {atr}")

    def to_uid_r(self, atr):
        if atr in self._atr_map.keys():
            return self._atr_map[atr]
        else:
            raise Exception(f"Unknown atr {atr}")