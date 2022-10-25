from kivy.properties import StringProperty
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
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
from kivymd.uix.snackbar import BaseSnackbar
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.button import MDFlatButton
from datetime import datetime
from kivymd.uix.list import IRightBodyTouch, TwoLineListItem
import speech_recognition as sr

from kivy.properties import StringProperty
from kivymd.icon_definitions import md_icons
from kivymd.uix.list import OneLineIconListItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
import json

import pyaudio
import wave
import subprocess
import os
import time
import threading
import re
import kivy
from kivy.utils import platform

from pydub import AudioSegment
from pydub.utils import make_chunks
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from kivy.metrics import dp
from pathlib import Path as caminho
import requests.exceptions


from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty

import datetime

from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import BaseSnackbar

import pyrebase

config = {
  "apiKey": "AIzaSyBBETYq36STMNO_zHccIAS5gOkKd50LYYQ",
  "authDomain": "app-saude-e144d.firebaseapp.com",
  "projectId": "app-saude-e144d",
  "storageBucket": "app-saude-e144d.appspot.com",
  "messagingSenderId": "982100847350",
  "databaseURL": "https://app-saude-e144d-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(config)
tabelaDeEnfermeiros = firebase.database().child("enfermeiros").get()
dados = firebase.database().child("dados").get()
sm = ScreenManager()
idioma = 'pt-BR'
global listaDePacientes

Window.size = (300, 500)

class MainWindow(Screen):
    def configuracoes(self, instance_action_top_appbar_button) :
        self.parent.current = 'cadastro_screen'

class LoginWindow(Screen):
    def set_enfermeiro (self, value):
        global login_enfermeiro
        login_enfermeiro = value

    def on_senha (self, value):
        global senha
        senha = value

    def verifica (self):
        if 'login_enfermeiro' not in globals() or login_enfermeiro=="":
            self.ids.campo_vazio.text = "insira seu usuário"
        elif 'senha' not in globals() or senha=="":
            self.ids.campo_vazio.text = "insira sua senha"
        else:
            comportamento = self.autenticacao(login_enfermeiro, senha)
            if comportamento == None:
                self.ids.campo_vazio.text = "Usuario não encontrado"
            elif comportamento == 'si':
                self.ids.campo_vazio.text = "Senha Incorreta"
            elif comportamento == 'lf':
                self.parent.current = 'main_screen'
                global tipo_dispositivo
                tipo_dispositivo=kivy.platform
                self.ids.campo_vazio.text = ""
                self.ids.password.text =""
            else:
                self.ids.campo_vazio.text = "Sem Conexão"

    def autenticacao (self, login, senha):
        try:
            for enfermeiroDado in tabelaDeEnfermeiros.each():
                if(enfermeiroDado.key() == login):
                    if(enfermeiroDado.val()['senha'] == senha):
                        return 'lf'
                    else:
                        return 'si'
        except:
            return 0


class NovoprontuarioWindow(Screen):
    def on_pre_enter(self):
        log = firebase.database().child("pacientes").shallow().get().val()
        for l in log:
            path = firebase.database().child("pacientes").child(l).get().val()
            for p, v in path.items():
                if p=='nome':
                    self.ids.scroll_paciente.add_widget(
                        ListItem(text=f"{v}", secondary_text=f"{'id:'+l}", id=l))
    def on_pre_leave(self):
        self.ids.scroll_paciente.clear_widgets()


class GravacaoWindow(Screen):
    def ativa_spinner(self):
        self.ids.spinner.active = True
    def desativa_spinner(self):
        self.ids.spinner.active = False

class Historico (Screen):
    def on_pre_enter(self):
        caminhoParaListarOsPacientes= firebase.database().child("dados").child(login_enfermeiro).shallow().get()
        try:
            for dado in dados.each():
                if(dado.key() == login_enfermeiro):
                    listaDePacientes = caminhoParaListarOsPacientes.val()
            for prontuario in listaDePacientes:
                separado = prontuario.split("-", 1)
                self.ids.scroll.add_widget(
                    ListItem(text=f"{separado[0]}", secondary_text=f"{separado[1]}", id=prontuario)
                )
        except:
            pass
    def on_pre_leave(self):
            self.ids.scroll.clear_widgets()

    def recebeProntuarioDoClique (text_item):
        global texto_item
        texto_item = text_item
        sm.current='exibir_prontuarios'


class ListItem(TwoLineListItem):
    on_release=lambda x: Historico.recebeProntuarioDoClique(x.id)


class ExibirProntuario (Screen):
    def on_pre_enter(self):
        try:
            caminho = firebase.database().child("dados").child(login_enfermeiro).child(texto_item).get().val()
            for chave, valor in caminho.items():
                self.ids.text_input.text = self.ids.text_input.text + '\n' + (chave + ' : ' + valor)
        except:
            caminho = firebase.database().child("pacientes").child(texto_item).get().val()
            for chave, valor in caminho.items():
                self.ids.text_input.text = self.ids.text_input.text + '\n' + (chave + ' : ' + str(valor))

    def on_pre_leave(self):
        self.ids.text_input.text = ""

    def voltar(self, instance_action_top_appbar_button):
        self.parent.current = 'historico_screen'

class Cadastro (Screen):
    def home (self, instance_action_top_appbar_button):
        self.parent.current = 'main_screen'

class Adicionando_Enfermeiros (Screen):
    pass

idioma = 'pt-BR'
class SelecioneIdioma(Screen):
    def voltar (self, instance_action_top_appbar_button):
        self.parent.current = 'cadastro_screen'
    def trocarIdioma (self, idioma_sigla):
        global idioma
        idioma = idioma_sigla


class ComoUsar(Screen):
    def voltar (self, instance_action_top_appbar_button):
        self.parent.current = 'cadastro_screen'

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class CustomSnackbar(BaseSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")
    snackbar_animation_dir = "Right"

screen = Builder.load_file("login.kv")

class LudApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

        principal = MainWindow(name='main_screen')
        login = LoginWindow(name='login_screen')
        gravacao = GravacaoWindow(name= 'gravacao_screen')
        historico = Historico(name = 'historico_screen')
        novo = NovoprontuarioWindow(name='novo_screen')
        cadastro = Cadastro(name='cadastro_screen')
        adicionando_enfermeiros = Adicionando_Enfermeiros(name ='add_enfermeiros')
        exibir_prontuario = ExibirProntuario(name='exibir_prontuarios')
        selecione_idioma = SelecioneIdioma(name='selecione_idioma_screen')
        como_usar= ComoUsar(name='como_usar_screen')
        

        sm.add_widget(login)
        sm.add_widget(principal)
        sm.add_widget(gravacao)
        sm.add_widget(historico)
        sm.add_widget(novo)
        sm.add_widget(cadastro)
        sm.add_widget(adicionando_enfermeiros)
        sm.add_widget(exibir_prontuario)
        sm.add_widget(selecione_idioma)
        sm.add_widget(como_usar)
        return sm


    def show(self, texto_re):
        snackbar = CustomSnackbar(
            text= texto_re,
            icon="information",
            snackbar_x="5dp",
            snackbar_y="370dp",
            snackbar_animation_dir = "Right",
        ).open()
        
    def check_internet (self, instance_action_top_appbar_button):
        url = 'https://www.google.com'
        timeout = 5
        try:
            requests.get(url, timeout=timeout)
            LudApp.show(self, "Dispositivo conectado")
        except:
            LudApp.show(self, "Não há conexão com a internet")


    def start_recording (self):
        if tipo_dispositivo=="win":
            self.CHUNK = 1024
            self.FORMAT = pyaudio.paInt16
            self.CHANNELS = 1
            self.RATE = 16000
            self._running = True
            self._frames = []
            threading._start_new_thread(self.__recording, ())
        if tipo_dispositivo=="android":
            audio.file_path = './audio.wav'
            audio._start()
            audio.state = 'recording'
        else:
            pass
        

    def __recording(self):
        self._running = True
        self._frames = []
        p = pyaudio.PyAudio()
        #Open stream
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        while(self._running):
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        if(tipo_dispositivo=='win'):
            self._running = False
        if(tipo_dispositivo=='android'):
            audio._stop()
        else:
            pass

    #Save file to filename location as a wavefront file.
    def save(self, filename):
        p = pyaudio.PyAudio()
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()

    def audio_prep (self, filename):
        audio = AudioSegment.from_file(filename, 'wav')

        # Tamanho em milisegundos
        tamanho = 100000
        # divisão do audio em partes
        partes = make_chunks(audio, tamanho)
        partes_audio=[]
        for i, parte in enumerate(partes):
            parte_name='parte{0}.wav'.format(i)
            partes_audio.append(parte_name)
            parte.export(parte_name, format='wav')


        def transcreve_audio(nome_audio):
            reconhecimento=sr.Recognizer( )

            with sr.AudioFile(nome_audio) as source:
                audio = reconhecimento.record(source)
            try:
                print('Reconhecimento: ' + reconhecimento.recognize_google(audio,language=idioma))
                texto = reconhecimento.recognize_google(audio,language=idioma)
            except sr.UnknownValueError:
                print('Conteúdo do áudio não entendido')
                texto = ''
            except sr.RequestError as e:
                print('Sem conexão')
                texto = ''
            return texto

        texto = ''
        for parte in partes_audio:
            texto = texto + ' ' + transcreve_audio(parte)

        def tratamento_frase (palavraChave):
            indice=(texto.index(palavraChave) + len(palavraChave) - 1)
            valor_indice = ([float(s) for s in re.findall(r'-?\d+\.?\d*', texto[indice : len(texto)])])
            return valor_indice

        def substituicao (palavraChave, listaDeSinonimo):
            for sinonimo in listaDeSinonimo:
                nonlocal texto
                texto = texto.replace(sinonimo, palavraChave)
            return texto.lower()

        def pressaoArterial (palavraChave, listaDeSinonimo):
            if palavraChave in substituicao(palavraChave, listaDeSinonimo):
                valor_indice = tratamento_frase(palavraChave)
                try:
                    return (str(valor_indice[0]) + ' X ' + str(valor_indice[1]))
                except:
                    return None
            else:
                return None

        def processarTexto(palavraChave, listaDeSinonimo):
            if palavraChave in substituicao(palavraChave, listaDeSinonimo):
                valor_indice = tratamento_frase(palavraChave)
                try:
                    return str(valor_indice[0])
                except:
                    return None #falou palavra chave mas não disse valor
            else:
                return None

        #def observacoes (palavraChave, listaDeSinonimo):
        #    substituicao(palavraChave, listaDeSinonimo)


        horario = (datetime.datetime.now())
        dia_formatado = str (horario.day) +' '+ str(horario.month) + ' ' + str(horario.year)
        horario_formatado = str(horario.strftime("%X"))

        def selecionaPartirDoIdNomeEnfermeiro (login):
            for enfermeiroDado in tabelaDeEnfermeiros.each():
                if(enfermeiroDado.key() == login):
                    nomeEnfermeiro = enfermeiroDado.val()['nome']
                    return nomeEnfermeiro

        def get_nome(id_nome):
            try:
                for paciente in firebase.database().child('pacientes').get().each():
                    if(paciente.key() == str(int(float(id_nome)))):
                        resul = (paciente.val()['nome'])
                        return resul
                return 'paciente não encontrado'
            except:
                return 'paciente não encontrado'


        sinonimosDePressao = ['pressão ', 'pa ', 'p.a. ']
        sinonimoDeEscalaDeDor = ['escala.de.dor ', 'escala de sua dor ', 'o quanto dói ']
        sinonimoDeFrequenciaCardiaca = ['batimento ','batimento cardíaco ', 'coração ', 'batida do coração ', 'pulsação ' ]
        sinonimoDeSaturacao = ['oxigênio ']
        sinonimoDeFreqRespiratoria = ['eupneia ', 'respiração ', 'ritmo respiratório ']
        sinonimoDeTemperatura = ['febre ', 'hipertermia ']
        sinonimoDeDiurese = ['xixi ', 'urina ']
        sinonimoDeEvacuacao = ['cocô ', 'excremento', 'excreção']
        sinonimoDeGlicose = ['glicemia ', 'açúcar ']
        sinonimoDeDrenagem = ['dreno ']
        sinonimoDePaciente = ['nome ', 'número ', 'id ']
        sinonimoDeObservações = ['observação ', 'notas ', 'anotações ']

        data = {
            'Paciente': get_nome(processarTexto('paciente ', sinonimoDePaciente)),
            'Data': dia_formatado,
            'Horario': horario_formatado,
            'Pressão Arterial': pressaoArterial('pressão arterial', sinonimosDePressao),
            'Frequência Cardíaca': processarTexto('frequência  cardíaca', sinonimoDeFrequenciaCardiaca),
            'Saturação': processarTexto('saturação', sinonimoDeSaturacao),
            'Frequência Respiratória':  processarTexto('frequência respiratória', sinonimoDeFreqRespiratoria),
            'Temperatura': processarTexto('temperatura', sinonimoDeTemperatura),
            'Diurese': processarTexto('diurese', sinonimoDeDiurese),
            'Glicose': processarTexto('glicose', sinonimoDeGlicose),
            'Evacuação': processarTexto('evacuação', sinonimoDeEvacuacao),
            'Drenagens': processarTexto('drenagens', sinonimoDeDrenagem),
            'Escala de Dor': processarTexto('escala de dor', sinonimoDeEscalaDeDor),
            'Técnico Responsável': selecionaPartirDoIdNomeEnfermeiro(login_enfermeiro)
        }
        firebase.database().child("dados").child(login_enfermeiro).child(data['Paciente']+'-' + data['Data']+ ' às ' + data['Horario']).set(data)

if __name__ == "__main__":
    LudApp().run()
