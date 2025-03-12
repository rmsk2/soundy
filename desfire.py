import hashlib
from smartcard.util import toHexString

class DESFireUidReader:
    def __init__(self, watched_atr):
        self._atr = watched_atr
        # Taken and corrected from https://ridrix.wordpress.com/2009/09/19/mifare-desfire-communication-example/
        self._apdu_get_version = [0x90, 0x60, 0x00, 0x00, 0x00]
        self._apdu_read_next   = [0x90, 0xAF, 0x00, 0x00, 0x00]
    
    def uid_to_card_id(self, d):
        t = hashlib.md5(bytes(d)).digest()[0:2]
        return t[1]*256 + t[0]

    def make_card_id(self, card, default_id):
        if self._atr != toHexString(card.atr):
            return default_id, True

        uid = self.read_des_fire_uid(card)
        if uid == None:
            return default_id, False

        new_id = self.uid_to_card_id(uid)

        return new_id, True

    def read_des_fire_uid(self, card):
        try:
            card.connection = card.createConnection()
            card.connection.connect()
            version_bytes = []
            response, _, sw2 = card.connection.transmit(self._apdu_get_version)
            if sw2 != 0xAF:
                return None

            version_bytes += response
            while sw2 != 0x00:
                response, _, sw2 = card.connection.transmit(self._apdu_read_next)
                version_bytes += response
            
            res = version_bytes[14:21]
        except:
            res = None

        return res
