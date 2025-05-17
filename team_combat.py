# combat_team.py

# Team Combat System - Four rangers vs Baby-Green
# Moves cost breath. Breathing in and Out controls the flow of combat.

import random
import time

# Stats:
#   Brain - Intelligence/strategic skills
#   Spine - Courage/willpower
#   Eyes - Perception/accuracy
#   Hands - Upper body strength/dexterity
#   Legs - Lower body strength/mobility
#   Breath - Resource for combat actions
#   HP - Health points

class CombatParticipant:
    def __init__(self, name, stats, skills, is_player=False):
        self.name = name
        self.stats = stats
        self.skills = skills
        self.is_player = is_player
        
    def breath_action(self):
        """Increase breath by 1"""
        self.stats['Breath'] += 1
        print(f"{self.name} takes a deep breath. Breath increased to {self.stats['Breath']}")
        return 0  # No damage
    
    def calculate_damage(self, stat, min_roll, max_roll):
        """Calculate damage based on stat and random roll"""
        stat_value = self.stats[stat]
        roll = random.randint(min_roll, max_roll)
        damage = stat_value * roll
        return damage
    
    def use_skill(self, skill_name, target):
        """Use a skill on the target"""
        # Find the skill
        selected_skill = None
        for skill in self.skills:
            if skill['name'].lower() == skill_name.lower():
                selected_skill = skill
                break
                
        if not selected_skill:
            print(f"Skill '{skill_name}' not found!")
            return False
        
        # Check if we have enough breath
        if self.stats['Breath'] < selected_skill['breath_cost']:
            print(f"{self.name} doesn't have enough breath to use {selected_skill['name']}!")
            return False
        
        # Deduct breath cost
        self.stats['Breath'] -= selected_skill['breath_cost']
        
        # Calculate damage and effects
        damage = 0
        effect = None
        
        if selected_skill['name'].lower() == 'punch':
            damage = self.calculate_damage('Hands', 0, 6)
            print(f"{self.name} delivers a powerful punch!")
        elif selected_skill['name'].lower() == 'kick':
            damage = self.calculate_damage('Legs', 0, 10)
            print(f"{self.name} executes a devastating kick!")
        elif selected_skill['name'].lower() == 'power slam':
            damage = self.calculate_damage('Hands', 5, 15)
            print(f"{self.name} leaps into the air and slams down with tremendous force!")
        elif selected_skill['name'].lower() == 'brain blast':
            damage = self.calculate_damage('Brain', 3, 12)
            print(f"{self.name} focuses mental energy into a concentrated blast!")
        elif selected_skill['name'].lower() == 'eye beam':
            damage = self.calculate_damage('Eyes', 4, 14)
            print(f"{self.name} shoots precision energy beams from their visor!")
        elif selected_skill['name'].lower() == 'spine strike':
            damage = self.calculate_damage('Spine', 2, 16)
            print(f"{self.name} channels courage into a powerful strike!")
        elif selected_skill['name'].lower() == 'heat wave':
            damage = self.calculate_damage('Spine', 2, 16)
            print(f"{self.name} unleashes waves of intense heat from their suit!")
            print(f"The attack leaves burn marks across {target.name}'s body!")
        elif selected_skill['name'].lower() == 'acrobatic strike':
            damage = self.calculate_damage('Legs', 4, 12)
            print(f"{self.name} performs an incredible series of flips before striking!")
            print(f"{self.name} is positioned to dodge the next attack!")
        elif selected_skill['name'].lower() == 'earth shatter':
            damage = self.calculate_damage('Spine', 3, 14)
            effect = 'stun'
            print(f"{self.name} channels the power of earth, creating a shockwave!")
            print(f"The ground cracks beneath {target.name}, stunning it momentarily!")
        elif selected_skill['name'].lower() == 'tech blast':
            damage = self.calculate_damage('Brain', 3, 12)
            print(f"{self.name} activates advanced weaponry systems for a tech-enhanced blast!")
        elif selected_skill['name'].lower() == 'shove':
            # Shove applies stun but no damage
            effect = 'stun'
            print(f"{self.name} shoves {target.name} off balance!")
        elif selected_skill['name'].lower() == 'group heal' or selected_skill['name'].lower() == 'field repair':
            # Return a special indicator for group heal
            print(f"{self.name} activates emergency suit repairs for the entire team!")
            return "group_heal"
        elif selected_skill['name'].lower() == 'breathe':
            self.breath_action()
            return True
        
        # Apply damage and effects
        if damage > 0:
            target.stats['hp'] -= damage
            print(f"{target.name} takes {damage} damage!")
            
            # Check for critical hit
            if random.random() < 0.1:  # 10% chance for critical
                bonus = int(damage * 0.5)
                target.stats['hp'] -= bonus
                print(f"CRITICAL HIT! {target.name} takes an additional {bonus} damage!")
        
        if effect:
            target.stats['effect'] = effect
            print(f"{target.name} is now affected by {effect}!")
            
        return True

