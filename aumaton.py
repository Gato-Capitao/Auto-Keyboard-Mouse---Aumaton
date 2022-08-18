"""Aumaton"""

"""
Automatiza funções do computador, como clicar ou apertar alguma tecla,
se pode fazer essas ações em uma ordem determinada, 
que pode ser usada para fazer certas tarefas repetidamente.

Funções:
    mouse: Clica em um lugar determinado na tela.
    teclado: Aperta uma tecla ou combinação
    clock: Espera um tempo definido.
"""

#Bibliotecas
import PySimpleGUI as sg
from threading import Thread
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode
import keyboard as kb
from datetime import datetime as dt
from time import sleep
import os
from pickle import dump, load
import requests

#Variavies
passos = []
teclas = [#Lista de teclas disponiveis
    '0', '1', '2', '3', '4', '5', '6', '7','8', '9','a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o','p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'alt','backspace', 'ctrl', 'ctrlleft', 'ctrlright', 'down', 'enter', 'esc', 'f1', 'f2', "f3", "f4", 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12','left', 'numlock', 'page down', 'page up', 'right', 'shift', 'shiftleft', 'shiftright', 'space', 'subtract', 'tab','up', 'win']

mouse = Controller()#Controlador, objeto usado para executar e mudar os valores do mouse.

mouseValores = {"acao":"mouse", "modo":"marcada", "x":200, "y":200, "botao":Button.left}
clockValores = {"acao":"clock", "modo":"aguarde", "tempo":5, "hora":19, "minuto":25}
tecladoValores = {"acao":"teclado", "teclas":"", "combinacao":False}
salvarValores= {"modo":"novo", "nome":None}

#design
dark = {'BACKGROUND': '#121316',
                'TEXT': '#a8adb9',
                'INPUT': '#0b3967',
                'TEXT_INPUT': '#a5c1dd',
                'SCROLL': '#c7e78b',
                'BUTTON': ('white', '#0b3967'),
                'PROGRESS': ('#01826B', '#D0D0D0'),
                'BORDER': 1,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}
sg.theme_add_new("Dark", dark)
sg.theme("Dark")

def layoutPrincipal():
    """Retorna a janela principal
    
    Variaveis:
        list - f_cordenadas/f_aguarde/f_espere: Frames que ficam dentro dos tabs
        list - tab_mouse/tab_teclado/tab_clock/tab_passos/tab_salvar: Tabs que ficam dentro do layout principal, e representam cada tipo de ações
    """
    f_cordenadas = [
    [sg.Text("x="), sg.Text(text="200", key="lcomplexo_mcx"), sg.Text("y="), sg.Text(text="200", key="lcomplexo_mcy"), sg.Button("Marcar", key="lcomplexo_mmarcar")]]
    f_aguarde = [
        [sg.Input(key="lcomplexo_ciaguarde", size=(10,1)), sg.Text("segundos")]
    ]
    f_espere = [
        [sg.Input(default_text="19:25",size=(10,1), key="lcomplexo_ciespere")]
    ]
    
    tab_mouse = [
        [sg.Text("Botao")],
        [sg.Radio("esquerdo", key="lcomplexo_mesquerdo", group_id="lcomplexo_mbotao", enable_events=True, default=True), sg.Radio("direito",  key="lcomplexo_mdireito", group_id="lcomplexo_mbotao", enable_events=True)],
        [sg.Text("Posiçao")],
        [sg.Radio("Posiçao do mouse", key="lcomplexo_mmouse", group_id="lcomplexo_mposicao", enable_events=True), sg.Radio("Decidir posiçao", key="lcomplexo_mdecidir", group_id="lcomplexo_mposicao", default=True, enable_events=True)],
        [sg.Frame("Cordenadas", f_cordenadas, visible=True, key="lcomplexo_mfcordenadas")],
        [sg.VPush()],
        [sg.Button("Adicionar",key="lcomplexo_madicionar")]]
    tab_teclado = [
        [sg.Text("Tecla")],
        [sg.Combo(teclas, default_value=teclas[0], key="lcomplexo_tcomboteclas"), sg.Button("Adicionar tecla", key="lcomplexo_tadicionart")],
        [sg.Text("Teclas:"), sg.Text("", key="lcomplexo_tcombinacao")], 
        [sg.Button("Limpar", key="lcomplexo_tlimpart")],
        
        [sg.VPush()],
        [sg.Button("Adicionar", key="lcomplexo_tadicionar")]]
    tab_clock = [
        [sg.Radio("Aguarde", key="lcomplexo_caguarde", group_id="lcomplexo_cfuncao", default=True, enable_events=True), sg.Radio("Espere", key="lcomplexo_cespere", group_id="lcomplexo_cfuncao", enable_events=True)],
        [sg.Frame("Aguarde", f_aguarde, key="lcomplexo_cfaguarde")],
        [sg.Frame("Espere", f_espere, visible=False, key="lcomplexo_cfespere")],
        [sg.VPush()],
        [sg.Button("Adicionar", key="lcomplexo_cadicionar")]]
    tab_passos = [
        [sg.Output(size=(35, 10), key="lcomplexo_poutput")],
        [sg.Button("Recarregar", key="lcomplexo_precarregar"), sg.Button("Resetar", key="lcomplexo_presetar")]
    ]
    tab_salvar = [
        [sg.Radio("Arquivo existente", key="lcomplexo_sexistente", group_id="lcomplexo_smodo", enable_events=True), sg.Radio("Novo", key="lcomplexo_snovo", group_id="lcomplexo_smodo", default=True, enable_events=True)],
        [sg.Text("Nome", key="lcomplexo_snometexto", visible=True)], 
        [sg.Input(key="lcomplexo_snome", visible=True, size=(30, 1))],
        [sg.VPush()],
        
        [sg.Combo(arquivos, visible=False, key="lcomplexo_sarquivos", size=(30, 1))],
        
        [sg.Button("Salvar", key="lcomplexo_ssalvar"), sg.Button("Carregar", key="lcomplexo_scarregar", visible=False)],]
    
    layout = [
        [sg.TabGroup([[sg.Tab("Mouse", layout=tab_mouse), sg.Tab("Teclado", layout=tab_teclado), sg.Tab("Relógio", layout=tab_clock), sg.Tab("Salvar", layout=tab_salvar), sg.Tab("Etapas", layout=tab_passos)]])],
        [sg.Text("P = Pausar/Despausar", key="lcomplexo_aviso", visible=True, text_color="green")],
        [sg.Text("O programa está rodando", key="lcomplexo_rodandoaviso", visible=False, text_color="green")],
        [sg.Button("Começar", key="lcomplexo_comecar"), sg.Button("Parar", key="lcomplexo_parar", button_color="red"), sg.Push()]]
    
    return sg.Window("Aumaton", layout=layout, finalize=True, grab_anywhere=True, resizable=True, margins=(25,25), icon="data/icon/cubo.ico")

