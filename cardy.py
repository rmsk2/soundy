from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
import pygame
from soundyconsts import *


class RfidObserver(CardObserver):
    def __init__(self, card_atrs, uid_repo, event_insert, event_remove, event_comm_error, event_first_card):
        self._card_atrs = {}
        self._inv_card_atrs = {}
        self._uid_repo = uid_repo

        for i in range(len(card_atrs)):
            self._card_atrs[i] = card_atrs[i]
            self._inv_card_atrs[card_atrs[i]] = i

        self._ev_insert = event_insert
        self._ev_remove = event_remove
        self._ev_comm_error = event_comm_error
        self._ev_first_card = event_first_card
        self._atr_inserted = NO_ATR
        self._id_inserted = NO_CARD_ID
        self._insert_count = 0

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
        
        uid_reader = self._uid_repo.to_uid_r(atr)
        card_id, ok = uid_reader.make_card_id(card)
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
                    pygame.event.post(pygame.event.Event(self._ev_comm_error, err_type=ERR_TYPE_COMM, err_msg="Card error at removal"))
                    
        for card in added_cards:
            # Only do something if there is no card inserted at the moment
            if self._atr_inserted == NO_ATR:
                id, ok = self.calc_card_id_inserted(card)
                if ok:
                    # Hook to turn off acr122U buzzer when first card is inserted
                    if self._insert_count == 0:
                        pygame.event.post(pygame.event.Event(self._ev_first_card, card_obj=card))

                    self._insert_count += 1

                    pygame.event.post(pygame.event.Event(self._ev_insert, card_id=id, beep=True))
                else:
                    pygame.event.post(pygame.event.Event(self._ev_comm_error, err_type=ERR_TYPE_COMM, err_msg="Card error at insertion"))

class CardManager:
    def __init__(self, known_atrs, uid_reader, event_insert, event_remove, event_comm_error, event_first_card):
        self._monitor = CardMonitor()
        self._observer = RfidObserver(known_atrs, uid_reader, event_insert, event_remove, event_comm_error, event_first_card)

    def start(self):
        self._monitor.addObserver(self._observer)

    def destroy(self):
        self._monitor.deleteObserver(self._observer)

