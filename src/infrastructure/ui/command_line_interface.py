"""
Implementation of the command-line interface.
"""
import os
import sys
import logging
from typing import List, Dict, Any, Optional, Callable

from src.entities.question import Question
from src.interfaces.ui.cli_interface import CLIInterface
from src.http.controllers.main_controller import MainController


# Configure logger
logger = logging.getLogger(__name__)


class CommandLineInterface(CLIInterface):
    """
    Implementation of the command-line interface.
    
    This class handles:
    - User interaction via the command line
    - Command parsing and routing
    - Displaying formatted text and questions
    - Handling user input
    """
    
    def __init__(self, controller: MainController):
        """
        Initialize the command-line interface.
        
        Args:
            controller: The main controller to handle commands
        """
        self.controller = controller
        self.running = False
        self.commands = {
            "ajuda": self._handle_help,
            "pergunta": self._handle_question,
            "explique": self._handle_explanation,
            "gerar-prova": self._handle_generate_exam,
            "mostrar-topicos": self._handle_show_topics,
            "limpar": self._handle_clear_history,
            "sair": self._handle_exit
        }
        
    def display_welcome_message(self) -> None:
        """Display a welcome message to the user."""
        self.clear_screen()
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                  FLIPFLOPS - Assistente FUVEST                ║
╚══════════════════════════════════════════════════════════════╝

Bem-vindo ao FLIPFLOPS, seu assistente educacional para o vestibular!

Comandos disponíveis:
  - pergunta [sua pergunta]       Faça uma pergunta de conhecimento geral
  - explique [conceito]           Peça uma explicação socrática de um conceito
  - gerar-prova [tópico] [número] Gere uma prova com perguntas de múltipla escolha
  - mostrar-topicos               Mostrar tópicos disponíveis para provas
  - limpar                        Limpar histórico de conversas
  - ajuda                         Mostrar esta mensagem de ajuda
  - sair                          Sair do programa

Digite um comando para começar!
"""
        print(welcome_text)
        logger.info("Welcome message displayed")
    
    def display_help(self) -> None:
        """Display help information showing available commands."""
        help_text = """
Comandos disponíveis:

  pergunta [sua pergunta]
      Faça uma pergunta de conhecimento geral e receba uma resposta
      Exemplo: pergunta Quem foi Santos Dumont?

  explique [conceito]
      Peça uma explicação socrática de um conceito
      Exemplo: explique Fotossíntese

  gerar-prova [tópico] [número]
      Gere uma prova com perguntas de múltipla escolha sobre um tópico
      Exemplo: gerar-prova "Literatura Brasileira" 5

  mostrar-topicos
      Mostrar tópicos disponíveis para geração de provas

  limpar
      Limpar histórico de conversas

  ajuda
      Mostrar esta mensagem de ajuda

  sair
      Sair do programa
"""
        print(help_text)
        logger.info("Help information displayed")
    
    def display_text(self, text: str) -> None:
        """
        Display text to the user.
        
        Args:
            text: The text to display
        """
        print(f"\n{text}\n")
    
    def display_error(self, message: str) -> None:
        """
        Display an error message to the user.
        
        Args:
            message: The error message to display
        """
        print(f"\n❌ Erro: {message}\n")
        logger.error(f"Error displayed to user: {message}")
    
    def display_success(self, message: str) -> None:
        """
        Display a success message to the user.
        
        Args:
            message: The success message to display
        """
        print(f"\n✅ {message}\n")
    
    def display_question(self, question_text: str, options: List[str]) -> None:
        """
        Display a multiple-choice question with options.
        
        Args:
            question_text: The question text
            options: The list of options (a through e)
        """
        print(f"\n{question_text}\n")
        
        option_letters = ['a', 'b', 'c', 'd', 'e']
        for letter, option in zip(option_letters, options):
            print(f"({letter}) {option}")
        print()
    
    def display_exam_results(self, score: float, total_questions: int) -> None:
        """
        Display exam results to the user.
        
        Args:
            score: The score as a percentage (0.0 to 1.0)
            total_questions: The total number of questions
        """
        correct_questions = int(score * total_questions)
        percentage = score * 100
        
        result_text = f"""