class FriendlyTeam:
    def __init__(self, members):
        self.members = members
        self.active_member_index = 0
        self.fallen_rangers = []  # Track defeated rangers
    
    def get_active_member(self):
        """Get the currently active team member"""
        return self.members[self.active_member_index]
    
    def next_member(self):
        """Switch to the next active member"""
        self.active_member_index = (self.active_member_index + 1) % len(self.members)
        # Skip defeated members
        while self.members[self.active_member_index].stats['hp'] <= 0:
            self.active_member_index = (self.active_member_index + 1) % len(self.members)
            # If we looped through all members and they're all defeated, break
            if self.active_member_index == 0:
                break
    
    def is_defeated(self):
        """Check if the entire team is defeated"""
        return all(member.stats['hp'] <= 0 for member in self.members)
    
    def heal_all(self, amount):
        """Heal all team members"""
        for member in self.members:
            if member.stats['hp'] > 0:  # Only heal living members
                member.stats['hp'] = min(member.stats['hp'] + amount, 100)  # Cap at 100 HP
                print(f"{member.name} healed for {amount} HP. Now at {member.stats['hp']} HP!")

class PlayerCharacter(CombatParticipant):
    def take_turn(self, enemy, team):
        """Handle player character's turn"""
        if self.stats['effect'] == 'stun':
            print(f"{self.name} is stunned and skips their turn!")
            self.stats['effect'] = 0  # Reset stun after skipping
            return
        
        # Display available skills
        print(f"\n{self.name}'s turn! Available skills:")
        for skill in self.skills:
            print(f"- {skill['name']} ({skill['description']}, Cost: {skill['breath_cost']} breath)")
        
        print(f"Current Breath: {self.stats['Breath']}")
        
        # Special "last stand" power boost for Green Ranger when allies are fallen
        if "Green" in self.name and len(team.fallen_rangers) >= 2 and team.fallen_rangers and random.random() < 0.3:
            print("\n╔═════════════════════════════╗")
            print("║        POWER SURGE!         ║")
            print("╚═════════════════════════════╝")
            print("Your anger at seeing your teammates fall triggers something deep within...")
            print("A surge of power flows through your suit, temporarily boosting your stats!")
            
            # Apply temporary boost
            self.stats['Hands'] += 2
            self.stats['Spine'] += 2
            self.stats['Breath'] += 1
            
            print(f"Hands +2 (Now {self.stats['Hands']})")
            print(f"Spine +2 (Now {self.stats['Spine']})")
            print(f"Breath +1 (Now {self.stats['Breath']})")
        
        valid_move = False
        
        while not valid_move:
            if self.is_player:
                intent = input(f"\nEnter your move: ").strip().lower()
            else:
                # AI teammates make decisions
                if self.stats['Breath'] < 2:
                    intent = "breathe"  # Build breath if low
                elif enemy.stats['hp'] < 100 and self.name == "Red Ranger":
                    intent = "heat wave"  # Finish off with strong attack
                elif "Yellow" in self.name and any(m.stats['hp'] < 40 and m.stats['hp'] > 0 for m in team.members):
                    intent = "field repair"  # Heal when teammates low
                elif "Pink" in self.name and self.stats['Breath'] >= 2:
                    intent = "acrobatic strike"  # Use signature move
                elif self.stats['Breath'] >= 3 and "Green" in self.name:
                    intent = "earth shatter"  # Use ultimate when possible
                else:
                    # Basic attacks
                    intent = random.choice(["punch", "kick"]) if self.stats['Breath'] >= 1 else "breathe"
                
                print(f"{self.name} chooses to use {intent.upper()}!")
                time.sleep(0.5)
            
            # Special case for Yellow Ranger's heal
            if intent.lower() in ["field repair", "group heal"] and "Yellow" in self.name:
                if self.use_skill(intent, None) == "group_heal":
                    team.heal_all(20)  # Heal all team members for 20 HP
                    valid_move = True
            # Special case for analyze
            elif intent.lower() == "analyze" and "Yellow" in self.name:
                print(f"{self.name} analyzes {enemy.name}'s weaknesses!")
                print(f"Weakness identified: {enemy.name} is vulnerable to coordinated attacks!")
                print(f"The next attack from any ranger will do +20% damage!")
                self.stats['Breath'] -= 1
                # Flag the enemy as analyzed
                enemy.stats['analyzed'] = True
                valid_move = True
            else:
                # Regular attack
                result = self.use_skill(intent, enemy)
                
                # If the enemy was analyzed, do bonus damage
                if result and enemy.stats.get('analyzed', False):
                    bonus_damage = int(0.2 * enemy.stats['hp'])  # Bonus damage based on remaining HP
                    enemy.stats['hp'] -= bonus_damage
                    print(f"COORDINATED ATTACK! {self.name} exploits the weakness for an additional {bonus_damage} damage!")
                    # Reset the analyzed flag
                    enemy.stats['analyzed'] = False
                
                valid_move = result
            
            if not valid_move:
                if self.is_player:
                    print("Try again with a valid move.")
                else:
                    # NPC rangers don't get stuck in loops
                    self.breath_action()
                    valid_move = True

