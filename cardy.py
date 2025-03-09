from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
import pygame
import hashlib

NO_CARD_ID = -1
NO_ATR = ""

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


class RfidObserver(CardObserver):
    def __init__(self, card_atrs, uid_reader, event_insert, event_remove, event_comm_error):
        self._card_atrs = {}
        self._inv_card_atrs = {}
        self._uid_reader = uid_reader

        for i in range(len(card_atrs)):
            self._card_atrs[i] = card_atrs[i]
            self._inv_card_atrs[card_atrs[i]] = i

        self._ev_insert = event_insert
        self._ev_remove = event_remove
        self._ev_comm_error = event_comm_error
        self._atr_inserted = NO_ATR
        self._id_inserted = NO_CARD_ID

    def calc_card_id_removed(self, card):
        atr = toHexString(card.atr)

        # card ATR must be known
        if not (atr in self._inv_card_atrs.keys()):
            return NO_CARD_ID, False

        # removed card has to be of the type which is currently inserted
        if atr != self._atr_inserted:
            return NO_CARD_ID, False

        help = self._id_inserted
        self._id_inserted = NO_CARD_ID
        self._atr_inserted = NO_ATR

        return help, True

    def calc_card_id_inserted(self, card):
        atr = toHexString(card.atr)

        # card ATR must be known
        if not (atr in self._inv_card_atrs.keys()):
            return NO_CARD_ID, False
        
        card_id, ok = self._uid_reader.make_card_id(card, self._inv_card_atrs[atr])
        if not ok:
            return NO_CARD_ID, False

        self._atr_inserted = atr        
        self._id_inserted = card_id
        return self._id_inserted, True


    def update(self, observable, actions):
        (added_cards, removed_cards) = actions

        for card in removed_cards:
            # Only do something if there is a card inserted at the moment
            if self._atr_inserted != NO_ATR:
                id, ok = self.calc_card_id_removed(card)
                if ok:
                    pygame.event.post(pygame.event.Event(self._ev_remove, card_id=id))
                else:
                    pygame.event.post(pygame.event.Event(self._ev_comm_error))
                    
        for card in added_cards:
            # Only do something if there is no card inserted at the moment
            if self._atr_inserted == NO_ATR:
                id, ok = self.calc_card_id_inserted(card)
                if ok:
                    pygame.event.post(pygame.event.Event(self._ev_insert, card_id=id, beep=True))
                else:
                    pygame.event.post(pygame.event.Event(self._ev_comm_error))

class CardManager:
    def __init__(self, known_atrs, uid_reader, event_insert, event_remove, event_comm_error):
        self._monitor = CardMonitor()
        self._observer = RfidObserver(known_atrs, uid_reader, event_insert, event_remove, event_comm_error)

    def start(self):
        self._monitor.addObserver(self._observer)

    def destroy(self):
        self._monitor.deleteObserver(self._observer)