╔══════════════════════════════════════════════════╗
║                 RESULTADO DA PROVA               ║
╠══════════════════════════════════════════════════╣
║  Questões corretas: {correct_questions}/{total_questions}
║  Porcentagem de acerto: {percentage:.1f}%
╚══════════════════════════════════════════════════╝
"""
        
        if percentage >= 80:
            result_text += "\n🎉 Excelente! Você está muito bem preparado!"
        elif percentage >= 60:
            result_text += "\n👍 Bom trabalho! Continue estudando."
        elif percentage >= 40:
            result_text += "\n📚 Você está no caminho certo, mas precisa estudar mais."
        else:
            result_text += "\n📝 Dedique mais tempo aos estudos para melhorar seu desempenho."
            
        print(result_text)
    
    def display_topics(self, topics: List[str]) -> None:
        """
        Display a list of available topics.
        
        Args:
            topics: The list of available topics
        """
        if not topics:
            print("\nNenhum tópico disponível no momento.\n")
            return
            
        print("\nTópicos disponíveis para geração de provas:\n")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
        print()
    
    def get_input(self, prompt: str = "> ") -> str:
        """
        Get input from the user.
        
        Args:
            prompt: The prompt to display
            
        Returns:
            The user's input as a string
        """
        try:
            return input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada pelo usuário.")
            return ""
    
    def get_multiple_choice_answer(
        self, num_options: int = 5, prompt: str = "Sua resposta (a-e): "
    ) -> str:
        """
        Get a multiple-choice answer from the user.
        
        Args:
            num_options: The number of options (defaults to 5)
            prompt: The prompt to display
            
        Returns:
            The selected option letter (a-e)
        """
        valid_options = 'abcde'[:num_options]
        
        while True:
            answer = self.get_input(prompt).lower()
            
            if not answer:
                continue
                
            if answer[0] in valid_options:
                return answer[0]
                
            self.display_error(
                f"Resposta inválida. Por favor, escolha uma das opções: {', '.join(valid_options)}"
            )
    
    def get_yes_no_input(self, prompt: str = "Confirma? (s/n): ") -> bool:
        """
        Get a yes/no input from the user.
        
        Args:
            prompt: The prompt to display
            
        Returns:
            True if the user answered yes, False otherwise
        """
        while True:
            answer = self.get_input(prompt).lower()
            
            if answer in ["s", "sim", "y", "yes"]:
                return True
                
            if answer in ["n", "não", "nao", "no"]:
                return False
                
            self.display_error("Resposta inválida. Por favor, responda com 's' ou 'n'.")
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def start(self) -> None:
        """Start the CLI interface main loop."""
        self.running = True
        self.display_welcome_message()
        
        while self.running:
            try:
                command = self.get_input("\nFlipflops> ")
                self._process_command(command)
            except Exception as e:
                logger.exception("Error in CLI main loop", exc_info=e)
                self.display_error(f"Ocorreu um erro inesperado: {str(e)}")
    
    def exit(self) -> None:
        """Exit the CLI interface."""
        self.running = False
        print("\nObrigado por usar o Flipflops! Até a próxima!\n")
    
    def _process_command(self, command_line: str) -> None:
        """
        Process a command line input.
        
        Args:
            command_line: The command line to process
        """
        if not command_line.strip():
            return
            
        parts = command_line.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command in self.commands:
            self.commands[command](args)
        else:
            self.display_error(
                f"Comando '{command}' não reconhecido. Digite 'ajuda' para ver os comandos disponíveis."
            )
    
    def _handle_help(self, args: str) -> None:
        """
        Handle the 'help' command.
        
        Args:
            args: Command arguments (unused)
        """
        self.display_help()
    
    def _handle_question(self, question: str) -> None:
        """
        Handle the 'question' command.
        
        Args:
            question: The question to answer
        """
        if not question.strip():
            self.display_error(
                "Por favor, forneça uma pergunta. Exemplo: pergunta Quem foi Santos Dumont?"
            )
            return
            
        try:
            answer = self.controller.answer_question(question)
            self.display_text(answer)
        except Exception as e:
            logger.exception("Error handling question", exc_info=e)
            self.display_error(
                "Não foi possível responder à pergunta. Por favor, tente novamente."
            )
    
    def _handle_explanation(self, concept: str) -> None:
        """
        Handle the 'explain' command.
        
        Args:
            concept: The concept to explain
        """
        if not concept.strip():
            self.display_error(
                "Por favor, forneça um conceito. Exemplo: explique Fotossíntese"
            )
            return
            
        try:
            explanation = self.controller.explain_concept(concept)
            self.display_text(explanation)
        except Exception as e:
            logger.exception("Error handling explanation", exc_info=e)
            self.display_error(
                "Não foi possível explicar o conceito. Por favor, tente novamente."
            )
    
    def _handle_generate_exam(self, args: str) -> None:
        """
        Handle the 'generate-exam' command.
        
        Args:
            args: Command arguments: topic and number of questions
        """
        parts = args.strip().split()
        
        # Check if we have enough arguments
        if len(parts) < 2:
            self.display_error(
                "Por favor, forneça um tópico e o número de questões. "
                'Exemplo: gerar-prova "Literatura Brasileira" 5'
            )
            return
            
        # Extract the number of questions (last part)
        try:
            num_questions = int(parts[-1])
            if num_questions <= 0 or num_questions > 20:
                self.display_error("O número de questões deve estar entre 1 e 20.")
                return
        except ValueError:
            self.display_error(
                "Número de questões inválido. Deve ser um número inteiro positivo."
            )
            return
            
        # Extract the topic (everything except the last part)
        topic = " ".join(parts[:-1]).strip()
        if not topic:
            self.display_error("Por favor, forneça um tópico para a prova.")
            return
            
        # Generate the exam
        try:
            questions = self.controller.generate_exam(topic, num_questions)
            
            if not questions:
                self.display_error(
                    f"Não foi possível gerar questões sobre o tópico '{topic}'. "
                    "Tente outro tópico ou use o comando 'mostrar-topicos'."
                )
                return
                
            # Run the exam
            self._run_exam(questions)
        except Exception as e:
            logger.exception("Error generating exam", exc_info=e)
            self.display_error(
                "Ocorreu um erro ao gerar a prova. Por favor, tente novamente."
            )
    
    def _run_exam(self, questions: List[Question]) -> None:
        """
        Run an exam with the given questions.
        
        Args:
            questions: The list of questions for the exam
        """
        self.clear_screen()
        
        # Introduction
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                         PROVA                                ║
╠══════════════════════════════════════════════════════════════╣
║  Tópico: {questions[0].topic}
║  Número de questões: {len(questions)}
╚══════════════════════════════════════════════════════════════╝

Responda às seguintes questões de múltipla escolha.
Para cada questão, digite a letra correspondente à resposta correta (a, b, c, d ou e).
Boa sorte!
""")
        
        if not self.get_yes_no_input("Pronto para começar a prova? (s/n): "):
            self.display_text("Prova cancelada pelo usuário.")
            return
            
        self.clear_screen()
        
        # Track answers
        answers = []
        
        # Display each question and get the answer
        for i, question in enumerate(questions, 1):
            print(f"\nQuestão {i} de {len(questions)}")
            self.display_question(question.text, question.options)
            
            answer = self.get_multiple_choice_answer()
            answers.append(answer)
            
            print(f"\nSua resposta: ({answer})")
            if i < len(questions):
                input("\nPressione Enter para continuar...")
                self.clear_screen()
        
        # Grade the exam
        score = self.controller.grade_exam(answers, questions)
        self.display_exam_results(score, len(questions))
        
        # Ask if the user wants to see explanations
        if self.get_yes_no_input("\nDeseja ver as explicações das respostas? (s/n): "):
            self._show_exam_explanations(questions, answers)
    
    def _show_exam_explanations(self, questions: List[Question], answers: List[str]) -> None:
        """
        Show explanations for exam questions.
        
        Args:
            questions: The list of questions
            answers: The user's answers
        """
        self.clear_screen()
        print("\n=== EXPLICAÇÕES DAS RESPOSTAS ===\n")
        
        for i, (question, answer) in enumerate(zip(questions, answers), 1):
            correct = answer == question.correct_answer
            status = "✅ CORRETA" if correct else "❌ INCORRETA"
            
            print(f"\nQuestão {i}: {status}")
            print(f"{question.text}\n")
            
            for letter, option in zip(['a', 'b', 'c', 'd', 'e'], question.options):
                prefix = ""
                if letter == question.correct_answer:
                    prefix = "✓ "
                elif letter == answer:
                    prefix = "✗ "
                print(f"{prefix}({letter}) {option}")
            
            print(f"\nExplicação: {question.explanation}")
            
            if i < len(questions):
                input("\nPressione Enter para continuar...")
                print("\n" + "-" * 50 + "\n")
    
    def _handle_show_topics(self, args: str) -> None:
        """
        Handle the 'show-topics' command.
        
        Args:
            args: Command arguments (unused)
        """
        try:
            topics = self.controller.get_exam_topics()
            self.display_topics(topics)
        except Exception as e:
            logger.exception("Error getting topics", exc_info=e)
            self.display_error(
                "Ocorreu um erro ao obter os tópicos disponíveis. Por favor, tente novamente."
            )
    
    def _handle_clear_history(self, args: str) -> None:
        """
        Handle the 'clear-history' command.
        
        Args:
            args: Command arguments (unused)
        """
        if self.get_yes_no_input("Tem certeza que deseja limpar o histórico de conversas? (s/n): "):
            try:
                success = self.controller.clear_conversation_history()
                if success:
                    self.display_success("Histórico de conversas limpo com sucesso!")
                else:
                    self.display_error("Não foi possível limpar o histórico de conversas.")
            except Exception as e:
                logger.exception("Error clearing conversation history", exc_info=e)
                self.display_error(
                    "Ocorreu um erro ao limpar o histórico. Por favor, tente novamente."
                )
    
    def _handle_exit(self, args: str) -> None:
        """
        Handle the 'exit' command.
        
        Args:
            args: Command arguments (unused)
        """
        self.exit() 