class Enemy(CombatParticipant):
    def take_turn(self, team):
        """Handle enemy's turn attacking the team"""
        if self.stats['effect'] == 'stun':
            print(f"{self.name} is stunned and skips their turn!")
            self.stats['effect'] = 0  # Reset stun after skipping
            return
        
        # Filter skills the enemy can use based on breath
        available_skills = [skill for skill in self.skills 
                           if self.stats['Breath'] >= skill['breath_cost']]
        
        if not available_skills:
            # If no skills available, breathe
            self.breath_action()
            return
        
        # Define death messages here to ensure they're in scope
        death_messages = {
            "Red Ranger": "Red Ranger falls to one knee, his suit sparking with damage. 'Keep... fighting...' he gasps before collapsing. His transformation fails, leaving him unconscious.",
            "Pink Ranger": "Pink Ranger attempts a backflip to dodge, but Baby-Green's attack catches her mid-air. She crashes to the ground, her suit flickering before powering down. She's out of the fight.",
            "Yellow Ranger": "Yellow Ranger's tech systems overload from the damage. 'My calculations were... off...' he mutters before falling. His visor goes dark as he hits the ground.",
            "Green Ranger (You)": "You feel your power fading as the damage overwhelms your suit's systems. The world spins around you as you fall to the ground, your transformation failing."
        }
        
        # Choose skill based on situation
        # Baby-Green gets smarter as its health decreases
        if self.stats['hp'] < 500 and 'Acid Spray' in [s['name'] for s in available_skills]:
            # When below half health, prefer area attacks
            chosen_skill = next((s for s in available_skills if s['name'] == 'Acid Spray'), random.choice(available_skills))
            print(f"\n{self.name}'s eyes glow with toxic rage as it prepares a massive attack!")
            time.sleep(0.5)
            
            # Area attack hits all living team members
            living_members = [member for member in team.members if member.stats['hp'] > 0]
            print(f"{self.name} unleashes a spray of corrosive acid across the battlefield!")
            self.stats['Breath'] -= chosen_skill['breath_cost']
            
            # Calculate and apply damage to all team members
            damage = self.calculate_damage('Brain', 2, 10)
            for member in living_members:
                member.stats['hp'] -= damage
                print(f"{member.name} is hit for {damage} damage by the acid spray!")
                
                # Check if this attack defeated any rangers
                if member.stats['hp'] <= 0:
                    print(f"\n{death_messages[member.name]}")
                    team.fallen_rangers.append(member.name)
            
            return
        
        elif self.stats['hp'] < 300 and 'Regenerate' in [s['name'] for s in available_skills] and random.random() < 0.4:
            # When severely damaged, may choose to heal
            chosen_skill = next((s for s in available_skills if s['name'] == 'Regenerate'), None)
            if chosen_skill:
                print(f"\n{self.name}'s wounds begin to bubble and mend themselves!")
                self.stats['Breath'] -= chosen_skill['breath_cost']
                heal_amount = 30
                self.stats['hp'] += heal_amount
                print(f"{self.name} regenerates {heal_amount} HP! Current HP: {self.stats['hp']}")
                return
        
        # Default: choose a target and attack
        chosen_skill = random.choice(available_skills)
        
        # Choose a random living team member to attack, preferring the Green Ranger
        living_members = [member for member in team.members if member.stats['hp'] > 0]
        if not living_members:
            return  # No living members to attack
        
        # 30% chance to target Green Ranger if alive
        green_ranger = next((member for member in living_members if "Green" in member.name), None)
        if green_ranger and random.random() < 0.3:
            target = green_ranger
            print(f"\n{self.name} focuses its attention on you specifically!")
        else:
            target = random.choice(living_members)
        
        print(f"{self.name} uses {chosen_skill['name']} on {target.name}!")
        
        # Apply the attack
        if chosen_skill['name'] == 'Toxic Punch':
            damage = self.calculate_damage('Hands', 1, 8)
            target.stats['hp'] -= damage
            print(f"{target.name} takes {damage} damage from the toxic punch!")
            print(f"The toxin seeps into {target.name}'s suit, causing additional damage over time!")
            
        elif chosen_skill['name'] == 'Stomp':
            damage = self.calculate_damage('Legs', 1, 12)
            target.stats['hp'] -= damage
            target.stats['effect'] = 'stun'
            print(f"{target.name} takes {damage} damage and is STUNNED by the powerful stomp!")
            
        elif chosen_skill['name'] == 'Breathe':
            self.breath_action()
            
        else:
            # Generic skill use
            self.use_skill(chosen_skill['name'], target)
        
        # Check if this attack defeated the target
        if target.stats['hp'] <= 0:
            print(f"\n{death_messages[target.name]}")
            team.fallen_rangers.append(target.name)

