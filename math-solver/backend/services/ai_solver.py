import os
import logging
import re
from typing import Optional, Dict, List, Any
import asyncio
import uuid

try:
    import openai
except ImportError:
    openai = None

from retry import retry_with_backoff, RetryableException, DEFAULT_API_RETRY_CONFIG
from errors import AIError, APIServiceError, ValidationError

logger = logging.getLogger(__name__)


class AISolver:
    """AI-powered problem solver with retry logic and error handling"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key and openai:
            openai.api_key = self.openai_api_key
        
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        logger.info("AISolver initialized")
    
    async def solve_problem(
        self,
        problem: str,
        capabilities: Dict[str, bool],
        file_data: Optional[Dict] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Solve a problem using AI with optional web search and code execution.
        
        Args:
            problem: The problem statement
            capabilities: Dict of enabled capabilities (webSearch, codeExecution, stepByStep)
            file_data: Optional file data associated with the problem
            session_id: Optional session ID for conversation history
            request_id: Optional request ID for tracking
        
        Returns:
            Dict with solution, steps, code, and metadata
        """
        request_id = request_id or str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())
        
        logger.info(
            f"Solving problem (request_id={request_id}, session_id={session_id})",
            extra={"problem_length": len(problem), "capabilities": capabilities}
        )
        
        try:
            if not problem or not problem.strip():
                raise ValidationError("Problem statement cannot be empty")
            
            # Validate capabilities
            valid_capabilities = {"webSearch", "codeExecution", "stepByStep"}
            for key in capabilities.keys():
                if key not in valid_capabilities:
                    logger.warning(f"Unknown capability: {key}")
            
            # Build system prompt
            system_prompt = self._build_system_prompt(capabilities)
            
            # Build user message
            user_message = self._build_user_message(problem, file_data)
            
            # Maintain conversation context
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            # Add to history
            self.conversation_history[session_id].append({
                "role": "user",
                "content": user_message
            })
            
            # Get AI response with retry logic
            response = await self._call_openai_with_retry(
                system_prompt=system_prompt,
                session_id=session_id,
                request_id=request_id
            )
            
            # Store response in history
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": response.get("content", "")
            })
            
            # Extract structured data from response
            steps = self._extract_steps(response.get("content", ""))
            code = self._extract_code(response.get("content", "")) if capabilities.get("codeExecution") else None
            
            result = {
                "solution": response.get("content", ""),
                "steps": steps,
                "code": code,
                "confidence": response.get("confidence", 0.7),
                "error": None,
                "session_id": session_id,
                "request_id": request_id
            }
            
            logger.info(f"Problem solved successfully (request_id={request_id})")
            return result
            
        except (ValidationError, AIError) as e:
            logger.error(f"Expected error solving problem (request_id={request_id}): {str(e)}")
            return {
                "solution": None,
                "steps": [],
                "code": None,
                "confidence": 0.0,
                "error": str(e.message),
                "error_type": e.error_type.value if hasattr(e, 'error_type') else "unknown",
                "session_id": session_id,
                "request_id": request_id
            }
        
        except Exception as e:
            logger.exception(f"Unexpected error solving problem (request_id={request_id})")
            return {
                "solution": None,
                "steps": [],
                "code": None,
                "confidence": 0.0,
                "error": f"An unexpected error occurred: {str(e)}",
                "error_type": "internal_error",
                "session_id": session_id,
                "request_id": request_id
            }
    
    async def _call_openai_with_retry(
        self,
        system_prompt: str,
        session_id: str,
        request_id: str
    ) -> Dict[str, Any]:
        """Call OpenAI API with retry logic"""
        
        if not self.openai_api_key or not openai:
            logger.warning(f"OpenAI API key not configured (request_id={request_id}), using mock response")
            return self._mock_response()
        
        async def _call():
            return await self._call_openai(system_prompt, session_id, request_id)
        
        try:
            return await retry_with_backoff(
                _call,
                config=DEFAULT_API_RETRY_CONFIG,
                on_retry=lambda attempt, delay, exc: logger.warning(
                    f"Retrying OpenAI API (attempt {attempt}, delay {delay:.2f}s, request_id={request_id})"
                )
            )
        except RetryableException as e:
            logger.error(f"OpenAI API failed after retries (request_id={request_id}): {str(e)}")
            raise APIServiceError(
                f"Failed to get response from AI service after retries: {str(e.original_exception or e)}",
                details={"request_id": request_id},
                retryable=True
            )
    
    async def _call_openai(
        self,
        system_prompt: str,
        session_id: str,
        request_id: str
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            
            # Add conversation history (last 5 messages for context)
            history = self.conversation_history.get(session_id, [])
            messages.extend(history[-10:])  # Keep last 10 messages for context
            
            logger.debug(f"Calling OpenAI API with {len(messages)} messages (request_id={request_id})")
            
            # Use async OpenAI client if available, otherwise sync
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                timeout=30.0
            )
            
            content = response.choices[0].message.content
            
            logger.debug(f"Received response from OpenAI (request_id={request_id}, content_length={len(content)})")
            
            return {
                "content": content,
                "model": response.model,
                "usage": response.usage.dict() if hasattr(response.usage, 'dict') else {},
                "confidence": 0.9
            }
            
        except Exception as e:
            error_msg = str(e)
            
            if "rate limit" in error_msg.lower():
                logger.error(f"Rate limit exceeded (request_id={request_id})")
                raise RetryableException(
                    f"OpenAI API rate limit exceeded: {error_msg}",
                    original_exception=e
                )
            
            elif "timeout" in error_msg.lower():
                logger.error(f"OpenAI API timeout (request_id={request_id})")
                raise RetryableException(
                    f"OpenAI API timeout: {error_msg}",
                    original_exception=e
                )
            
            elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                logger.error(f"OpenAI API authentication failed (request_id={request_id})")
                raise APIServiceError(
                    f"Authentication failed: Invalid API key",
                    details={"request_id": request_id},
                    retryable=False
                )
            
            else:
                logger.error(f"OpenAI API error (request_id={request_id}): {error_msg}")
                raise RetryableException(
                    f"OpenAI API error: {error_msg}",
                    original_exception=e
                )
    
    def _build_system_prompt(self, capabilities: Dict[str, bool]) -> str:
        """Build context-aware system prompt based on enabled capabilities"""
        prompt = (
            "You are an expert problem solver specializing in mathematics, science, and coding. "
            "Your goal is to provide clear, accurate, and comprehensive solutions. "
        )
        
        if capabilities.get("stepByStep"):
            prompt += "Always provide detailed step-by-step explanations for your solutions. "
        
        if capabilities.get("webSearch"):
            prompt += "You can reference web search results for current information and concepts. "
        
        if capabilities.get("codeExecution"):
            prompt += (
                "If appropriate, provide executable code blocks wrapped in ```language\ncode\n``` format. "
            )
        
        prompt += (
            "Format your response clearly with:\n"
            "- A concise explanation of the approach\n"
            "- Step-by-step solution (if applicable)\n"
            "- Code examples (if requested and applicable)\n"
            "- Final answer/conclusion\n"
            "Be thorough but concise."
        )
        
        return prompt
    
    def _build_user_message(self, problem: str, file_data: Optional[Dict] = None) -> str:
        """Build user message with context"""
        message = f"Problem: {problem}"
        
        if file_data:
            message += f"\n\nFile attached: {file_data.get('filename', 'unknown')} (Type: {file_data.get('file_type', 'unknown')})"
            if file_data.get('text'):
                message += f"\nFile content preview:\n{file_data['text'][:500]}"
        
        return message
    
    def _extract_steps(self, content: str) -> List[str]:
        """Extract step-by-step instructions from response using regex"""
        steps = []
        
        if not content:
            return steps
        
        # Pattern 1: "Step N:" or "Step N:"
        step_pattern = r'(?:^|\n)\s*(?:Step\s+\d+|[0-9]+\.)\s*(?::)?\s*(.+?)(?=(?:Step\s+\d+|[0-9]+\.|$))'
        matches = re.finditer(step_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        for match in matches:
            step_text = match.group(1).strip()
            if step_text:
                steps.append(f"Step {len(steps) + 1}: {step_text}")
        
        # If no steps found, split by common delimiters
        if not steps:
            lines = content.split('\n')
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(('-', '*', '•')) or re.match(r'^\d+\.\s', stripped):
                    steps.append(stripped)
        
        # If still no steps, use the whole content
        if not steps:
            steps = [content[:200] + "..." if len(content) > 200 else content]
        
        return steps[:10]  # Limit to 10 steps
    
    def _extract_code(self, content: str) -> Optional[str]:
        """Extract code blocks from response using regex"""
        if not content:
            return None
        
        # Pattern for markdown code blocks with language specification
        pattern = r'```(?:\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            # Return the first (largest) code block
            code_block = matches[0].strip()
            if code_block:
                return code_block
        
        # Alternative pattern for plain triple backticks
        if '```' in content:
            parts = content.split('```')
            if len(parts) >= 3:
                return parts[1].strip()
        
        return None
    
    def _mock_response(self) -> Dict[str, Any]:
        """Generate mock response when API is not available"""
        return {
            "content": (
                "Mock Response: To enable real AI solving, please configure your OpenAI API key "
                "in the .env file.\n\n"
                "For now, here are generic steps for problem solving:\n"
                "1. Analyze the problem statement carefully\n"
                "2. Identify the relevant concepts and formulas\n"
                "3. Break down the problem into smaller parts\n"
                "4. Apply the appropriate methods or calculations\n"
                "5. Verify your answer and check for errors"
            ),
            "model": "mock",
            "usage": {},
            "confidence": 0.3
        }
    
    async def web_search(self, query: str) -> List[Dict]:
        """Perform web search (mock implementation)"""
        logger.info(f"Web search requested for: {query}")
        return [
            {
                "title": f"Search result for: {query}",
                "url": "https://example.com",
                "snippet": "Web search not yet implemented. Configure a search API to enable this feature."
            }
        ]
    
    async def execute_code(self, code: str) -> Dict:
        """Execute code safely (mock implementation)"""
        logger.warning("Code execution requested but not yet implemented")
        return {
            "output": "Code execution not yet implemented. Use caution when running untrusted code.",
            "error": None
        }
    
    def clear_session_history(self, session_id: str) -> None:
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            logger.info(f"Cleared history for session: {session_id}")