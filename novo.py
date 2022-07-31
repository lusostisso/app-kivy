

from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.base import runTouchApp 
from kivy.uix.button import Button 
from kivy.core.window import Window 
from kivy.uix.relativelayout import RelativeLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivymd.uix.card import MDCardSwipe

from kivy.properties import StringProperty
from kivymd.icon_definitions import md_icons
from kivymd.uix.list import OneLineIconListItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

import pyaudio
import wave
import subprocess
import os
import time
import threading
import re

import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from pathlib import Path as caminho

Window.size = (300, 500)

class ScreenManager(ScreenManager):
    pass


class MainWindow(Screen):
    def historico (self):
        self.parent.current = 'historico'
    def account (self):
        self.parent.current = 'login_screen'
    def novo (self):
        self.parent.current = 'novo_prontuario'
    def host (self):
        self.parent.current = 'host'

class LoginWindow(Screen):        
    def on_senha (self, value):
        global senha
        senha = value

    def set_enfermeiro (self, value):
        global login_enfermeiro
        login_enfermeiro = value

    def get_enfermeiro (self):
        return login_enfermeiro

    def verifica (self):
        if 'login_enfermeiro' not in globals():
            self.ids.campo_vazio.text = "insira seu usuário"
        elif 'senha' not in globals():
            self.ids.campo_vazio.text = "insira sua senha" 
        elif login_enfermeiro=="":
            self.ids.campo_vazio.text = "insira seu usuário"
        elif senha=="":
            self.ids.campo_vazio.text = "insira sua senha" 
        else:
            self.parent.current = 'main_screen'
            self.ids.campo_vazio.text = ""
            self.ids.user.text = ""
            self.ids.password.text =""
            

class NovoprontuarioWindow(Screen):
    def set_paciente (self, value):
        global paciente
        paciente = value

    def get_paciente (self):
        return paciente

    def verifica (self):
        if 'paciente' not in globals():
            self.ids.nome_label.text = "insira o nome do paciente"
        elif 'horario' not in globals():
            self.ids.nome_label.text = "insira o horario"
        elif 'data_prontuario' not in globals():
            self.ids.nome_label.text="insira a data"
        else:
            self.ids.nome_label.text=""
            self.parent.current = 'gravacao'

    def set_time(self, instance, time):
        global horario
        horarios = str(time)
        self.ids.time_label.text = horarios
        horario = (horarios.replace(":", "_"))

    def get_time (self):
        return horario
 
    def set_date (self, instance, value, data_range):
        global data_prontuario
        data_prontuarios = str(value)
        self.ids.date_label.text = data_prontuarios
        data_prontuario = (data_prontuarios.replace("-", "_"))

    def get_date (self):
        return data_prontuario

    def on_cancela(self, instance, value, data_range):
        self.ids.date_label.text = "Data não selecionada"

    def on_cancel(self, instance, time):
        self.ids.time_label.text = "horário não selecionado"

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_cancel=self.on_cancel, time=self.set_time)
        time_dialog.open()

    def show_date_picker (self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.set_date, on_cancela=self.on_cancela)
        date_dialog.open()
    def home (self):
        self.parent.current = 'main_screen'
    def historico (self):
        self.parent.current = 'historico'
    def account (self):
        self.parent.current = 'login_screen'
    def host (self):
        self.parent.current = 'host'
class GravacaoWindow(Screen):
    def home (self):
        self.parent.current = 'main_screen'
    def historico (self):
        self.parent.current = 'historico'
    def account (self):
        self.parent.current = 'login_screen'
    def novo (self):
        self.parent.current = 'novo_prontuario'
    def host (self):
        self.parent.current = 'host'