def display_team_status(team, enemy):
    """Display current status of team and enemy"""
    print("\n╔═════════════════════ STATUS ═════════════════════╗")
    print(f"ENEMY: {enemy.name} - HP: {enemy.stats['hp']} - Breath: {enemy.stats['Breath']}")
    
    if enemy.stats['hp'] < 300:
        print("ENEMY STATUS: SEVERELY DAMAGED (HP < 300)")
    elif enemy.stats['hp'] < 500:
        print("ENEMY STATUS: DAMAGED (HP < 500)")
    elif enemy.stats['hp'] < 800:
        print("ENEMY STATUS: SLIGHTLY DAMAGED (HP < 800)")
    else:
        print("ENEMY STATUS: HEALTHY")
    
    print("\nRANGER TEAM:")
    for member in team.members:
        status = "▶ ACTIVE" if member == team.get_active_member() else "WAITING"
        if member.stats['hp'] <= 0:
            status = "DEFEATED"
            hp_display = "0"
        else:
            hp_percent = (member.stats['hp'] / 150) * 100  # 150 is max possible HP
            if hp_percent > 75:
                hp_display = f"{member.stats['hp']} (GOOD)"
            elif hp_percent > 40:
                hp_display = f"{member.stats['hp']} (DAMAGED)"
            else:
                hp_display = f"{member.stats['hp']} (CRITICAL)"
        
        print(f"  {member.name:<15} - HP: {hp_display:<15} - Breath: {member.stats['Breath']} - {status}")
    
    print("╚═════════════════════════════════════════════════╝")