def layoutErro():
    """Retorna a janela de erro"""
    layout = [
        [sg.VPush()],
        [sg.Text("Erro")],
        [sg.VPush()],
        
        [sg.Text("Preencha corretamente")],
        [sg.VPush()],
        
        [sg.Button("x", key="lerro_fechar", button_color="red", font="Courier", size=(2,1))],
        [sg.VPush()]]

    return sg.Window("ERRO", layout=layout, grab_anywhere=True, finalize=True, margins=(25,25), element_justification="center", no_titlebar=True, icon="data/icon/cubo.ico")

#Objeto do Complexo
class ComplexoT(Thread):
    """Objeto complexo"""
    
    def __init__(self):
        self.passos = []
        self.ativo = False
        self.executando = False
    def desativar(self):
        self.executando = False
        self.ativo = False
    def ativar(self):
        self.executando = False
        self.ativo = True
    def interruptor(self):
        """Pausa e despausa a função principal
        """
        if self.executando:
            self.executando = False
        else:
            self.executando = True
    def correr(self):
        """
        Função principal
        
        Variaveis:
            bool - self.executando: Pausa e despausa o laço de repetição
            bool - self.ativo: Quando for Falso a função terminará
        """
        while(self.ativo):
            for passo in self.passos:
                while not self.executando:
                    if not self.ativo:
                        break
                    sleep(0.5)
                if passo["acao"] == "teclado":
                    kb.press_and_release(passo["teclas"])
                elif passo["acao"] == "mouse":
                    if passo["modo"] == "marcada":
                        mouse.position = (passo["x"], passo["y"])
                        mouse.click(passo["botao"])
                    else:
                        mouse.click(passo["botao"])
                elif passo["acao"] == "clock":
                    if passo["modo"] == "aguarde":
                        sleep(passo["tempo"])
                    else:
                        while True:
                            if passo["hora"] == dt.now().hour and passo["minuto"] == dt.now().minute or not self.ativo:
                                break
                            sleep(1)
complexoPrograma = ComplexoT()

#Fucoes
def definirPosicao():
    """Define as posições do mouse"""
    sleep(5)
    mouseValores["x"], mouseValores["y"]= mouse.position
    janela["lcomplexo_mcx"].update(str(mouseValores["x"]))
    janela["lcomplexo_mcy"].update(str(mouseValores["y"]))