class Historico (Screen):
    def fechar_janela(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.fechar_janela)
        self._popup = Popup(title="Carregar arquivo", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            self.text_input.text = stream.read()

        self.fechar_janela()

    def home (self):
        self.parent.current = 'main_screen'
    def account (self):
        self.parent.current = 'login_screen'
    def novo (self):
        self.parent.current = 'novo_prontuario'
    def host (self):
        self.parent.current = 'host'

class Host (Screen):
    def historico (self):
        self.parent.current = 'historico'
    def account (self):
        self.parent.current = 'login_screen'
    def novo (self):
        self.parent.current = 'novo_prontuario'
    def home (self):
        self.parent.current = 'main_screen'

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


screen = Builder.load_file("my.kv")

class LudApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        return ScreenManager()
        

    def start_recording (self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self._running = True
        self._frames = []
        threading._start_new_thread(self.__recording, ())
    def __recording(self):
        #Set running to True and reset previously recorded frames
        self._running = True
        self._frames = []
        #Create pyaudio instance
        p = pyaudio.PyAudio()
        #Open stream
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        # To stop the streaming, new thread has to set self._running to false
        # append frames array while recording
        while(self._running):
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        # Interrupted, stop stream and close it. Terinate pyaudio process.
        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self._running = False

    #Save file to filename location as a wavefront file.
    def save(self, filename):
        print("Salvando")
        p = pyaudio.PyAudio()
        if not filename.endswith(".wav"):
            filename = filename + ".wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        print("Salvo")

    @staticmethod
    def delete(filename):
        os.remove(filename)

    # Convert wav to mp3 with same name using ffmpeg.exe
    @staticmethod
    def wavTomp3(wav):
        mp3 = wav[:-3] + "mp3"
        # Remove file if existent
        if os.path.isfile(mp3):
            LudApp.delete(mp3)
        # Call CMD command
        subprocess.call('ffmpeg -i "'+wav+'" "'+mp3+'"')
    
    #segunda parte
    def audio_prep (self):
        # arquivos
        audio_mp3 = 'test.mp3'
        audio_wav = 'test.wav'

        # conversão de mp3 para wav
        sound = AudioSegment.from_mp3(audio_mp3)
        sound.export(audio_wav, format='wav')

        # selecionando audio
        audio = AudioSegment.from_file(audio_wav, 'wav')

        # Tamanho em milisegundos
        tamanho = 30000
        # divisão do audio em partes
        partes = make_chunks(audio, tamanho)
        partes_audio=[]
        for i, parte in enumerate(partes):
            # Enumerando arquivo particionado
            parte_name='musica{0}.wav'.format(i)
            # Guardando os nomes das partições em uma lista
            partes_audio.append(parte_name)
            # Exportando arquivos
            parte.export(parte_name, format='wav')

        def transcreve_audio(nome_audio):
            # Selecione o audio para reconhecimento
            r=sr.Recognizer( )
            with sr.AudioFile(nome_audio) as source:
                audio = r.record(source)  # leitura do arquivo de audio

            #Reconhecimento usando o Google Speech Recognition
            try:
                print('Reconhecimento: ' + r.recognize_google(audio,language='pt-BR'))
                texto = r.recognize_google(audio,language='pt-BR')
            except sr.UnknownValueError:
                print('Audio nao foi entendido')
                texto = ''
            except sr.RequestError as e:
                print('Erro ao solicitar resultados do serviço Google Speech Recognition; {0}'.format(e))
                texto = ''
            return texto

        texto = ''
        for parte in partes_audio:
            texto = texto + ' ' + transcreve_audio(parte)

        planilha = ['Nome do paciente','','@','Data','','@','Horário','','@','Pressão Arterial', '', '@','Frequência Cardíaca', '','@','Saturação', '','@', 'Frequência Respiratória', '','@','Temperatura','°C','@','Diurese','','@','Evacuação','','@','Drenagens','','@','Escala de Dor','','@','Técnico Responsável','']
#                         0             1   2     3   4    5    6        7               8           9          10     11            12                 13      14         15        16   17     18        19     20       21       22          23             24           25   
        indice = 0

        planilha_minuscula = [x.lower() for x in planilha] 
        palavras_que_aparecem = []
        for a in planilha_minuscula: #nome, pressao 
            if texto.lower().__contains__(a):
                palavras_que_aparecem.append(a)
        try:
            while True:
                palavras_que_aparecem.remove('')
        except ValueError:
            pass

        for i in palavras_que_aparecem:
            indice=(texto.index(i) + len(i) - 1) #acha no texto o 1 indice da palavra chave e pega a extensao da palavra pra nao precisar pprocurar
            valor_indice = ([float(s) for s in re.findall(r'-?\d+\.?\d*', texto[indice : len(texto)])]) #ele procura no texto a partir do indice de cima uo primeiro numero
                #procura a palavra chave na planilha, e adiciona 1 no indice que achar
                #ali coloca o valor achado por valor_indice
            indice_planilha = planilha_minuscula.index(i) + 1
            if valor_indice == []:
                planilha[indice_planilha] = 'Não auferido'
            elif i=="pressão arterial":
                planilha[indice_planilha] = str(valor_indice [0]) + ' X ' + str(valor_indice[1])
            else:
                planilha[indice_planilha] = str(valor_indice [0]) + planilha[indice_planilha]

        #pega o indice da primeira letra
        planilha[4] = NovoprontuarioWindow().get_date()
        planilha [7] = NovoprontuarioWindow().get_time()
        planilha[1] = NovoprontuarioWindow().get_paciente()
        planilha [-1] = LoginWindow().get_enfermeiro()
        nome_arquivo = NovoprontuarioWindow().get_paciente() + "-" + NovoprontuarioWindow().get_date()+ "-"+ NovoprontuarioWindow().get_time() +".txt"
    
            
        painel = str(planilha)
        painel = painel.replace(",", "")
        painel = painel.replace("]", "")
        painel = painel.replace("[", "")
        painel = painel.replace("'", "")
        painel = painel.replace("@", "\n")
        

        
        with open (nome_arquivo, "w") as arquivo:
            arquivo.write(str(painel))


if __name__ == "__main__":
    LudApp().run()

