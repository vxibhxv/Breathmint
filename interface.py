import json
from typing import List, Dict, Optional, Union
# from openai import OpenAI

import anthropic

class Interface:
    def __init__(self, game_state, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        self.game_state = game_state
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

        self.INTENTS = {
            "where_am_i": "Where am I?",
            "who_is_here": "Who all are there?",
            "move_location": "Move to new location",
            "sub_action": "Do sub-action part of action",
            "save": "Save the game",
            "quit": "Quit the game",
            "fallback": "Unknown / ambiguous input"
        }

    def handle_input(self, text_input: str, input_req: List[str], options: List[Dict]):
        """
        Main entry point to handle player input.
        Uses rules + GPT to determine intent and arguments.
        """
        intent = self._apply_rules(text_input)

        if not intent:
            intent = self._gpt_classify(text_input)

        args = {}

        # Generalized argument extraction
        if input_req:
            extracted = self._extract_args(text_input, input_req, options)
            if extracted:
                args.update(extracted)
            elif intent != "fallback":
                return "I couldn't determine the details of your request."

        return intent, args

    # -------------------- Rule-based Intent Matching -------------------- #
    def _apply_rules(self, text: str) -> Optional[str]:
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

    def _gpt_classify(self, text_input: str) -> str:
        prompt = f"""
You are a game input classifier. Map the input to one of the following intent keywords:
- where_am_i : User wants location information
- who_is_here : User wants other characters/player information
- move_location: Player wants to go to a new location
- sub_action: Player wants to do something
- save: Player wants to save
- quit: Player wants to quit

Input: "{text_input}"

Respond ONLY with one of the above. If unclear, respond with "fallback".
"""
        try:
            response = self.client.messages.create(
                model=self.model,
                system = "You help classify player inputs for a game.",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            print(response.content[0])
            return response.content[0].text
        except Exception as e:
            print("GPT error:", e)
            return "fallback"

    # -------------------- General Argument Extractor -------------------- #
    def _extract_args(self, text_input: str, input_req: List[str], options: List[Dict]) -> Optional[Dict[str, str]]:
        if input_req == ['node']:
            return self._extract_node(text_input, options)
        elif input_req == ['event', 'stages']:
            return self._extract_event_and_stage(text_input, options)
        else:
            return None

    def _extract_node(self, text_input: str, options: List[Dict]) -> Optional[Dict[str, str]]:
        nodes = [opt["node"] for opt in options if "node" in opt]

        prompt = f"""
Player said: "{text_input}"

Known nodes: {', '.join(nodes)}

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
            return {"node": loc} if loc.lower() != "unknown" else None
        except Exception as e:
            print("GPT error during node extraction:", e)
            return None

    def _extract_event_and_stage(self, text_input: str, options: List[Dict]) -> Optional[Dict[str, str]]:
        # Flatten options into list of {event, stage}
        flattened = []
        for opt in options:
            event_name = opt['event'][0] if isinstance(opt['event'], (list, tuple)) else opt['event']
            for stage in opt.get('stages', []):
                flattened.append({"event": event_name, "stage": stage})

        prompt = f"""
The player input is: "{text_input}"

Match it to one of the known stages from below. Each stage belongs to an event.

Options:
{json.dumps(flattened, indent=2)}

Respond ONLY with JSON like:
{{ "event": "event_name", "stage": "stage_name" }}

If you can't determine, return: "unknown"
"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            content = response.content[0].text
            print(content)
            if content.lower() == "unknown":
                return None
            return json.loads(content)
        except Exception as e:
            print("GPT error during event-stage extraction:", e)
            return None