def mostrarPassos():
    """Mostra os passos na tab_salvar"""
    for passo in passos:
        if passo["acao"] == "mouse":
            if passo["modo"] == "mouse":
                print("Clique")
            else:
                print("Clique em {}, {}".format(passo["x"], passo["y"]))
        elif passo["acao"] == "teclado":
            print("Pressione e solte {}".format(passo["teclas"]))
        else:
            if passo["modo"] == "aguarde":
                print("Aguarde {} segundos".format(passo["tempo"]))
            else:
                print("Espere até {}:{}".format(passo["hora"], passo["minuto"]))
def salvarPassos(nome):
    """Salva os passos em um arquivo"""
    endereco = os.getcwd()
    with open("data\saves\{}".format(nome), "wb") as arquivo:
        dump(passos, arquivo)
def carregarPassos(nome):
    """Carrega os passos de um arquivo em binario para a variavel passos"""
    with open("data\saves\{}".format(nome), "rb") as arquivo:
        return load(arquivo)
def criarPastas():
    """Verifica se os arquivos devidos estão presentes
    
    Arquivos:
        pasta - data: Guarda todas as outras pastas do programa
        pasta - icon: Guarda o icone do programa
        pasta - saves: Gaurda os saves de passos do programa
        arquivo - cubo.ico: Icone do programa, caso não exista será baixado
    """
    endereco = os.getcwd()
    if not "data" in os.listdir(endereco):
        os.mkdir(endereco+"\data")
    if not "saves" in os.listdir(endereco+"\data"):
        os.mkdir(endereco+"\data\saves")
    if not "icon" in os.listdir(endereco+"\data"):
        os.mkdir(endereco+"\data\icon")
        with open("data\icon\cubo.ico", "wb") as arquivo:
            pag = requests.get("https://filedropper.com/d/s/download/ULx6JQMTiSVrySx9lIffjSS8WcY0ph")
            arquivo.write(pag.content)


def listenerFuncao():#Observer do teclado
    """
    Observa o teclado, quando a tecla pressionada for a tecla botaoLeitor executará a função teclapressionada
    
    Variaveis:
        str - botaoLeitor: Tecla que precisa ser pressioanada para entrar na condicional
        bool - complexoPrograma.ativo: Controla se o programa está ativo, quando dadá como False desativa o programa
    """
    botaoLeitor = KeyCode(char="p")
    
    def teclapressionada():
        complexoPrograma.interruptor()
        
    def pressionado(tecla):
        if tecla == botaoLeitor:
            teclapressionada()
            sleep(1)

    with Listener(on_press=pressionado) as leitor:
        leitor.join()

criarPastas()
arquivos = [arquivos for arquivos in os.listdir(os.getcwd()+"\data\saves")]#Cria lista de arquivos da pasta save

tecladoObserver = Thread(target=listenerFuncao, daemon=True)#Cria uma Thread que observa o teclado.

jcomplexo, jErro = layoutPrincipal(), []
tecladoObserver.start()

#processo
while True:
    #Observa os eventos que acontecem na GUI
    janela, evento, valor = sg.read_all_windows()
    if janela == jErro:
        #Esconde a janela erro se clicar em fechar.
        jErro.hide()
    
    elif evento == sg.WINDOW_CLOSED:
        #Caso clique em fechar na janela principal, quebra o laço de repetição
        break
    

