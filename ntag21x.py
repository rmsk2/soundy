import hashlib
from smartcard.util import toHexString
from soundyconsts import *

class Ntag215UidReader(IUidReader):
    def __init__(self, watched_atr):
        self._atr = watched_atr
        # https://www.acs.com.hk/download-manual/419/API-ACR122U-2.04.pdf
        self._apdu_get_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    
    def get_atr(self):
        return self._atr
    
    def get_name(self):
        return "Ntag215"

    def make_card_id(self, card):
        uid = self._read_ntag_uid(card)
        if uid == None:
            return NO_CARD_ID, False

        t = hashlib.md5(bytes(uid)).digest()[0:2]
        new_id = t[1]*256 + t[0]

        return new_id, True

    def _read_ntag_uid(self, card):
        try:
            card.connection = card.createConnection()
            card.connection.connect()
            response, sw1, sw2 = card.connection.transmit(self._apdu_get_uid)
            if (sw1 != 0x90) or (sw2 != 0x00):
                return None

            res = response
        except:
            res = None

        return res
