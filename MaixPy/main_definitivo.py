import sensor
import image
import lcd
import time
import audio
from Maix import I2S


# Inizializzazione display e fotocamera
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=4000)
sensor.run(1)

# Funzione per calibrare la fotocamera con media RGB 10x10
def calibrazione_fotocamera(rgb_noti, lab_noti):
    print("Posizionare un cartolina davanti alla fotocamera...")
    time.sleep(2)

    # Cattura l'immagine
    img = sensor.snapshot()
    lcd.display(img)  # Mostra l'immagine sul display


    # Definisce la matrice 10x10 al centro dell'immagine
    width, height = img.width(), img.height()
    centro_x, centro_y = width // 2, height // 2
    offset = 5  # Metà della matrice 10x10

    # Somma i valori RGB dei pixel nella matrice 10x10
    r_totali, g_totali, b_totali = 0, 0, 0
    pixel_count = 0

    for x in range(centro_x - offset, centro_x + offset):
        for y in range(centro_y - offset, centro_y + offset):
            r, g, b = img.get_pixel(x, y)
            r_totali += r
            g_totali += g
            b_totali += b
            pixel_count += 1

    # Calcola la media dei valori RGB
    r_misurato = r_totali // pixel_count
    g_misurato = g_totali // pixel_count
    B_misurato = b_totali // pixel_count


    l_misurato, a_misurato, b_misurato = rgb_to_lab(r_misurato, g_misurato, B_misurato)

    print("Colore medio misurato: R={}, G={}, B={}, l={}, a={}, b={}".format(r_misurato, g_misurato, B_misurato, l_misurato, a_misurato, b_misurato))




    # Calcola i fattori di correzione, mettere controllo zero e limiti
    if r_misurato == 0 :
        r_misurato = 1

    R_factor = rgb_noti[0] / r_misurato

    if R_factor > 1.2 :
        R_factor = 1.2

    if R_factor < 0.8 :
        R_factor = 0.8

    if g_misurato == 0 :
        g_misurato = 1

    G_factor = rgb_noti[1] / g_misurato

    if G_factor > 1.2 :
        G_factor = 1.2

    if G_factor < 0.8 :
        G_factor = 0.8

    if B_misurato == 0 :
        B_misurato = 1

    B_factor = rgb_noti[2] / B_misurato

    if B_factor > 1.2 :
        B_factor = 1.2

    if B_factor < 0.8 :
        B_factor = 0.8



    if l_misurato == 0 :
        l_misurato = 1

    l_factor = lab_noti[0] / l_misurato

    if l_factor > 1.2 :
        l_factor = 1.2

    if l_factor < 0.8 :
        l_factor = 0.8

    if a_misurato == 0 :
        a_misurato = 1

    a_factor = lab_noti[1] / a_misurato

    if a_factor > 1.2 :
        a_factor = 1.2

    if a_factor < 0.8 :
        a_factor = 0.8

    if b_misurato == 0 :
        b_misurato = 1

    b_factor = lab_noti[2] / b_misurato

    if b_factor > 1.2 :
        b_factor = 1.2

    if b_factor < 0.8 :
        b_factor = 0.8

    print("Fattori di correzione: R'={}, G'={}, B'={}, l'={}, a'={}, b'={}".format(R_factor, G_factor, B_factor, l_factor, a_factor, b_factor))
    return R_factor, G_factor, B_factor, l_factor, a_factor, b_factor



