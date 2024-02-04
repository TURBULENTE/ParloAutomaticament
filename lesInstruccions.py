#!bin/bash -i
import time
import markovify
import soundcard as sc
import soundfile as sf
import subprocess
from gtts import gTTS
import nltk
from random import randrange
import random
import re
#from pynput.keyboard import Key, Controller
#Path para markovify
from sys import path as syspath
from os import path as ospath
from nltk.corpus import stopwords
from inputimeout import inputimeout
#nltk.download('stopwords')
#nltk.download('punkt')
from nltk.tokenize import word_tokenize
all_stopwords = stopwords.words('spanish')


#Las stop words están consideradas en castellano y catalán. 
swords = ['?', '¿', '!', '¡', "que", "pero", "ante", "con", "si", "no", "se", "contra", "hacia", "sin", "tras", "durante", "en","por","desde","para","bajo", "però", "davant", "amb", "sense", "després", "durant", "per"]
all_stopwords.extend(swords)
syspath.append(ospath.join(ospath.expanduser("~"), '/home/tresymedio/.local/lib/python3.9/site-packages/markovify/')) #adaptar al path...
syspath.append(ospath.join(ospath.expanduser("~"), '/home/tresymedio/.local/lib/python3.9/site-packages/nltk/'))  #adaptar al path...

import serial


## Función para text-to-speech: Graba un archivo mp3 con el texto sintentizado y lo reproduce (utiliza el tts de google).
def speak(text):
    tts = gTTS(text=text, lang='ca')
    fname = "respuesta.mp3"
    tts.save(fname)
    subprocess.call(["ffplay", "-v", "0", "-nodisp", "-autoexit","respuesta.mp3"])

# Función para limpiar texto utilizando la libreria "re"
def clean(text):
    text = re.sub('\W', ' ', text) # Remplaza caracteres no alfanuméricos por espacios
    text = text.lower() # todas las letras en minúsculas
    text = re.sub(r'á', 'a', text) # elimina acentos
    text = re.sub(r'é', 'e', text)
    text = re.sub(r'í', 'i', text)
    text = re.sub(r'ó', 'o', text)
    text = re.sub(r'ú', 'u', text)
    return text

# Abre archivos de texto y los guarda en "text_{a,b,c,d}"
with open("cocina.txt") as f:
    text_a = f.read()
with open("politica.txt") as g:
    text_b = g.read()
with open("sostenibilidad.txt") as h:
    text_c = h.read()

# Limpia el texto con función clean() para eliminar caracteres no alfanumŕicos y acentos.
text_a = clean(text_a)
text_b = clean(text_b)
text_c = clean(text_c)


# Aplica markovify: calcula la matriz de probabilidades de sucesión de palabras.
co = markovify.Text(text_a, state_size=1) # state_size = número de palabras de la que depende la probabilidad de una nueva palabra. 1 es lo más chico.
po = markovify.Text(text_b, state_size=1)
so = markovify.Text(text_c, state_size=1)

#1er Entrenamiento
model_combo = markovify.combine([co,po,so], [0.1, 0.8, 0.1])

# FLAG 2: aquí puedes elegir ir a flag 0 o flag 1. Se empieza así el loop
# 2. Si escribes 1, pasas a flag 0.
# 3. Si escribes 2 pasas a flag 1.

# Tecla 1 - FLAG 0: Construye cada segundo una frase con el modelo de markov.
# 1. Para poder cambiar a otra parte del programa (cambiar flag) tiene un input con tiempo límite:
# - 1 para quedarse
# - 2 para ir a flag 1
# - 3 para regresar a flag 2

# Tecla 2 - FLAG 1: Preguntarle cosas a la bot y responde a partir de una palabra rescatada de la pregunta
# 1. Escribir cualquier pregunta. Tratará de encontrar alguna palabra que pueda utilizar como inicial en la cadena de Markov.
# Si no lo logra después de 100 intentos, desiste con "No tengo información suficiente para contestar".
# Si no se ha escrito nada coherente o no detecta alguna palabra que funcione después de limpiarla, sale del loop y dice "No me has hecho una pregunta"
# 2. Para salir de esta parte (flag 1), podemos escribir:
# - 1 para ir a flag 0
# - 2 para quedarse en flag 1
# - 3 para regresar a flag 2


flag = 2
flag2= 0

while(True):
    while flag == 2:
        start = input("")
        if start == "1":
            flag = 0
        if start == "2":
            flag = 1
        if start=="3":
            flag = 2

    while flag == 0:
            model_combo = model_combo.compile()
            print(" ")
            new_text = model_combo.make_short_sentence(300, max_overlap_ratio = 0.7)
            if new_text == None:
                print("Un moment, estic buscant informació per a escriure...")
            else:
                print(new_text)
                speak(new_text)
            time.sleep(1)
            flag2=1

            while flag2 == 1:
                try:
                    cue = inputimeout("", timeout=2)
                    if cue == "1":
                        flag = 0
                    if cue == "2":
                        flag = 1
                        flag2= 0
                    if cue == "3":
                        flag = 2
                        flag2 = 0

                except Exception:
                    flag2 = 0

    while flag == 1:
        q = input("\n Què vols saber?")
        if q == "1":
            flag = 0
        else:
            if q == "2":
                flag = 1
            else:
                if q == "3":
                    flag = "2"
                else:
                    if q != "":
                        try:
                            words = q
                            words = clean(words)
                            words_tokens = word_tokenize(words)
                            words_wo_sw = [word for word in words_tokens if not word in all_stopwords]
                            rword = random.choice(words_wo_sw)
                            model_combo = model_combo.compile()
                            print(" ")
                            new_text = model_combo.make_short_sentence(300, max_overlap_ratio = 0.7)
                            clean_text = clean(new_text)
                            count = 0
                            t = 0
                            while rword not in clean_text:
                                rword = random.choice(words_wo_sw)
                                t += 1
                                count += 1

                                if(t > 5):
                                    new_text = model_combo.make_short_sentence(300, max_overlap_ratio = 0.7)
                                    clean_text = clean(new_text)
                                    t = 0

                                if(count > 50):
                                    print("Ho sento. No tinc informació suficient per a contestar. Fes una altra pregunta.")
                                    speak("Ho sento. No tinc informació suficient per a contestar. Fes una altra pregunta.")
                                    count = 0
                                    t = 0
                                    break

                            if rword in clean_text:
                                print(new_text)
                                speak(new_text)
                                count = 0
                                t = 0
                        except:
                            print("Ho sento. No tinc informació suficient per a contestar. Fes una altra pregunta.")
                            speak("Ho sento. No tinc informació suficient per a contestar. Fes una altra pregunta.")
