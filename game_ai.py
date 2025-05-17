# game_ai.py

import anthropic
from typing import Dict
import difflib


class GameAI:
    def __init__(self):
        api_key = open("api_key.txt", "r").read().strip()
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-7-sonnet-20250219"
        self.max_tokens = 1000
        self.temperature = 0.1
    
    def _match_node_name(self, user_node_name: str, available_nodes: list[str]):
        """
        Attempts to match the user's intended node to one of the available connections.
        Returns the best match or None.
        """
        matches = difflib.get_close_matches(user_node_name.lower(), [n.lower() for n in available_nodes], n=1, cutoff=0.6)
        if matches:
            # Return the original node name (case-sensitive match)
            for node in available_nodes:
                if node.lower() == matches[0]:
                    return node
        return None

    def process_command(self, classified: Dict, state) -> str:
        action = classified["action"]
        args = classified.get("args", {})

        if action == "describe":
            question = args.get("raw", "describe")
            return self._gpt_respond_about_context(question, state.describe())

        elif action == "move_to":
            requested_node = args["node"]
            available = state.current_node.connections

            matched_node = self._match_node_name(requested_node, available)
            if matched_node:
                state.move_to(matched_node)
                return self._gpt_wrap_movement(matched_node, state.current_node.describe())
            else:
                return f"You can't go to '{requested_node}' from here. Try: {', '.join(available)}."
            
        elif action == "perform_event":
            result = state.perform_event()

            # GPT handles interactive turns
            if isinstance(result, dict) and result.get("status") == "awaiting_player_question":
                player_question = args.get("raw", "")
                response = self._gpt_conversation(
                    player_input=player_question,
                    conversation_context=result["context"],
                    history=result["history"]
                )
                state.conversation_history.append((player_question, response))
                return response

            # GPT wraps up movement after conversation ends
            elif isinstance(result, dict) and result.get("status") == "movement_complete":
                return self._gpt_wrap_movement(result["location"], result["description"])

            # Turn 1: pre-written lines
            else:
                return result


        elif action == "quit":
            return "Thanks for playing."

        return f"I don't understand: {args.get('raw', '')}"

    # === GPT helpers ===
    def classify_input(self, text: str, context) -> Dict:
        prompt = f"""
You are the input interpreter for a text adventure game.
Your job is to map free-form player input into one of the following actions:
Game context:
\"\"\"
{context}
\"\"\"

- describe : The user wants to know more about the game.
options: list connections, characters and events
- move_to : The user wants to move to a different location.
- perform_event : The user wants to talk to someone or do something.
- quit : The user wants to quit the game.
- unknown : The user input doesn't match any of the above actions.

Input: "{text}"
Output: JSON object like one of:
{{"action": "describe", "args": {{}}}}
{{"action": "move_to", "args": {{"node": "kitchen"}}}}
{{"action": "perform_event", "args": {{}}}}
{{"action": "quit", "args": {{}}}}
{{"action": "unknown", "args": {{"raw": "..."}}}}
"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        import json
        try:
            return json.loads(response.content[0].text)
        except Exception:
            return {"action": "unknown", "args": {"raw": text, "reason": "GPT parse error"}}

    def _gpt_respond_about_context(self, question: str, context: str) -> str:
        prompt = f"""You are the narrator of a text adventure game.

Player asks: "{question}"
Game context:
\"\"\"
{context}
\"\"\"

Answer briefly and only using details from the context.
"""
        return self._call_gpt(prompt)

    def _gpt_wrap_movement(self, location: str, description: str) -> str:
        prompt = f"""The player just moved to {location}.

New location description:
\"\"\"
{description}
\"\"\"

Write a short transition message describing the move and what they now see.
"""
        return self._call_gpt(prompt)

    def _gpt_conversation(self, player_input: str, conversation_context: list[str], history: list[tuple[str, str]]) -> str:
        # messages = [{"role": "system", "content": "You are an NPC or narrator in a text-based adventure game."}]
        messages = []
        if isinstance(conversation_context, list):
            context_text = "\n".join(conversation_context)
        else:
            context_text = str(conversation_context)

        messages.append({"role": "user", "content": f"Scene:\n{context_text}"})

        for user_input, npc_reply in history:
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": npc_reply})

        messages.append({"role": "user", "content": player_input})

        response = self.client.messages.create(
            model=self.model,
            system = "You are an NPC or narrator in a text-based adventure game.",
            temperature=self.temperature,
            messages=messages,
            max_tokens=self.max_tokens
        )

        return response.content[0].text


    def _call_gpt(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
