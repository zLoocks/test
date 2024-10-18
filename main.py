import json
import os
import logging
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

# Definindo cores globais para melhorar o visual do aplicativo
theme_colors = {
    "background": (0.98, 0.98, 0.98, 1),
    "card_background": (0.92, 0.96, 0.98, 1),
    "button_background": (0.0, 0.48, 0.76, 1),
    "button_text": (1, 1, 1, 1),
    "title_text": (0.15, 0.15, 0.15, 1),
    "selected_button": (0.2, 0.8, 0.2, 1),
    "unselected_button": (0.9, 0.9, 0.9, 1),
    "correct_answer": (0.6, 0.8, 0.2, 1),
    "main_text": (0.2, 0.2, 0.2, 1)
}

# Ajustar o tamanho da janela para uma melhor experiência visual
Window.size = (800, 600)

# Lista de temas e os ícones correspondentes, com o nome do arquivo JSON para cada tema
temas = [
    {"nome": "Motoren", "icone": "motor_icon.png", "arquivo_json": "motoren.json"},
    {"nome": "Theorie", "icone": "theory_icon.png", "arquivo_json": "theorie.json"},
    {"nome": "Elektronik", "icone": "elektronik_icon.png", "arquivo_json": "elektronik.json"},
    {"nome": "Schutzmaßnahme", "icone": "schutz_icon.png", "arquivo_json": "schutzmassnahme.json"},
    {"nome": "Maschinen und Elektronik", "icone": "maschinen_icon.png", "arquivo_json": "maschinen.json"}
]

# Função para carregar perguntas de um arquivo JSON
def carregar_perguntas(arquivo_json):
    try:
        caminho_absoluto = os.path.join(os.path.dirname(__file__), arquivo_json)
        with open(caminho_absoluto, 'r', encoding='utf-8') as f:
            perguntas = json.load(f)
        logging.info(f"Arquivo {arquivo_json} carregado com sucesso.")
        return perguntas
    except FileNotFoundError:
        logging.error(f"Arquivo {arquivo_json} não encontrado.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Erro ao decodificar o JSON do arquivo {arquivo_json}.")
        return []

# Classe para gerenciar o quiz
class QuizManager:
    def __init__(self):
        self.perguntas = []
        self.indice_pergunta_atual = 0
        self.pontuacao = 0
        self.respostas_selecionadas = []

    def carregar_perguntas(self, arquivo_json):
        # Carregar todas as perguntas do JSON e embaralhar
        self.perguntas = carregar_perguntas(arquivo_json)
        random.shuffle(self.perguntas)
        self.indice_pergunta_atual = 0
        self.pontuacao = 0
        self.respostas_selecionadas = []

    def obter_pergunta_atual(self):
        if self.indice_pergunta_atual < len(self.perguntas):
            return self.perguntas[self.indice_pergunta_atual]
        return None

    def verificar_resposta(self):
        pergunta_atual = self.obter_pergunta_atual()
        if pergunta_atual:
            respostas_corretas = pergunta_atual.get('resposta_correta', [])
            if isinstance(respostas_corretas, list):
                respostas_corretas = [str(resp).lower().strip() for resp in respostas_corretas]
            else:
                respostas_corretas = [str(respostas_corretas).lower().strip()]
            respostas_selecionadas = [str(resp).lower().strip() for resp in self.respostas_selecionadas]
            if set(respostas_selecionadas) == set(respostas_corretas):
                self.pontuacao += 1
                return True
        return False

    def selecionar_resposta(self, resposta):
        if resposta not in self.respostas_selecionadas:
            self.respostas_selecionadas.append(resposta)
        else:
            self.respostas_selecionadas.remove(resposta)

    def limpar_respostas_selecionadas(self):
        self.respostas_selecionadas = []

    def proxima_pergunta(self):
        if self.indice_pergunta_atual < len(self.perguntas) - 1:
            self.indice_pergunta_atual += 1
            self.limpar_respostas_selecionadas()
            return True
        return False

    def obter_pontuacao(self):
        return self.pontuacao

    def obter_porcentagem_acertos(self):
        if len(self.perguntas) == 0:
            return 0
        return (self.pontuacao / len(self.perguntas)) * 100

# Widget para definir o fundo branco
class WhiteBackground(BoxLayout):
    def __init__(self, **kwargs):
        super(WhiteBackground, self).__init__(**kwargs)
        with self.canvas.before:
            Color(*theme_colors['background'])  # Cor de fundo
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[20])
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

