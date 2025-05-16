# combat.py

# Breath and Combat
# Moves cost breath. Breathing in and Out controls the flow of combat.

import random

# Stats:
#   Brain - Intelligence/strategic skills
#   Spine - Courage/willpower
#   Eyes - Perception/accuracy
#   Hands - Upper body strength/dexterity
#   Legs - Lower body strength/mobility
#   Breath - Resource for combat actions
#   HP - Health points

class CombatParticipant:
    def __init__(self, stats, skills, is_player=False):
        self.stats = stats
        self.skills = skills
        self.is_player = is_player
        
    def breath_action(self):
        """Increase breath by 1"""
        self.stats['Breath'] += 1
        print(f"{'You' if self.is_player else 'Enemy'} take a deep breath. Breath increased to {self.stats['Breath']}")
        return 0  # No damage
    
    def calculate_damage(self, stat, min_roll, max_roll):
        """Calculate damage based on stat and random roll"""
        stat_value = self.stats[stat]
        roll = random.randint(min_roll, max_roll)
        return stat_value * roll
    
    def use_skill(self, skill_name, target):
        """Use a skill on the target"""
        # Check if we have enough breath
        for skill in self.skills:
            if skill['name'].lower() == skill_name.lower():
                # Check breath cost
                if self.stats['Breath'] < skill['breath_cost']:
                    print(f"Not enough breath to use {skill['name']}!")
                    return False
                
                # Deduct breath cost
                self.stats['Breath'] -= skill['breath_cost']
                
                # Calculate damage
                damage = 0
                effect = None
                
                if skill['name'].lower() == 'punch':
                    damage = self.calculate_damage('Hands', 0, 6)
                elif skill['name'].lower() == 'kick':
                    damage = self.calculate_damage('Legs', 0, 10)
                elif skill['name'].lower() == 'shove':
                    # Shove applies stun but no damage
                    effect = 'stun'
                    target.stats['effect'] = effect
                elif skill['name'].lower() == 'breathe':
                    self.breath_action()
                    return True
                
                # Apply damage and effects
                if damage > 0:
                    target.stats['hp'] -= damage
                    print(f"{'You' if self.is_player else 'Enemy'} used {skill['name']} for {damage} damage!")
                
                if effect:
                    print(f"{'You' if self.is_player else 'Enemy'} applied {effect} effect!")
                    
                return True
        
        print(f"Skill '{skill_name}' not found!")
        return False

class Player(CombatParticipant):
    def take_turn(self, enemy):
        """Handle player's turn"""
        if self.stats['effect'] == 'stun':
            print("You are stunned and skip your turn!")
            self.stats['effect'] = 0  # Reset stun after skipping
            return
        
        # Display available skills
        print("\nYour turn! Available skills:")
        for skill in self.skills:
            print(f"- {skill['name']} ({skill['description']}, Cost: {skill['breath_cost']} breath)")
        
        print(f"Current Breath: {self.stats['Breath']}")
        valid_move = False
        
        while not valid_move:
            intent = input("\nEnter your move (punch, kick, shove, breathe): ").strip().lower()
            valid_move = self.use_skill(intent, enemy)
            
            if not valid_move:
                print("Try again with a valid move.")

class Enemy(CombatParticipant):
    def take_turn(self, player):
        """Handle enemy's turn"""
        if self.stats['effect'] == 'stun':
            print("Enemy is stunned and skips their turn!")
            self.stats['effect'] = 0  # Reset stun after skipping
            return
        
        # Filter skills the enemy can use based on breath
        available_skills = [skill for skill in self.skills 
                           if self.stats['Breath'] >= skill['breath_cost']]
        
        if not available_skills:
            # If no skills available, breathe
            self.breath_action()
            return
        
        # Random skill selection
        chosen_skill = random.choice(available_skills)
        print(f"Enemy uses {chosen_skill['name']}!")
        self.use_skill(chosen_skill['name'], player)

def main():
    # Initialize player stats and skills
    player_stats = {
        'Brain': 5,
        'Spine': 6,
        'Eyes': 4,
        'Hands': 7,
        'Legs': 6,
        'Breath': 1,
        'hp': 100,
        'effect': 0
    }
    
    player_skills = [
        {'name': 'Punch', 'description': 'Hands*(0-6) dmg', 'breath_cost': 1},
        {'name': 'Kick', 'description': 'Legs*(0-10) dmg', 'breath_cost': 1},
        {'name': 'Shove', 'description': 'Stun enemy, no dmg', 'breath_cost': 0},
        {'name': 'Breathe', 'description': 'Gain 1 breath', 'breath_cost': 0}
    ]
    
    # Initialize enemy stats and skills
    enemy_stats = {
        'Brain': 5,
        'Spine': 6,
        'Eyes': 4,
        'Hands': 7,
        'Legs': 6,
        'Breath': 1,
        'hp': 100,
        'effect': 0,
        'portrait': 'file_path'  # Placeholder for enemy portrait
    }
    
    enemy_skills = [
        {'name': 'Punch', 'description': 'Hands*(0-6) dmg', 'breath_cost': 1},
        {'name': 'Kick', 'description': 'Legs*(0-10) dmg', 'breath_cost': 1},
        {'name': 'Shove', 'description': 'Stun player, no dmg', 'breath_cost': 0},
        {'name': 'Breathe', 'description': 'Gain 1 breath', 'breath_cost': 0}
    ]
    
    # Create player and enemy
    player = Player(player_stats, player_skills, is_player=True)
    enemy = Enemy(enemy_stats, enemy_skills)
    
    # Combat loop
    turn = 0
    victory = False
    defeat = False
    
    print("Combat begins!")
    print("==============")
    
    # Main combat loop
    while not (victory or defeat):
        turn += 1
        print(f"\n--- Turn {turn} ---")
        print(f"Player HP: {player.stats['hp']} | Enemy HP: {enemy.stats['hp']}")
        print(f"Player Breath: {player.stats['Breath']} | Enemy Breath: {enemy.stats['Breath']}")
        
        # Checkpoint for testing
        print("\n[CHECKPOINT] Beginning of turn")
        
        # Player's turn
        player.take_turn(enemy)
        
        # Check if enemy is defeated
        if enemy.stats['hp'] <= 0:
            victory = True
            continue
        
        # Checkpoint for testing
        print("\n[CHECKPOINT] After player turn")
        
        # Enemy's turn
        enemy.take_turn(player)
        
        # Check if player is defeated
        if player.stats['hp'] <= 0:
            defeat = True
            continue
        
        # Checkpoint for testing
        print("\n[CHECKPOINT] End of turn")
    
    # End of combat
    if victory:
        print("\n=== VICTORY! ===")
        print("You have defeated the enemy!")
        return "victory"
    else:
        print("\n=== DEFEAT! ===")
        print("You have been defeated...")
        return "defeat"

if __name__ == '__main__':
    result = main()
    print(f"Combat result: {result}")
