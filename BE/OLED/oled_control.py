import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import time

# --- Configurazione Display ---
# Il display da 0.91 pollici è solitamente 128x32
WIDTH = 128
HEIGHT = 32

# Inizializza l'interfaccia I2C (usando i pin predefiniti del Raspberry Pi: SDA=GPIO2, SCL=GPIO3)
i2c = busio.I2C(board.SCL, board.SDA)

# Crea l'oggetto display SSD1306
# Il tuo display 0.91" (Ver 1.6) usa l'indirizzo I2C 0x3C di default
try:
    disp = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)
except ValueError:
    print("Errore: Impossibile trovare il dispositivo SSD1306 all'indirizzo 0x3C. Controlla i collegamenti.")
    exit()

# Pulisci il display
disp.fill(0)
disp.show()

# --- Preparazione dell'Immagine ---
# Crea una tela per il disegno (1 bit depth, bianco/nero)
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Disegna un rettangolo nero per azzerare l'immagine
draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

# Carica un font. Se non hai 'DejaVuSans.ttf', usane un altro o usa il font di default.
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
except IOError:
    # Se il font non è disponibile, usa il font di default
    font = ImageFont.load_default()

# --- Funzioni di Disegno ---

def mostra_testo(riga1, riga2):
    # Pulisci la tela
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

    # Scrivi il testo
    # Posizione (x, y) per la riga 1 (in alto a sinistra)
    draw.text((0, 0), riga1, font=font, fill=255)
    
    # Posizione (x, y) per la riga 2 (sotto)
    draw.text((0, 15), riga2, font=font, fill=255)

    # Visualizza l'immagine sul display fisico
    disp.image(image)
    disp.show()


# --- Esecuzione ---
try:
    print("Inizio visualizzazione sul display...")
    
    mostra_testo("Ciao, Raspberry Pi!", "OLED SSD1306 OK")
    
    # Aspetta un po'
    time.sleep(5)
    
    # Esempio: Mostra un contatore
    for i in range(3):
        mostra_testo("Contatore:", f"Tempo rimasto: {3 - i}")
        time.sleep(1)
        
    mostra_testo("Finito!", "A presto!")
    time.sleep(3)
    
    # Spegni il display pulendolo
    disp.fill(0)
    disp.show()
    
    print("Display spento.")

except KeyboardInterrupt:
    print("\nInterrotto dall'utente.")
finally:
    # Assicurati che il display sia pulito anche in caso di errore/interruzione
    disp.fill(0)
    disp.show()