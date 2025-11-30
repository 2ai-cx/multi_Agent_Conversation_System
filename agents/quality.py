"""
Quality Agent - Response Validator

Responsibilities:
- Validate responses against scorecard criteria
- Evaluate each criterion as boolean pass/fail
- Provide specific feedback for failed criteria
- Trigger refinement when validation fails
- Approve graceful failure messages
- Log all validation failures
"""

from typing import Dict, Any, List
from agents.base import BaseAgent
from agents.models import Scorecard, ScorecardCriterion, ValidationResult, ValidationFailureLog


class QualityAgent(BaseAgent):
    """
    Validator agent that ensures response quality before sending.
    """
    
    async def validate_response(
        self,
        request_id: str,
        response: str,
        scorecard: Dict[str, Any],
        channel: str,
        original_question: str
    ) -> Dict[str, Any]:
        """
        Validate response against scorecard criteria.
        
        Args:
            request_id: Unique request identifier
            response: Formatted response to validate
            scorecard: Scorecard with validation criteria
            channel: Communication channel
            original_question: User's original question
            
        Returns:
            Dict with validation_result and failed_criteria
        """
        self.logger.info(f"✅ [Quality] Starting validation: {request_id}")
        self.logger.info(f"📝 [Quality] Response length: {len(response)} chars")
        self.logger.info(f"📱 [Quality] Channel: {channel}")
        
        # Parse scorecard
        scorecard_obj = Scorecard(**scorecard)
        self.logger.info(f"📊 [Quality] Validating against {len(scorecard_obj.criteria)} criteria")
        
        # Evaluate each criterion
        self.logger.info(f"🔍 [Quality] Evaluating criteria...")
        for criterion in scorecard_obj.criteria:
            self.logger.info(f"  ⏳ Evaluating: {criterion.id} - {criterion.description}")
            passed, feedback = await self._evaluate_criterion(
                criterion, response, channel, original_question
            )
            criterion.passed = passed
            criterion.feedback = feedback
            if passed:
                self.logger.info(f"  ✅ PASS: {criterion.id}")
            else:
                self.logger.warning(f"  ❌ FAIL: {criterion.id} - {feedback}")
        
        # Evaluate overall
        overall_passed = scorecard_obj.evaluate()
        self.logger.info(f"🎯 [Quality] Overall result: {'PASS' if overall_passed else 'FAIL'}")
        
        # Get failed criteria
        failed_criteria = scorecard_obj.get_failed_criteria()
        failed_ids = [c.id for c in failed_criteria]
        if failed_criteria:
            self.logger.warning(f"❌ [Quality] {len(failed_criteria)} criteria failed: {', '.join(failed_ids)}")
        
        # Aggregate feedback
        aggregated_feedback = None
        if not overall_passed:
            aggregated_feedback = self._aggregate_feedback(failed_criteria)
            self.logger.info(f"📝 [Quality] Aggregated feedback: {aggregated_feedback[:100]}..." if len(aggregated_feedback) > 100 else f"📝 [Quality] Aggregated feedback: {aggregated_feedback}")
            
            # Log validation failure
            self._log_validation_failure(
                request_id,
                original_question,
                scorecard_obj,
                failed_criteria
            )
        
        # Create validation result
        validation_result = ValidationResult(
            request_id=request_id,
            passed=overall_passed,
            scorecard_id=scorecard_obj.request_id,
            failed_criteria_ids=failed_ids,
            feedback=aggregated_feedback
        )
        
        self.logger.info(f"✅ [Quality] Validation complete. Result: {'APPROVED' if overall_passed else 'NEEDS REFINEMENT'}")
        
        return {
            "validation_result": validation_result.model_dump(mode='json'),
            "failed_criteria": [c.model_dump(mode='json') for c in failed_criteria]
        }
    
    async def _evaluate_criterion(
        self,
        criterion: ScorecardCriterion,
        response: str,
        channel: str,
        original_question: str
    ) -> tuple[bool, str]:
        """
        Evaluate a single criterion.
        
        Args:
            criterion: Criterion to evaluate
            response: Response to check
            channel: Communication channel
            original_question: User's question
            
        Returns:
            Tuple of (passed: bool, feedback: str)
        """
        # Build evaluation prompt
        prompt = f"""Evaluate if this response meets the criterion.

Response: "{response}"
Channel: {channel}
Original question: "{original_question}"

Criterion: {criterion.description}
Expected: {criterion.expected}

Does the response meet this criterion?
Answer with "yes" if it passes, or "no - [specific reason]" if it fails.

Evaluation:"""
        
        # Call LLM
        evaluation = await self.llm_client.generate(prompt)
        
        # Parse evaluation
        if isinstance(evaluation, dict):
            evaluation = evaluation.get("result", str(evaluation))
        
        evaluation = str(evaluation).strip().lower()
        
        if evaluation.startswith("yes"):
            return True, ""
        else:
            # Extract feedback
            feedback = evaluation.replace("no -", "").replace("no,", "").strip()
            if not feedback:
                feedback = f"Failed: {criterion.description}"
            return False, feedback
    
    def _aggregate_feedback(self, failed_criteria: List[ScorecardCriterion]) -> str:
        """
        Aggregate feedback from multiple failed criteria.
        
        Args:
            failed_criteria: List of failed criteria
            
        Returns:
            Aggregated feedback string
        """
        if not failed_criteria:
            return ""
        
        feedback_parts = []
        for criterion in failed_criteria:
            if criterion.feedback:
                feedback_parts.append(f"- {criterion.description}: {criterion.feedback}")
            else:
                feedback_parts.append(f"- {criterion.description}: Failed")
        
        return "\n".join(feedback_parts)
    
    def _log_validation_failure(
        self,
        request_id: str,
        original_question: str,
        scorecard: Scorecard,
        failed_criteria: List[ScorecardCriterion]
    ):
        """
        Log validation failure for debugging.
        
        Args:
            request_id: Request identifier
            original_question: User's question
            scorecard: Scorecard that was evaluated
            failed_criteria: Criteria that failed
        """
        failure_log = ValidationFailureLog(
            request_id=request_id,
            original_question=original_question,
            scorecard=scorecard,
            validation_results=failed_criteria,
            refinement_attempted=False,  # Will be updated if refinement happens
            refinement_succeeded=None,
            final_outcome="Pending refinement",
            failure_reason=f"{len(failed_criteria)} criteria failed validation"
        )
        
        self.logger.warning(f"Validation failure: {failure_log.model_dump_json()}")
    
    async def validate_graceful_failure(
        self,
        request_id: str,
        failure_message: str,
        failure_reason: str
    ) -> Dict[str, Any]:
        """
        Validate and approve graceful failure message.
        
        Graceful failures are always approved, but logged for debugging.
        
        Args:
            request_id: Request identifier
            failure_message: User-friendly failure message
            failure_reason: Technical failure reason
            
        Returns:
            Dict with approved=True and logged=True
        """
        # Log graceful failure
        self.logger.info(
            f"Graceful failure approved for {request_id}: "
            f"Reason: {failure_reason}, Message: {failure_message}"
        )
        
        return {
            "approved": True,
            "logged": True
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Quality agent action"""
        action = input_data.get("action")
        
        if action == "validate_response":
            return await self.validate_response(
                input_data["request_id"],
                input_data["response"],
                input_data["scorecard"],
                input_data["channel"],
                input_data["original_question"]
            )
        elif action == "validate_graceful_failure":
            return await self.validate_graceful_failure(
                input_data["request_id"],
                input_data["failure_message"],
                input_data["failure_reason"]
            )
        else:
            raise ValueError(f"Unknown action: {action}")