# Rilevamento blob
def rileva_blob():

    print("Inizio ricerca blob...")
    time.sleep(1)

    # Range LAB del colore

    rosso_lab = (53, 80, 67)
    verde_lab = (87, -86, 83)
    blu_lab = (32, 79, -107)


    l_rosso = 53/l_factor
    a_rosso = 80/a_factor
    b_rosso = 67/b_factor

    l_verde = 70/l_factor
    a_verde = -60/a_factor
    b_verde = 60/b_factor

    l_blu = 32/l_factor
    a_blu = 79/a_factor
    b_blu = -107/b_factor

    #blue_thresholds = (int(l_blu - 30), int(l_blu + 30), int(a_blu - 100), int(a_blu + 20), int(b_blu - 10), int(b_blu + 100))
    #red_thresholds = (int(l_rosso - 30), int(l_rosso + 10), int(a_rosso - 50), int(a_rosso + 20), int(b_rosso - 60), int(b_rosso + 20))
    #green_thresholds = (int(l_verde - 40), int(l_verde + 10), int(a_verde - 10 ), int(a_verde + 50), int(b_verde - 60), int(b_verde + 10))

    blue_thresholds = (10, 60, -50, 80, -128, 30)
    red_thresholds = (0, 100, 0, 127, -50, 50)
    green_thresholds = (10, 80, -128, 0, -50, 127)
    lista_threshold  = [red_thresholds, green_thresholds, blue_thresholds]

    lista_blob  =  []

    for color_threshold in lista_threshold:
        # Ottiene l'orario di inizio in secondi
        start_time = time.time()

        # Ciclo while che dura 3 secondi
        while time.time() - start_time < 3:

            img=sensor.snapshot()
            blobs = img.find_blobs([color_threshold])

            if blobs:
                    larger_blob = max(blobs, key=lambda b: b.pixels())  # Trova il blob più grande con quel colore

                    # Disegna un rettangolo attorno al blob rilevato
                    img.draw_rectangle(larger_blob.rect())
                    lcd.display(img)
                    lista_blob.append(larger_blob)
            else:
                print("errore")

    # Trova il blob più grande tra quello rosso, blu o verde
    if lista_blob :
        largest_blob =  max(lista_blob, key=lambda b: b.pixels())
    else:
        print('Nessun blob trovato')
        r,g,b= 0,0,0
        return r, g, b

    # Ottiene i valori RGB al centro del blob (metodo alternativo rispetto a width e height//2)
    cx = largest_blob.cx()
    cy = largest_blob.cy()
    offset = 5  # Metà della matrice 10x10

    # Somma i valori RGB dei pixel nella matrice 10x10
    r_totali, g_totali, b_totali = 0, 0, 0
    pixel_count = 0

    for x in range(cx - offset, cx + offset):
        for y in range(cy - offset, cy + offset):
            r, g, b = img.get_pixel(x, y)
            r_totali += r
            g_totali += g
            b_totali += b
            pixel_count += 1

    # Calcola la media dei valori RGB
    R = r_totali // pixel_count
    G = g_totali // pixel_count
    B = b_totali // pixel_count

    # Applica i fattori di correzione
    r = R*R_factor
    g = G*G_factor
    b = B*B_factor

    print("Valori RGB rilevati - R:", r, "G:", g, "B:", b)
    return r,g,b





# Funzione per convertire RGB a XYZ
def rgb_to_xyz(r, g, b):

    # Normalizza i valori RGB su scala da 0 a 1
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0

    # Correzione gamma
    r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4

    # Converti in XYZ (standard illuminant D65)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    return x, y, z

# Funzione per convertire XYZ a LAB
def xyz_to_lab(x, y, z):

    # D65 white point
    x_ref = 0.95047
    y_ref = 1.00000
    z_ref = 1.08883

    # Normalizza
    x = x / x_ref
    y = y / y_ref
    z = z / z_ref

    # Funzione di aiuto per la trasformazione
    def f(t):
        return t ** (1/3) if t > 0.008856 else (7.787 * t + 16 / 116)

    l = 116 * f(y) - 16
    a = 500 * (f(x) - f(y))
    b = 200 * (f(y) - f(z))

    return l, a, b

# Funzione principale per convertire RGB a LAB
def rgb_to_lab(r, g, b):
    x, y, z = rgb_to_xyz(r, g, b)
    return xyz_to_lab(x, y, z)

def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    diff = mx - mn

    if mx == mn:
        hue = 0
    elif mx == r:
        hue = (60 * ((g-b)/diff) + 360) % 360
    elif mx == g:
        hue = (60 * ((b-r)/diff) + 120) % 360
    else:
        hue = (60 * ((r-g)/diff) + 240) % 360

    if mx == 0:
        s = 0
    else:
        s = (diff/mx) * 100

    v = mx * 100

    return (hue, s, v)





# Valori RGB noti del colore di riferimento (hardcoded)
rgb_rosso_noto = [213, 1, 50]
rgb_verde_noto = [168, 173, 1]
rgb_blu_noto = [6, 107, 139]

