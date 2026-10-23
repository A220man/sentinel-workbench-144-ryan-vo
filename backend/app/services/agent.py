"""Agent state management service."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Window, AgentState, AgentStateHistory, AttentionItem, AttentionKind
from app.models.user import User


class AgentService:
    """Service for managing agent states and attention items."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def update_agent_state(
        self,
        window_id: int,
        new_state: AgentState,
        actor: Optional[User] = None,
    ) -> Window:
        """Update window agent state and create history/attention items."""
        window = await self.db.get(Window, window_id)
        if not window:
            raise ValueError(f"Window {window_id} not found")
        
        old_state = window.agent_state
        if old_state == new_state:
            return window
        
        # Create history entry
        history = AgentStateHistory(
            window_id=window.id,
            from_state=old_state,
            to_state=new_state,
        )
        self.db.add(history)
        
        # Update window
        window.agent_state = new_state
        window.updated_at = datetime.now(timezone.utc)
        
        # Handle attention items based on state transition
        await self._handle_state_transition(window, old_state, new_state)
        
        await self.db.commit()
        await self.db.refresh(window)
        return window
    
    async def _handle_state_transition(
        self,
        window: Window,
        from_state: AgentState,
        to_state: AgentState,
    ) -> None:
        """Create or dismiss attention items based on state transition."""
        # If window is quiet, don't create attention items for finished/question/errored
        if window.quiet and to_state in (AgentState.DONE, AgentState.NEEDS_INPUT, AgentState.ERRORED):
            return
        
        # Dismiss existing attention items when state changes away from terminal states
        if from_state in (AgentState.DONE, AgentState.NEEDS_INPUT, AgentState.ERRORED):
            await self._dismiss_attention_for_window(window.id, [AttentionKind.FINISHED, AttentionKind.QUESTION, AttentionKind.ERRORED])
        
        # Create new attention items for terminal states
        if to_state == AgentState.DONE:
            window.completion_seq += 1
            item = AttentionItem(
                window_id=window.id,
                kind=AttentionKind.FINISHED,
                title=f"Pane {window.index + 1} finished turn #{window.completion_seq}",
                human_nonce=self._generate_nonce(),
            )
            self.db.add(item)
        elif to_state == AgentState.NEEDS_INPUT:
            item = AttentionItem(
                window_id=window.id,
                kind=AttentionKind.QUESTION,
                title=f"Pane {window.index + 1} needs input",
                human_nonce=self._generate_nonce(),
            )
            self.db.add(item)
        elif to_state == AgentState.ERRORED:
            item = AttentionItem(
                window_id=window.id,
                kind=AttentionKind.ERRORed,
                title=f"Pane {window.index + 1} errored",
                human_nonce=self._generate_nonce(),
            )
            self.db.add(item)
    
    async def _dismiss_attention_for_window(
        self,
        window_id: int,
        kinds: list[AttentionKind],
    ) -> None:
        """Dismiss undismissed attention items of given kinds for a window."""
        from sqlalchemy import update
        stmt = update(AttentionItem).where(
            AttentionItem.window_id == window_id,
            AttentionItem.dismissed_at.is_(None),
            AttentionItem.kind.in_(kinds),
        ).values(dismissed_at=datetime.now(timezone.utc))
        await self.db.execute(stmt)
    
    def _generate_nonce(self) -> str:
        """Generate a human nonce for attention dismissal."""
        import secrets
        return secrets.token_urlsafe(16)
    
    async def set_window_quiet(self, window_id: int, quiet: bool) -> Window:
        """Set window quiet mode."""
        window = await self.db.get(Window, window_id)
        if not window:
            raise ValueError(f"Window {window_id} not found")
        
        window.quiet = quiet
        window.updated_at = datetime.now(timezone.utc)
        
        if quiet:
            # Dismiss existing attention items for this window
            await self._dismiss_attention_for_window(
                window_id,
                [AttentionKind.FINISHED, AttentionKind.QUESTION, AttentionKind.ERRORED]
            )
        
        await self.db.commit()
        await self.db.refresh(window)
        return window
