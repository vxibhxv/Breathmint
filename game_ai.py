# game_ai.py

import anthropic
from typing import Dict
import difflib


class GameAI:
    def __init__(self):
        api_key = "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"
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-7-sonnet-20250219"
        self.max_tokens = 1000
        self.temperature = 0.1
    
    
    def _apply_rules(self, text: str):
        text = text.lower()

        if "where" in text:
            return "where_am_i"
        if "who" in text:
            return "who_is_here"
        if any(kw in text for kw in ["go to", "move to", "travel to"]):
            return "move_location"
        if any(kw in text for kw in ["do", "start", "continue", "complete", "perform"]):
            return "sub_action"
        if "save" in text:
            return "save"
        if "quit" in text or "exit" in text:
            return "quit"
        return None
    
    def _match_node_name(self, user_node_name: str, available_nodes: list[str]):
        """
        Attempts to match the user's intended node to one of the available connections.
        Returns the best match or None.
        """
        try:
            matches = difflib.get_close_matches(user_node_name.lower(), [n.lower() for n in available_nodes], n=1, cutoff=0.6)
        except Exception as e:
            return user_node_name
        if matches:
            # Return the original node name (case-sensitive match)
            for node in available_nodes:
                if node.lower() == matches[0]:
                    return node
        return user_node_name
    
    def classify_input(self, text, state):
        intent = self._apply_rules(text)

        if not intent:
            intent = self._gpt_classify(text)

        args = {}
        if intent == "quit" or intent == "save":
            state.save_game()
            print("Quiting game...")
            return {"action": "quit"}

        if intent == "move_location":
            args = {
                "action": "move_to",
                "raw": text
            }
        elif intent == "sub_action":
            args = {
                "action": "perform_event",
                "raw": text
            }
        else:
            args = {
                "action": "describe",
                "raw": text
            }
        return args
    
    def _extract_node(self, text_input: str, options):
        prompt = f"""
Player said: "{text_input}"

Known nodes: {', '.join(options)}

If the player is asking to move, return ONLY the node name. If it's not clear, return "unknown".
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            loc = response.content[0].text
            print("Extracted node:", loc)
            return loc
        except Exception as e:
            print("GPT error during node extraction:", e)
            return None

    def process_command(self, classified: Dict, state) -> str:
        action = classified["action"]
        take_action = classified.get("raw")

        if action == "describe":
            question = take_action
            return self._gpt_respond_about_context(question, state.describe())

        elif action == "move_to":
            requested_node = take_action
            available = state.current_node.connections
            matched_node = self._extract_node(requested_node, available)
            if matched_node:
                state.move_to(matched_node)
                return self._gpt_wrap_movement(matched_node, state.current_node.describe())
            else:
                return f"You can't go to '{requested_node}' from here. Try: {', '.join(available)}."
            
        elif action == "perform_event":
            result = state.perform_event()

            # GPT handles interactive turns
            if isinstance(result, dict) and result.get("status") == "awaiting_player_question":
                response = result["response"]
                return response

            # GPT wraps up movement after conversation ends
            elif isinstance(result, dict) and result.get("status") == "movement_complete":
                return self._gpt_wrap_movement(result["location"], result["description"])
            else:
                return result

        return f"I don't understand: {take_action}"

    # === GPT helpers ===
    def _gpt_classify(self, text: str) -> Dict:
        prompt = f"""
You are a game input classifier. Map the input to one of the following intent keywords:
- where_am_i : User wants location information
- who_is_here : User wants other characters/player information
- where_can_i_go : User wants to know where they can go
- what_can_i_do : User wants to know what they can do
- move_location: Player wants to go to a new location
- sub_action: Player wants to do something
- save: Player wants to save
- quit: Player wants to quit

Input: "{text}"

Respond ONLY with one of the above. If unclear, respond with "fallback".
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