def main():
    # Initialize team members with different stat distributions (color-coded rangers)
    
    # Red Ranger - High Spine and HP (Tank)
    red_stats = {
        'Brain': 4,
        'Spine': 10,
        'Eyes': 3,
        'Hands': 8,
        'Legs': 5,
        'Breath': 1,
        'hp': 150,
        'effect': 0
    }
    
    red_skills = [
        {'name': 'Punch', 'description': 'Hands*(0-6) dmg', 'breath_cost': 1},
        {'name': 'Shove', 'description': 'Stun enemy, no dmg', 'breath_cost': 0},
        {'name': 'Heat Wave', 'description': 'Spine*(2-16) dmg, applies burn', 'breath_cost': 2},
        {'name': 'Breathe', 'description': 'Gain 1 breath', 'breath_cost': 0}
    ]
    
    # Pink Ranger - Agile fighter with balanced stats
    pink_stats = {
        'Brain': 5,
        'Spine': 6,
        'Eyes': 7,
        'Hands': 8,
        'Legs': 9,
        'Breath': 1,
        'hp': 110,
        'effect': 0
    }
    
    pink_skills = [
        {'name': 'Punch', 'description': 'Hands*(0-6) dmg', 'breath_cost': 1},
        {'name': 'Kick', 'description': 'Legs*(0-10) dmg', 'breath_cost': 1},
        {'name': 'Acrobatic Strike', 'description': 'Legs*(4-12) dmg, can dodge next attack', 'breath_cost': 2},
        {'name': 'Breathe', 'description': 'Gain 1 breath', 'breath_cost': 0}
    ]
    
    # Yellow Ranger - Tech specialist with high Brain
    yellow_stats = {
        'Brain': 10,
        'Spine': 4,
        'Eyes': 8,
        'Hands': 5,
        'Legs': 5,
        'Breath': 1,
        'hp': 90,
        'effect': 0
    }
    
    yellow_skills = [
        {'name': 'Tech Blast', 'description': 'Brain*(3-12) dmg', 'breath_cost': 2},
        {'name': 'Analyze', 'description': 'Reveals enemy weakness', 'breath_cost': 1},
        {'name': 'Field Repair', 'description': 'Heal all teammates for 20 HP', 'breath_cost': 3},
        {'name': 'Breathe', 'description': 'Gain 1 breath', 'breath_cost': 0}
    ]
    
    # Green Ranger (You) - Balanced but powerful
    green_stats = {
        'Brain': 7,
        'Spine': 7,
        'Eyes': 7,
        'Hands': 7,
        'Legs': 7,
        'Breath': 2,  # Starts with more breath
        'hp': 120,
        'effect': 0
    }
    
    green_skills = [
        {'name': 'Punch', 'description': 'Hands*(0-6) dmg', 'breath_cost': 1},
        {'name': 'Kick', 'description': 'Legs*(0-10) dmg', 'breath_cost': 1},
        {'name': 'Earth Shatter', 'description': 'Spine*(3-14) dmg, stuns enemy', 'breath_cost': 3},
        {'name': 'Breathe', 'description': 'Gain 1 breath', 'breath_cost': 0}
    ]
    
    # Create team members (color-coded rangers)
    red_ranger = PlayerCharacter("Red Ranger", red_stats, red_skills, is_player=False)
    pink_ranger = PlayerCharacter("Pink Ranger", pink_stats, pink_skills, is_player=False)
    yellow_ranger = PlayerCharacter("Yellow Ranger", yellow_stats, yellow_skills, is_player=False)
    green_ranger = PlayerCharacter("Green Ranger (You)", green_stats, green_skills, is_player=True)
    
    # Create team
    ranger_team = FriendlyTeam([green_ranger, red_ranger, pink_ranger, yellow_ranger])
    
    # Initialize Baby-Green enemy with 999 HP
    baby_green_stats = {
        'Brain': 9,
        'Spine': 10,
        'Eyes': 7,
        'Hands': 9,
        'Legs': 8,
        'Breath': 3,  # Starts with extra breath
        'hp': 999,
        'effect': 0,
        'portrait': 'baby_green.png'
    }
    
    baby_green_skills = [
        {'name': 'Toxic Punch', 'description': 'Hands*(1-8) dmg + poison', 'breath_cost': 1},
        {'name': 'Stomp', 'description': 'Legs*(1-12) dmg + stun', 'breath_cost': 2},
        {'name': 'Acid Spray', 'description': 'Brain*(2-10) dmg to all rangers', 'breath_cost': 3},
        {'name': 'Regenerate', 'description': 'Heal 30 HP', 'breath_cost': 2},
        {'name': 'Breathe', 'description': 'Gain 1 breath', 'breath_cost': 0}
    ]
    
    # Create Baby-Green enemy
    baby_green = Enemy("Baby-Green", baby_green_stats, baby_green_skills)
    
    # Combat loop
    turn = 0
    victory = False
    defeat = False
    escape_route = None  # Will be set to "air" or "land" if player survives
    
    print("\n╔══════════════════════════════════════╗")
    print("║           MINT BATTLEFIELD          ║")
    print("║ Rangers vs The Menacing Baby-Green  ║")
    print("╚══════════════════════════════════════╝\n")
    
    time.sleep(1)
    print("The Seoul skyline glimmers in the distance as your team approaches the Mint facility.")
    time.sleep(1)
    print("After rescuing Blue from the cult at the school, your team received an emergency alert...")
    time.sleep(1)
    print("A toxic monstrosity has emerged from the chemical waste near the Mint.")
    time.sleep(1)
    print("As you arrive at the scene, the ground trembles with each massive step of the creature.")
    time.sleep(1)
    print("Baby-Green - a hulking, acid-dripping abomination - turns toward your team...")
    time.sleep(1)
    print("Red Ranger steps forward: 'Remember your training. We can take this thing down together!'")
    time.sleep(1)
    print("You all activate your morphers in unison. It's time to fight!")
    
    # Main combat loop
    while not (victory or defeat):
        turn += 1
        print(f"\n--- Turn {turn} ---")
        
        # Display status
        display_team_status(ranger_team, baby_green)
        
        # Checkpoint for testing
        print("\n[CHECKPOINT] Beginning of turn")
        
        # Active team member's turn
        active_member = ranger_team.get_active_member()
        print(f"\n{active_member.name}'s turn!")
        active_member.take_turn(baby_green, ranger_team)
        
        # Check if enemy is defeated
        if baby_green.stats['hp'] <= 0:
            victory = True
            continue
        
        # Checkpoint for testing
        print("\n[CHECKPOINT] After player turn")
        
        # Enemy's turn
        print(f"\n{baby_green.name}'s turn!")
        baby_green.take_turn(ranger_team)
        
        # Check if team is defeated
        if ranger_team.is_defeated():
            defeat = True
            continue
        
        # Move to next team member
        ranger_team.next_member()
        
        # Checkpoint for testing
        print("\n[CHECKPOINT] End of turn")
        
        # Dramatic pause for last ranger standing
        if len([m for m in ranger_team.members if m.stats['hp'] > 0]) == 1:
            last_ranger = next(m for m in ranger_team.members if m.stats['hp'] > 0)
            if "Green" in last_ranger.name and turn % 3 == 0:
                print("\n╔═════════════════════════════════════╗")
                print("║        LAST RANGER STANDING         ║")
                print("╚═════════════════════════════════════╝")
                print(f"You stand alone against {baby_green.name}, your teammates fallen around you.")
                print("With grim determination, you prepare for what might be your final attack.")
                time.sleep(1)
        
        # Small delay between turns for readability
        time.sleep(0.5)
    
    # End of combat
    if victory:
        print("\n╔═════════════════════════════╗")
        print("║         VICTORY!           ║")
        print("╚═════════════════════════════╝")
        
        # Determine which rangers survived
        survivors = [m.name for m in ranger_team.members if m.stats['hp'] > 0]
        fallen = ranger_team.fallen_rangers
        
        if "Green Ranger (You)" in survivors:
            print(f"Despite {baby_green.name}'s immense power, you managed to defeat it!")
            
            # If player is the only survivor
            if len(survivors) == 1:
                print("You stand alone in victory, your teammates having sacrificed themselves in battle.")
                print("Their powers weren't enough, but yours proved to be the monster's undoing.")
            else:
                survivor_names = ", ".join([name for name in survivors if name != "Green Ranger (You)"])
                print(f"You and {survivor_names} stand victorious over the fallen monster.")
            
            # Escape decision
            print("\nWith the battle won but casualties taken, you must decide how to return:")
            time.sleep(1)
            while escape_route is None:
                choice = input("\nWill you return by AIR or by LAND? ").lower().strip()
                if choice in ["air", "land"]:
                    escape_route = choice
                    print(f"\nYou decide to return by {escape_route.upper()}.")
                    if escape_route == "air":
                        print("Calling your Zords, you quickly airlift your fallen teammates and escape the contaminated zone.")
                    else:
                        print("You carefully navigate the difficult terrain, carrying your fallen teammates to safety.")
                else:
                    print("Please choose either AIR or LAND.")
        else:
            print("Your team has defeated the monster, but at a great cost...")
            print("You lie defeated, your consciousness fading, but your teammates completed the mission.")
            print("The last thing you see is the monster falling as your remaining teammates stand victorious.")
            escape_route = "emergency"
        
        return "victory"
        
    else:
        print("\n╔═════════════════════════════╗")
        print("║         DEFEAT!            ║")
        print("╚═════════════════════════════╝")
        
        print(f"{baby_green.name} has proven too powerful for your team...")
        
        # Check if Green Ranger was last to fall
        if ranger_team.fallen_rangers and ranger_team.fallen_rangers[-1] == "Green Ranger (You)":
            print("You fought valiantly to the very end, but even your powers weren't enough.")
            print("As your vision fades, you see Baby-Green lumbering toward the city...")
            print("The mission has failed, but perhaps reinforcements will arrive in time.")
        else:
            print("You watch helplessly as your last teammate falls to the monster's attacks.")
            print("Unable to continue the fight, darkness closes in around you.")
        
        return "defeat"

if __name__ == '__main__':
    result = main()
    print(f"Combat result: {result}")
    if result == "victory":
        print("\nYou've completed the Mint mission and defeated Baby-Green!")
        print("Return to Ranger HQ for debriefing and to plan your next move.")
    else:
        print("\nGAME OVER")
        print("Tip: Try coordinating your team's attacks better and use breath management strategically.")