
def buzzer_off(card):
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