#complexo
    else:
        match evento:
            case "lcomplexo_mmouse" | "lcomplexo_mdecidir":
                #Salva as mudanças feitas no Radio da tab mouse, que decide de que modo será clicado
                if evento == "lcomplexo_mmouse":
                    janela["lcomplexo_mfcordenadas"].update(visible=False)
                    mouseValores["modo"] = "mouse"
                else:
                    janela["lcomplexo_mfcordenadas"].update(visible=True)
                    mouseValores["modo"] = "marcada"
            case "lcomplexo_mmarcar":
                #Executa a função difinirPosicao em uma Thread
                marcarPosicao = Thread(target=definirPosicao)
                marcarPosicao.start()
            case "lcomplexo_mesquerdo" | "lcomplexo_mdireito":
                #Decide qual botão será apertado
                if evento=="lcomplexo_mesquerdo":
                    mouseValores["botao"] = Button.left
                else:
                    mouseValores["botao"] = Button.right
            case "lcomplexo_madicionar":
                #Adiciona o dicionario em passos
                try:
                    passos.append(mouseValores)
                except:
                    jErro = layoutErro()
            
            case "lcomplexo_caguarde" | "lcomplexo_cespere":
                #Muda os valores do dicionaio de acordo com o Radio.
                if evento == "lcomplexo_caguarde":
                    clockValores["modo"] = "aguarde"
                    janela["lcomplexo_cfespere"].update(visible=False)
                    janela["lcomplexo_cfaguarde"].update(visible=True)
                else:
                    clockValores["modo"] = "espere"
                    janela["lcomplexo_cfaguarde"].update(visible=False)
                    janela["lcomplexo_cfespere"].update(visible=True)
            case "lcomplexo_cadicionar":
                #Adiciona o dicionario clock na lista passos
                try:
                    if clockValores["modo"] == "aguarde":
                        clockValores["tempo"] = float(valor["lcomplexo_ciaguarde"])
                        passos.append({"acao":clockValores["acao"], "modo":clockValores["modo"], "tempo":clockValores["tempo"]})
                    elif len(str(valor["lcomplexo_ciespere"])) == 5:
                        clockValores["tempo"] = str(valor["lcomplexo_ciespere"]).replace(":", "")
                        tente = float(clockValores["tempo"])
                        passos.append({"acao":clockValores["acao"], "modo":clockValores["modo"], "hora":int(valor["lcomplexo_ciespere"].split(":")[0]), "minuto":int(valor["lcomplexo_ciespere"].split(":")[1])})
                except:
                    jErro = layoutErro()
            
            case "lcomplexo_tadicionart":
                #Adiciona tecla nas combinações
                if valor["lcomplexo_tcomboteclas"] in teclas and len(tecladoValores["teclas"]) < 20:
                    if not tecladoValores["combinacao"]:
                        tecladoValores["teclas"] = str(valor["lcomplexo_tcomboteclas"])
                        janela["lcomplexo_tcombinacao"].update(tecladoValores["teclas"])
                        tecladoValores["combinacao"] = True
                    else:
                        tecladoValores["teclas"] += " + "+valor["lcomplexo_tcomboteclas"]
                        janela["lcomplexo_tcombinacao"].update(tecladoValores["teclas"])
            case "lcomplexo_tlimpart":
                #Limpa as conbinações
                tecladoValores["teclas"] = ""
                tecladoValores["combinacao"] = False
                janela["lcomplexo_tcombinacao"].update(tecladoValores["teclas"])
            case "lcomplexo_tadicionar":
                #Adiciona o dicionario do teclado em uma lista
                passos.append({"acao":tecladoValores["acao"], "teclas":tecladoValores["teclas"]})
            
            case "lcomplexo_sexistente" | "lcomplexo_snovo":
                #Decide o modo em que o arquivo será salvo
                if evento == "lcomplexo_sexistente":
                    janela["lcomplexo_snometexto"].update(visible=False)
                    janela["lcomplexo_snome"].update(visible=False)
                    janela["lcomplexo_sarquivos"].update(visible=True)
                    janela["lcomplexo_scarregar"].update(visible=True)
                    salvarValores["modo"] = "existente"
                else:
                    janela["lcomplexo_sarquivos"].update(visible=False)
                    janela["lcomplexo_scarregar"].update(visible=False)
                    janela["lcomplexo_snometexto"].update(visible=True)
                    janela["lcomplexo_snome"].update(visible=True)
                    salvarValores["modo"] = "novo"
            case "lcomplexo_ssalvar":
                #Salva a lista passos em um arquivo
                try:
                    if salvarValores["modo"] == "existente":
                        salvarValores["nome"]= valor["lcomplexo_sarquivos"]
                    else:
                        salvarValores["nome"] = valor["lcomplexo_snome"]
                        
                    salvarPassos(salvarValores["nome"])
                except:
                    pass
            case "lcomplexo_scarregar":
                #Carrega o arquivo para a variavel passos
                try:
                    passos = carregarPassos(valor["lcomplexo_sarquivos"])
                except:
                    jErro = layoutErro()
            
            case "lcomplexo_precarregar":
                #Recarrega os valores do output na tab salvar
                janela["lcomplexo_poutput"].update("")
                mostrarPassos()
            case "lcomplexo_presetar":
                #Limpa a variavel passos
                passos = []
                janela["lcomplexo_poutput"].update("")

            case "lcomplexo_comecar":
                """
                Começa a executar a função principal do programa em uma Thread
                """
                if not complexoPrograma.ativo:
                    complexoPrograma.passos = passos
                    complexoPrograma.ativar()
                
                    complexo_processamento = Thread(target=complexoPrograma.correr, daemon=True)
                    complexo_processamento.start()
                    janela["lcomplexo_rodandoaviso"].update(visible=True)
    
            case _:
                """Caso o botão Para na GUI seja pressionado, o programa parará"""
                if complexoPrograma.ativo:
                    janela["lcomplexo_rodandoaviso"].update(visible=False)
                    complexoPrograma.desativar()