lab_rosso_noto = [45, 71, 37]
lab_verde_noto = [68, -18, 70]
lab_blu_noto = [42, -13.5, -25]

# Calibra la fotocamera e ottieni i fattori di correzione
r_rosso_factor, g_rosso_factor, B_rosso_factor, l_rosso_factor, a_rosso_factor, b_rosso_factor = calibrazione_fotocamera(rgb_rosso_noto, lab_rosso_noto)
time.sleep(3)

r_verde_factor, g_verde_factor, B_verde_factor, l_verde_factor, a_verde_factor, b_verde_factor = calibrazione_fotocamera(rgb_verde_noto, lab_verde_noto)
time.sleep(3)

r_blu_factor, g_blu_factor, B_blu_factor, l_blu_factor, a_blu_factor, b_blu_factor = calibrazione_fotocamera(rgb_blu_noto, lab_blu_noto)
time.sleep(3)

r_somma_factor = r_rosso_factor + r_verde_factor + r_blu_factor
g_somma_factor = g_rosso_factor + g_verde_factor + g_blu_factor
B_somma_factor = B_rosso_factor + B_verde_factor + B_blu_factor

R_factor = r_somma_factor/3
G_factor = g_somma_factor/3
B_factor = B_somma_factor/3


l_somma_factor = l_rosso_factor + l_verde_factor + l_blu_factor
a_somma_factor = a_rosso_factor + a_verde_factor + a_blu_factor
b_somma_factor = b_rosso_factor + b_verde_factor + b_blu_factor

l_factor = l_somma_factor/3
a_factor = a_somma_factor/3
b_factor = b_somma_factor/3


while True:

    # Esegui il rilevamento dei blob con i valori RGB corretti
    r,g,b =rileva_blob()

    hue, s, v = rgb_to_hsv(r, g, b)

    print('Valori HSV :', hue, s, v)

    # Verifica il colore e riproduce il file audio corrispondente
    if (hue > 300 or hue < 60)  and  s <= 50  and  v < 50 :
        print("Colore rilevato: Rosso     Accordo riprodotto: Do3 Maggiore")

    elif (hue > 300 or hue < 60)  and  s >= 50  and  v < 50 :
        print("Colore rilevato: Rosso     Accordo riprodotto: Do3 Minore")

    elif (hue > 300 or hue < 60)  and  s <= 50  and  v > 50 :
        print("Colore rilevato: Rosso     Accordo riprodotto: Re3 Maggiore")

    elif (hue > 300 or hue < 60)  and  s >= 50  and  v > 50 :
        print("Colore rilevato: Rosso     Accordo riprodotto: Re3 Minore")

    elif (hue >= 60 and hue <= 180)  and  s <= 50  and  v < 50  :
        print("Colore rilevato: Verde     Accordo riprodotto: Do4 Maggiore")

    elif (hue >= 60 and hue <= 180)  and  s >= 50  and  v < 50  :
        print("Colore rilevato: Verde     Accordo riprodotto: Do4 Minore")

    elif (hue >= 60 and hue <= 180)  and  s <= 50  and  v > 50  :
        print("Colore rilevato: Verde     Accordo riprodotto: Re4 Maggiore")

    elif (hue >= 60 and hue <= 180)  and  s >= 50  and  v > 50  :
        print("Colore rilevato: Verde     Accordo riprodotto: Re4 Minore")

    elif (hue > 180 and hue <= 300)  and  s <= 50  and  v < 50  :
        print("Colore rilevato: Blu       Accordo riprodotto: Do5 Maggiore")

    elif (hue > 180 and hue <= 300)  and  s >= 50  and  v < 50  :
        print("Colore rilevato: Blu       Accordo riprodotto: Do5 Minore")

    elif (hue > 180 and hue <= 300)  and  s <= 50  and  v > 50  :
        print("Colore rilevato: Blu       Accordo riprodotto: Re5 Maggiore")

    elif (hue > 180 and hue <= 300)  and  s >= 50  and  v > 50  :
        print("Colore rilevato: Blu       Accordo riprodotto: Re5 Minore")