# Tela de seleção de temas
class MenuTemasScreen(Screen):
    def __init__(self, quiz_manager, **kwargs):
        super().__init__(**kwargs)
        self.quiz_manager = quiz_manager
        layout = WhiteBackground(orientation='vertical', padding=20, spacing=15)

        title_label = Label(text="Wählen Sie ein Thema", font_size='28sp', size_hint=(1, None), height=60, color=theme_colors['title_text'], bold=True)
        layout.add_widget(title_label)

        temas_layout = GridLayout(cols=2, spacing=15, size_hint_y=None, padding=10)
        temas_layout.bind(minimum_height=temas_layout.setter('height'))

        for tema in temas:
            tema_card = self.criar_cartao_tema(tema)
            temas_layout.add_widget(tema_card)

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(temas_layout)
        layout.add_widget(scroll_view)

        self.add_widget(layout)

    def criar_cartao_tema(self, tema):
        tema_card = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(None, None), size=(160, 180))
        with tema_card.canvas.before:
            Color(*theme_colors['card_background'])  # Cor de fundo dos cartões
            tema_card.rect = RoundedRectangle(size=tema_card.size, pos=tema_card.pos, radius=[15])
            tema_card.bind(size=self._update_card_rect, pos=self._update_card_rect)

        icone = Image(source=tema["icone"], size_hint=(1, 0.6))
        tema_card.add_widget(icone)

        btn = Button(
            text=tema["nome"],
            font_size='14sp',
            color=theme_colors['button_text'],
            background_normal='',
            background_color=theme_colors['button_background'],
            size_hint=(1, 0.4)
        )
        btn.bind(on_press=lambda instance: self.on_select_tema(tema))  # Vincular ao tema específico
        tema_card.add_widget(btn)

        return tema_card

    def _update_card_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def on_select_tema(self, tema):
        # Quando o botão do tema é clicado, carrega o JSON correspondente e troca de tela
        self.quiz_manager.carregar_perguntas(tema["arquivo_json"])  # Carregar as perguntas do JSON associado
        quiz_screen = self.manager.get_screen('quiz')
        self.manager.current = 'quiz'
        quiz_screen.mostrar_pergunta()

