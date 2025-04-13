#! /usr/bin/env python3

import os
from smartcard.CardMonitoring import CardMonitor, CardObserver
from soundyconsts import *
import uidfactory


class CardIdObserver(CardObserver):
    def __init__(self, uid_repo):
        
        self._uid_repo = uid_repo

    def _acr122u_buzzer_off(self, card):
        try:
            card.connection = card.createConnection()
            card.connection.connect()
            response, sw1, sw2 = card.connection.transmit([0xFF, 0x00, 0x52, 0x00, 0x00])
            if (sw1 != 0x90) or (sw2 != 0x00):
                return None

            res = response
        except:
            res = None

        return res

    def update(self, _, actions):
        (addedcards, removedcards) = actions

        for card in addedcards:
            res = self._acr122u_buzzer_off(card)
            if res != None:
                print("Buzzer switched off")
            else:
                print("Turning off buzzer failed")
            

        for card in removedcards:
            pass


if __name__ == "__main__":
    try:
        os.system(CLEAR_COMMAND)
        u = uidfactory.UidReaderRepo()
        print(f"Put any card on the reader to switch buzzer off")
        cardmonitor = CardMonitor()
        uid_observer = CardIdObserver(u)
        cardmonitor.addObserver(uid_observer)

        input("Press Enter to stop\n\n")
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e)
    finally:
        cardmonitor.deleteObserver(uid_observer)