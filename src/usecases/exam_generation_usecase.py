"""
Implementation of the exam generation use case.
"""
import logging
import json
import re
from typing import List, Dict, Any, Optional, Set

from src.entities.question import Question
from src.entities.document import Document
from src.entities.topic import Topic
from src.interfaces.services.llm_service import LLMService
from src.interfaces.services.query_service import QueryService
from src.interfaces.services.embedding_service import EmbeddingService
from src.interfaces.services.exam_service import ExamService
from src.interfaces.repositories.document_repository import (
    DocumentRepository
)
from src.interfaces.repositories.topic_repository import TopicRepository


# Configure logger
logger = logging.getLogger(__name__)


class ExamGenerationUseCase(ExamService):
    """
    Implementation of the exam generation service.
    
    This class handles:
    - Generation of multiple-choice questions on specified topics
    - Grading of completed exams
    - Extraction of available topics from the document base
    """
    
    def __init__(
        self,
        llm_service: LLMService,
        query_service: QueryService,
        embedding_service: EmbeddingService,
        document_repository: DocumentRepository,
        topic_repository: TopicRepository,
        max_context_docs: int = 5,
        min_similarity_score: float = 0.7
    ):
        """
        Initialize the exam generation use case.
        
        Args:
            llm_service: Service for generating text using LLMs
            query_service: Service for processing and retrieving relevant docs
            embedding_service: Service for generating and comparing embeddings
            document_repository: Repository for accessing documents
            topic_repository: Repository for accessing topics
            max_context_docs: Maximum number of documents to include in context
            min_similarity_score: Minimum similarity score for relevant docs
        """
        self.llm_service = llm_service
        self.query_service = query_service
        self.embedding_service = embedding_service
        self.document_repository = document_repository
        self.topic_repository = topic_repository
        self.max_context_docs = max_context_docs
        self.min_similarity_score = min_similarity_score
        
        # Cache for topics to avoid repeated processing
        self._topics_cache: Optional[List[str]] = None
        
        logger.info("Initialized exam generation use case")
    
    def generate_exam(self, topic: str, num_questions: int) -> List[Question]:
        """
        Generate an exam with multiple-choice questions on a specified topic.
        
        Args:
            topic: The topic to generate questions about
            num_questions: The number of questions to generate
            
        Returns:
            A list of Question objects
        """
        logger.info(
            f"Generating exam on topic '{topic}' with {num_questions} questions"
        )
        
        try:
            # Retrieve relevant documents for the topic
            relevant_docs = self._retrieve_documents_for_topic(topic)
            
            if not relevant_docs:
                logger.warning(f"No relevant documents found for topic: {topic}")
                return []
            
            # Prepare context from relevant documents
            context = self._prepare_context_from_documents(relevant_docs)
            
            # Generate questions using LLM
            raw_questions = self._generate_raw_questions(
                topic, context, num_questions
            )
            
            # Parse and validate the generated questions
            questions = self._parse_and_validate_questions(
                raw_questions, topic
            )
            
            if len(questions) < num_questions:
                logger.warning(
                    f"Generated only {len(questions)} valid questions "
                    f"out of {num_questions} requested"
                )
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating exam: {str(e)}")
            return []
    
    def grade_exam(
        self, answers: List[str], questions: List[Question]
    ) -> float:
        """
        Grade a completed exam.
        
        Args:
            answers: The answers provided by the student (a-e)
            questions: The questions in the exam
            
        Returns:
            The score as a percentage (0.0 to 1.0)
        """
        logger.info(f"Grading exam with {len(questions)} questions")
        
        if not questions:
            return 0.0
            
        if len(answers) != len(questions):
            logger.warning(
                f"Number of answers ({len(answers)}) does not match "
                f"number of questions ({len(questions)})"
            )
            # Only grade the questions that have answers
            questions = questions[:len(answers)]
            
        if not questions:
            return 0.0
        
        # Count correct answers
        correct_count = 0
        for i, (answer, question) in enumerate(zip(answers, questions)):
            # Normalize answer to lowercase
            normalized_answer = answer.lower().strip()
            if normalized_answer == question.get_correct_answer():
                correct_count += 1
                logger.debug(f"Question {i+1}: Correct answer")
            else:
                logger.debug(
                    f"Question {i+1}: Incorrect answer. Got {normalized_answer}, "
                    f"expected {question.get_correct_answer()}"
                )
        
        # Calculate percentage
        score = correct_count / len(questions)
        logger.info(
            f"Exam graded: {correct_count}/{len(questions)} correct "
            f"({score:.2%})"
        )
        
        return score
    
    def get_exam_topics(self) -> List[str]:
        """
        Get available topics for exams based on the document base.
        
        Returns:
            A list of topic strings
        """
        # Check if we have cached topics
        if self._topics_cache is not None:
            return self._topics_cache
            
        logger.info("Retrieving available exam topics")
        
        try:
            # Try to get topics from the topic repository first
            topics = self.topic_repository.list_topics()
            
            if topics:
                # Extract topic names and deduplicate
                topic_names = sorted(set(topic.name for topic in topics))
                logger.info(f"Found {len(topic_names)} topics in repository")
                self._topics_cache = topic_names
                return topic_names
            
            # If no topics found in repository, extract from documents
            logger.info("No topics found in repository, extracting from documents")
            all_documents = self.document_repository.list_documents()
            
            if not all_documents:
                logger.warning("No documents found in repository")
                return []
            
            # Extract topics from document metadata and content
            extracted_topics = self._extract_topics_from_documents(all_documents)
            
            logger.info(f"Extracted {len(extracted_topics)} topics from documents")
            self._topics_cache = sorted(extracted_topics)
            return self._topics_cache
            
        except Exception as e:
            logger.error(f"Error retrieving exam topics: {str(e)}")
            return []
    
    def _retrieve_documents_for_topic(self, topic: str) -> List[Document]:
        """
        Retrieve documents relevant to a specific topic.
        
        Args:
            topic: The topic to retrieve documents for
            
        Returns:
            A list of relevant documents
        """
        try:
            # Generate embedding for the topic
            topic_embedding = self.embedding_service.create_embedding(topic)
            
            # Search for similar documents
            docs = self.query_service.retrieve_relevant_documents(
                topic, 
                topic_embedding,
                max_results=self.max_context_docs,
                min_score=self.min_similarity_score
            )
            
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents for topic: {str(e)}")
            return []
    
    def _prepare_context_from_documents(
        self, documents: List[Document]
    ) -> str:
        """
        Prepare context text from relevant documents.
        
        Args:
            documents: List of relevant documents
            
        Returns:
            Formatted context text
        """
        context_parts = []
        
        for i, doc in enumerate(documents):
            # Extract title or use a placeholder
            title = doc.metadata.get("title", f"Documento {i+1}")
            
            # Extract and format content
            content = doc.content
            if len(content) > 2000:
                # Truncate long content
                content = content[:2000] + "..."
            
            # Format as a section
            section = f"--- {title} ---\n{content}\n"
            context_parts.append(section)
        
        return "\n".join(context_parts)
    
    def _generate_raw_questions(
        self, topic: str, context: str, num_questions: int
    ) -> str:
        """
        Generate raw question text using the LLM.
        
        Args:
            topic: The topic for the questions
            context: The context information from documents
            num_questions: Number of questions to generate
            
        Returns:
            Raw text containing the generated questions
        """
        prompt = (
            "Você é um educador experiente preparando questões de múltipla escolha "
            "para estudantes do ensino médio no Brasil se preparando para o vestibular FUVEST.\n\n"
            f"Crie {num_questions} questões de múltipla escolha sobre o tema: {topic}\n\n"
            "Use o seguinte contexto como base para elaborar as questões:\n"
            f"{context}\n\n"
            "Requisitos para as questões:\n"
            "1. Cada questão deve testar a compreensão do aluno, não apenas memorização\n"
            "2. Cada questão deve ter exatamente 5 alternativas (a, b, c, d, e)\n"
            "3. As alternativas incorretas devem ser plausíveis\n"
            "4. Inclua uma explicação do porquê a resposta correta é correta\n"
            "5. Use linguagem clara e apropriada para estudantes do ensino médio\n"
            "6. As questões devem ser desafiadoras mas justas\n\n"
            "Responda no seguinte formato JSON para que eu possa processar facilmente:\n"
            "```json\n"
            "{\n"
            '  "questions": [\n'
            "    {\n"
            '      "text": "Texto da pergunta",\n'
            '      "options": ["Opção A", "Opção B", "Opção C", "Opção D", "Opção E"],\n'
            '      "correct_answer": "a",\n'
            '      "explanation": "Explicação da resposta correta"\n'
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "Certifique-se de que o JSON esteja válido e completo."
        )
        
        # Generate the raw questions using the LLM
        raw_output = self.llm_service.generate_text(prompt)
        
        return raw_output
    
    def _parse_and_validate_questions(
        self, raw_questions: str, topic: str
    ) -> List[Question]:
        """
        Parse and validate the raw questions generated by the LLM.
        
        Args:
            raw_questions: The raw text output from the LLM
            topic: The topic of the questions
            
        Returns:
            A list of validated Question objects
        """
        # Extract JSON content (might be wrapped in markdown code blocks)
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        json_matches = re.findall(json_pattern, raw_questions, re.DOTALL)
        
        if json_matches:
            json_str = json_matches[0]
        else:
            # Try to find a JSON object without code blocks
            json_pattern = r'\{.*"questions":\s*\[.*\]\s*\}'
            json_matches = re.findall(json_pattern, raw_questions, re.DOTALL)
            if json_matches:
                json_str = json_matches[0]
            else:
                logger.error("Failed to extract JSON from LLM output")
                return []
        
        try:
            # Parse the JSON
            data = json.loads(json_str)
            
            if 'questions' not in data:
                logger.error("Missing 'questions' key in JSON data")
                return []
            
            # Process each question
            questions = []
            for i, q_data in enumerate(data['questions']):
                try:
                    # Validate required fields
                    required_fields = ['text', 'options', 'correct_answer', 'explanation']
                    if not all(field in q_data for field in required_fields):
                        logger.warning(
                            f"Question {i+1} missing required fields, skipping"
                        )
                        continue
                    
                    # Validate options length
                    if len(q_data['options']) != 5:
                        logger.warning(
                            f"Question {i+1} has {len(q_data['options'])} options "
                            "instead of 5, skipping"
                        )
                        continue
                    
                    # Create Question object
                    question = Question(
                        text=q_data['text'],
                        options=q_data['options'],
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data['explanation'],
                        topic=topic
                    )
                    
                    questions.append(question)
                    
                except Exception as e:
                    logger.warning(
                        f"Error processing question {i+1}: {str(e)}, skipping"
                    )
                    continue
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error validating questions: {str(e)}")
            return []
    
    def _extract_topics_from_documents(
        self, documents: List[Document]
    ) -> List[str]:
        """
        Extract potential topics from the document collection.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            List of extracted topic strings
        """
        # Collect topics from document metadata
        topics_from_metadata: Set[str] = set()
        
        for doc in documents:
            # Check if document has topic metadata
            if 'topics' in doc.metadata and isinstance(doc.metadata['topics'], list):
                for topic in doc.metadata['topics']:
                    if isinstance(topic, str) and topic.strip():
                        topics_from_metadata.add(topic.strip())
            
            # Check if document has a single topic
            if 'topic' in doc.metadata and isinstance(doc.metadata['topic'], str):
                topic = doc.metadata['topic'].strip()
                if topic:
                    topics_from_metadata.add(topic)
        
        # If we have enough topics from metadata, use those
        if len(topics_from_metadata) >= 5:
            return list(topics_from_metadata)
        
        # Otherwise, ask the LLM to extract topics from document content
        # Select a subset of documents to avoid overwhelming the LLM
        sample_docs = documents[:10]
        sample_content = "\n\n".join(doc.content[:500] for doc in sample_docs)
        
        prompt = (
            "Você é um especialista em educação com foco no vestibular FUVEST. "
            "Com base nos trechos de documentos abaixo, identifique os principais "
            "tópicos de estudo que poderiam ser usados para gerar questões para "
            "estudantes do ensino médio.\n\n"
            "Documentos:\n"
            f"{sample_content}\n\n"
            "Liste entre 10 e 15 tópicos específicos encontrados nestes documentos, "
            "apropriados para questões de vestibular. Responda em formato JSON:\n"
            "```json\n"
            "{\n"
            '  "topics": ["Tópico 1", "Tópico 2", ...]\n'
            "}\n"
            "```"
        )
        
        try:
            # Generate topics using the LLM
            raw_output = self.llm_service.generate_text(prompt)
            
            # Extract JSON
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            json_matches = re.findall(json_pattern, raw_output, re.DOTALL)
            
            if json_matches:
                json_str = json_matches[0]
            else:
                # Try to find JSON object without code blocks
                json_pattern = r'\{\s*"topics":\s*\[.*?\]\s*\}'
                json_matches = re.findall(json_pattern, raw_output, re.DOTALL)
                if json_matches:
                    json_str = json_matches[0]
                else:
                    logger.warning("Failed to extract topics JSON from LLM output")
                    # Fall back to any topics from metadata
                    return list(topics_from_metadata)
            
            # Parse JSON
            data = json.loads(json_str)
            
            if 'topics' in data and isinstance(data['topics'], list):
                extracted_topics = [
                    topic for topic in data['topics'] 
                    if isinstance(topic, str) and topic.strip()
                ]
                
                # Combine with topics from metadata
                all_topics = list(topics_from_metadata) + extracted_topics
                # Remove duplicates and sort
                return sorted(set(all_topics))
            
        except Exception as e:
            logger.error(f"Error extracting topics from documents: {str(e)}")
        
        # Fall back to any topics from metadata
        return list(topics_from_metadata) 