# Tela de perguntas
class QuizScreen(Screen):
    def __init__(self, quiz_manager, **kwargs):
        super().__init__(**kwargs)
        self.quiz_manager = quiz_manager
        self.layout = WhiteBackground(orientation='vertical', padding=20, spacing=10)

        self.question_label = Label(text="Pergunta aparecerá aqui", font_size='22sp', size_hint=(1, None), height=100, color=theme_colors['title_text'], bold=True, halign='center', valign='middle')
        self.question_label.bind(size=self.question_label.setter('text_size'))
        self.layout.add_widget(self.question_label)

        self.buttons_layout = BoxLayout(orientation='vertical', spacing=12, padding=(20, 10))
        self.layout.add_widget(self.buttons_layout)

        self.help_button = Button(text="Ajuda", font_size='16sp', size_hint=(0.5, None), height=50, pos_hint={'center_x': 0.5}, background_color=(0.9, 0.6, 0.2, 1), color=theme_colors['button_text'])
        self.help_button.bind(on_press=self.on_ajuda)
        self.layout.add_widget(self.help_button)

        self.next_button = Button(text="Próxima Pergunta", font_size='16sp', size_hint=(0.5, None), height=50, pos_hint={'center_x': 0.5}, background_color=theme_colors['button_background'], color=theme_colors['button_text'])
        self.next_button.bind(on_press=self.on_proxima_pergunta)
        self.layout.add_widget(self.next_button)
        self.next_button.disabled = True

        self.back_button = Button(text="Zurück zum Hauptmenü", font_size='16sp', size_hint=(0.5, None), height=50, pos_hint={'center_x': 0.5}, background_color=(0.5, 0.5, 0.5, 1), color=theme_colors['button_text'])
        self.back_button.bind(on_press=self.on_back_to_menu)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def mostrar_pergunta(self):
        pergunta = self.quiz_manager.obter_pergunta_atual()
        if pergunta:
            self.question_label.text = pergunta['pergunta']
            self.buttons_layout.clear_widgets()
            self.next_button.disabled = True
            opcoes = pergunta['opcoes'][:]
            random.shuffle(opcoes)  # Embaralhar as opções
            for opcao in opcoes:
                btn = Button(text=opcao, font_size='14sp', background_normal='', background_color=theme_colors['unselected_button'], color=theme_colors['main_text'], size_hint_y=None, height=45)
                btn.bind(on_press=self.on_selecionar_resposta)
                self.buttons_layout.add_widget(btn)
        else:
            self.finalizar_quiz()

    def finalizar_quiz(self):
        self.buttons_layout.clear_widgets()
        self.next_button.disabled = True
        porcentagem_acertos = self.quiz_manager.obter_porcentagem_acertos()
        if porcentagem_acertos >= 80:
            self.question_label.text = f"Quiz finalizado! Pontuação: {self.quiz_manager.obter_pontuacao()} ({porcentagem_acertos:.2f}%)\nHerzlichen Glückwunsch! Sie haben großartig abgeschnitten!"
            self.mostrar_icone_final("congratulations_icon.png")
        else:
            self.question_label.text = f"Quiz finalizado! Pontuação: {self.quiz_manager.obter_pontuacao()} ({porcentagem_acertos:.2f}%)\nBitte versuchen Sie es weiter! Sie schaffen das!"
            self.mostrar_icone_final("try_again_icon.png")
        # Resetar o quiz ao final
        self.quiz_manager.indice_pergunta_atual = 0
        self.quiz_manager.pontuacao = 0
        self.quiz_manager.limpar_respostas_selecionadas()

    def mostrar_icone_final(self, icone_path):
        # Remover qualquer ícone anterior antes de adicionar um novo
        for widget in self.layout.children[:]:
            if isinstance(widget, Image) and widget.source in ["congratulations_icon.png", "try_again_icon.png"]:
                self.layout.remove_widget(widget)
        icone = Image(source=icone_path, size_hint=(0.4, 0.4), pos_hint={'center_x': 0.5})
        self.layout.add_widget(icone)
        self.icone_atual = icone
        self.bind(on_leave=self.remover_icone_final)

    def remover_icone_final(self, *args):
        if hasattr(self, 'icone_atual') and self.icone_atual in self.layout.children:
            self.layout.remove_widget(self.icone_atual)

    def on_selecionar_resposta(self, instance):
        resposta = instance.text
        self.quiz_manager.selecionar_resposta(resposta)
        if resposta in self.quiz_manager.respostas_selecionadas:
            instance.background_color = theme_colors['selected_button']  # Marcar como selecionado
        else:
            instance.background_color = theme_colors['unselected_button']  # Voltar à cor original
        pergunta_atual = self.quiz_manager.obter_pergunta_atual()
        respostas_corretas = pergunta_atual.get('resposta_correta', [])
        respostas_corretas = [str(resp).lower().strip() for resp in respostas_corretas] if isinstance(respostas_corretas, list) else [str(respostas_corretas).lower().strip()]
        respostas_selecionadas = [str(resp).lower().strip() for resp in self.quiz_manager.respostas_selecionadas]
        if set(respostas_selecionadas) == set(respostas_corretas):
            self.next_button.disabled = False

    def on_proxima_pergunta(self, instance):
        # Avançar para a próxima pergunta imediatamente após usar a ajuda
        if self.next_button.disabled is False:
            if self.quiz_manager.proxima_pergunta():
                self.mostrar_pergunta()
            else:
                self.finalizar_quiz()
        elif self.quiz_manager.verificar_resposta() or not self.quiz_manager.obter_pergunta_atual().get('resposta_correta', []):
            if self.quiz_manager.proxima_pergunta():
                self.mostrar_pergunta()
            else:
                self.finalizar_quiz()

    def on_back_to_menu(self, instance):
        self.manager.current = 'menu'

    def on_ajuda(self, instance):
        pergunta_atual = self.quiz_manager.obter_pergunta_atual()
        if pergunta_atual:
            respostas_corretas = pergunta_atual.get('resposta_correta', [])
            respostas_corretas = [str(resp).lower().strip() for resp in respostas_corretas] if isinstance(respostas_corretas, list) else [str(respostas_corretas).lower().strip()]
            for btn in self.buttons_layout.children:
                if btn.text.lower().strip() in respostas_corretas:
                    btn.background_color = theme_colors['correct_answer']  # Marcar como resposta correta
            self.next_button.disabled = False  # Habilitar o botão "Próxima Pergunta" após usar a ajuda

# Aplicativo principal
class QuizApp(App):
    def build(self):
        quiz_manager = QuizManager()

        sm = ScreenManager()
        sm.add_widget(MenuTemasScreen(name='menu', quiz_manager=quiz_manager))
        sm.add_widget(QuizScreen(name='quiz', quiz_manager=quiz_manager))

        return sm

if __name__ == '__main__':
    QuizApp().run()
