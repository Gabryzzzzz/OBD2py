import tm1637
TMs = []

def aggiungi_display(clk, dio):
    TMs.append(tm1637.TM1637(clk=clk, dio=dio))


def setup_led_display():
    aggiungi_display(23, 24)
    TMs[0].number(0000)
    aggiungi_display(25, 8)
    TMs[1].number(0000)
    aggiungi_display(7, 1)
    TMs[2].number(0000)



