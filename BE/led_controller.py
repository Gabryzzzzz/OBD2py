import tm1637

TMs = []

def aggiungi_display(clk, dio):
    TMs.append(tm1637.TM1637(clk=clk, dio=dio))