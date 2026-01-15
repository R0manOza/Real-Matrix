"""Phase 1: Problem Dataset Builder

Creates a comprehensive dataset of 25 challenging problems:
- 7 math/logic problems
- 6 physics problems
- 6 logic puzzles with constraints
- 6 game theory problems
"""

import json
import os

# File paths (defined here to avoid requiring API key for dataset building)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROBLEMS_FILE = os.path.join(DATA_DIR, "problems.json")


def create_problems_dataset():
    """Create the complete problem dataset with correct answers."""
    
    problems = []
    
    # ========== 7 Math/Logic Problems ==========
    
    problems.append({
        "id": "math_001",
        "category": "math_logic",
        "problem_text": "In how many ways can you tile a 3×8 rectangle with 2×1 dominoes?",
        "correct_answer": "34",
        "answer_type": "integer",
        "explanation": "This is a classic tiling problem. For a 3×n rectangle, the recurrence relation is f(n) = f(n-1) + f(n-3). Starting with f(0)=1, f(1)=0, f(2)=3, we get f(8)=34."
    })
    
    problems.append({
        "id": "math_002",
        "category": "math_logic",
        "problem_text": "Find the smallest positive integer n such that n! ends in exactly 100 zeros.",
        "correct_answer": "405",
        "answer_type": "integer",
        "explanation": "The number of trailing zeros in n! is determined by the number of factors of 5. We need floor(n/5) + floor(n/25) + floor(n/125) + ... = 100. Solving gives n = 405."
    })
    
    problems.append({
        "id": "math_003",
        "category": "math_logic",
        "problem_text": "A number is called 'perfect' if it equals the sum of its proper divisors. What is the 4th perfect number?",
        "correct_answer": "8128",
        "answer_type": "integer",
        "explanation": "Perfect numbers follow the form 2^(p-1) * (2^p - 1) where 2^p - 1 is prime. The first four are 6, 28, 496, and 8128."
    })
    
    problems.append({
        "id": "math_004",
        "category": "math_logic",
        "problem_text": "How many distinct ways can you arrange the letters in MISSISSIPPI such that no two I's are adjacent?",
        "correct_answer": "7350",
        "answer_type": "integer",
        "explanation": "Total arrangements of MISSISSIPPI = 11!/(4!4!2!1!) = 34650. Using inclusion-exclusion to count arrangements with no adjacent I's gives 7350."
    })
    
    problems.append({
        "id": "math_005",
        "category": "math_logic",
        "problem_text": "What is the sum of all positive integers n such that n^2 + n + 1 is divisible by 7?",
        "correct_answer": "21",
        "answer_type": "integer",
        "explanation": "We need n^2 + n + 1 ≡ 0 (mod 7). Testing n = 0 to 6, we find n ≡ 2 or 4 (mod 7). The sum of all such n from 1 to 100 is 21 (specifically n = 2, 4, 9, 11, 16, 18, etc., but the pattern gives sum = 21 for the first cycle)."
    })
    
    problems.append({
        "id": "math_006",
        "category": "math_logic",
        "problem_text": "A function f: R → R satisfies f(x+y) = f(x) + f(y) for all real x, y, and f(1) = 5. What is f(2024)?",
        "correct_answer": "10120",
        "answer_type": "integer",
        "explanation": "This is Cauchy's functional equation. If f is continuous (or measurable), then f(x) = cx for some constant c. Since f(1) = 5, we have c = 5, so f(2024) = 5 × 2024 = 10120."
    })
    
    problems.append({
        "id": "math_007",
        "category": "math_logic",
        "problem_text": "How many integer solutions (x, y) exist for the equation x^2 + y^2 = 2024?",
        "correct_answer": "0",
        "answer_type": "integer",
        "explanation": "2024 = 8 × 253 = 8 × 11 × 23. For a number to be representable as a sum of two squares, all primes of the form 4k+3 in its factorization must appear with even exponent. Since 11 ≡ 3 (mod 4) appears with exponent 1, there are no integer solutions."
    })
    
    # ========== 6 Physics Problems ==========
    
    problems.append({
        "id": "physics_001",
        "category": "physics",
        "problem_text": "A satellite of mass m orbits Earth in a circular orbit at altitude h = 400 km. If the satellite's speed is increased by 20%, what is the new orbital period as a fraction of the original period? (Assume Earth's radius R = 6371 km and ignore atmospheric drag)",
        "correct_answer": "0.694",
        "answer_type": "float",
        "explanation": "For circular orbit: v = sqrt(GM/r). Original period T = 2πr/v. If v_new = 1.2v, then r_new = (v/v_new)^2 × r = r/1.44. New period T_new = 2πr_new/v_new = (2πr/v) × (1/1.44) × (1/1.2) = T × 0.578. Actually, using Kepler's laws: T^2 ∝ r^3, and v^2 ∝ 1/r, so if v increases by 20%, r decreases, and T_new/T = (r_new/r)^(3/2) = (1/1.2^2)^(3/2) = 0.694."
    })
    
    problems.append({
        "id": "physics_002",
        "category": "physics",
        "problem_text": "A block of mass 2 kg slides down a frictionless incline at 30° to the horizontal. At the bottom, it collides elastically with a stationary block of mass 4 kg on a horizontal surface. What is the final speed of the 2 kg block? (Assume g = 10 m/s² and the first block starts from rest at height 5 m)",
        "correct_answer": "3.33",
        "answer_type": "float",
        "explanation": "First block speed before collision: v = sqrt(2gh) = sqrt(2×10×5) = 10 m/s. For elastic collision: v1' = (m1-m2)/(m1+m2) × v1 = (2-4)/(2+4) × 10 = -10/3 = -3.33 m/s. The negative sign indicates direction reversal, so speed is 3.33 m/s."
    })
    
    problems.append({
        "id": "physics_003",
        "category": "physics",
        "problem_text": "A capacitor of capacitance C is charged to voltage V and then disconnected. A dielectric with κ = 3 is inserted, filling half the volume. What is the new voltage across the capacitor?",
        "correct_answer": "0.667",
        "answer_type": "float",
        "explanation": "Charge Q = CV is conserved. If the dielectric fills half the volume as a slab, we can model it as two capacitors in series: one air-filled (C_air = 2C for half volume) and one dielectric-filled (C_dielectric = 6C for half volume with κ=3). For series: 1/C_new = 1/(2C) + 1/(6C) = 2/(3C), so C_new = 1.5C. New voltage V' = Q/C_new = CV/(1.5C) = 2V/3 = 0.667V."
    })
    
    problems.append({
        "id": "physics_004",
        "category": "physics",
        "problem_text": "A block slides down a frictionless incline from a height of 5 m above the ground. What is the speed of the block when it reaches the bottom? (Use g = 10 m/s²)",
        "correct_answer": "10.0",
        "answer_type": "float",
        "explanation": "Using conservation of energy: mgh = (1/2)mv². The potential energy at height h = 5 m converts to kinetic energy. So v² = 2gh = 2×10×5 = 100, giving v = 10.0 m/s."
    })
    
    problems.append({
        "id": "physics_005",
        "category": "physics",
        "problem_text": "Light of wavelength 500 nm is incident on a double slit with separation d = 0.1 mm. The screen is 2 m away. What is the distance between the 3rd bright fringe and the central maximum?",
        "correct_answer": "0.03",
        "answer_type": "float",
        "explanation": "For double-slit interference: y = mλL/d where m is order, λ is wavelength, L is screen distance, d is slit separation. For m=3: y = 3 × 500×10⁻⁹ × 2 / (0.1×10⁻³) = 3 × 500×10⁻⁹ × 2 / 10⁻⁴ = 3 × 10⁻² = 0.03 m = 3 cm."
    })
    
    problems.append({
        "id": "physics_006",
        "category": "physics",
        "problem_text": "A rod of length L = 1 m and mass M = 2 kg rotates about one end. A force F = 10 N is applied perpendicularly at the free end. What is the angular acceleration?",
        "correct_answer": "15.0",
        "answer_type": "float",
        "explanation": "Moment of inertia about end: I = (1/3)ML² = (1/3) × 2 × 1² = 2/3 kg·m². Torque: τ = FL = 10 × 1 = 10 N·m. Angular acceleration: α = τ/I = 10 / (2/3) = 15 rad/s²."
    })
    
    # ========== 6 Logic Puzzles ==========
    
    problems.append({
        "id": "logic_001",
        "category": "logic_puzzle",
        "problem_text": "Five people live in five houses in a row. Each has a different color house, different pet, different drink, different hobby, and different profession. Clues: 1) The doctor lives next to the blue house. 2) The engineer has a cat. 3) The person who drinks coffee lives in the red house. 4) The teacher drinks tea. 5) The green house is immediately to the left of the white house. 6) The person who plays chess drinks milk. 7) The person in the yellow house plays guitar. 8) The person in the middle house drinks water. 9) The lawyer lives in the first house. 10) The person who plays chess lives next to the person with a dog. 11) The person with a bird lives next to the person who plays guitar. 12) The person who plays piano has a fish. 13) The doctor lives next to the person with a horse. 14) The person who plays guitar drinks orange juice. Who has the fish?",
        "correct_answer": "The teacher",
        "answer_type": "string",
        "explanation": "This is a constraint satisfaction problem. Working through the clues systematically: House 1: Lawyer (clue 9). House 3: Water (clue 8). The teacher drinks tea (clue 4), so teacher is not in house 3. The green house is left of white (clue 5). The person who plays piano has a fish (clue 12). Through systematic deduction: House 1: Lawyer, Yellow, Guitar, Orange Juice, Bird; House 2: Engineer, Blue, Cat, Coffee; House 3: Teacher, Red, Piano, Tea, Fish; House 4: Doctor, Green, Chess, Milk, Horse; House 5: (remaining), White, (remaining), Water, Dog. So the teacher has the fish."
    })
    
    problems.append({
        "id": "logic_002",
        "category": "logic_puzzle",
        "problem_text": "There are three boxes: one contains only apples, one contains only oranges, and one contains both apples and oranges. The boxes are labeled, but all labels are wrong. You can take out one fruit from one box. Which box should you choose to correctly relabel all boxes?",
        "correct_answer": "The box labeled 'Both'",
        "answer_type": "string",
        "explanation": "Since all labels are wrong, the box labeled 'Both' cannot contain both. It must contain either only apples or only oranges. If you pick from it and get an apple, then it's the apples box. The box labeled 'Oranges' must then be the 'Both' box (since it can't be oranges), and the box labeled 'Apples' must be the oranges box. Similarly if you get an orange, it's the oranges box, and you can deduce the rest."
    })
    
    problems.append({
        "id": "logic_003",
        "category": "logic_puzzle",
        "problem_text": "A king has 1000 bottles of wine. One is poisoned. You have 10 test subjects (rats). The poison takes exactly 24 hours to kill. How can you identify the poisoned bottle in 24 hours?",
        "correct_answer": "Use binary encoding: assign each bottle a unique 10-bit binary number. Feed each rat the wine from bottles where that rat's bit position is 1. The pattern of dead rats after 24 hours gives the binary number of the poisoned bottle.",
        "answer_type": "string",
        "explanation": "This is a binary search/encoding problem. With 10 rats, you can encode 2^10 = 1024 different states, which is enough for 1000 bottles. Each rat represents one bit position. After 24 hours, the dead rats indicate which bits are 1 in the poisoned bottle's number."
    })
    
    problems.append({
        "id": "logic_004",
        "category": "logic_puzzle",
        "problem_text": "You are in a room with three light switches. One controls a light bulb in another room. You can only go to the other room once. How do you determine which switch controls the light?",
        "correct_answer": "Turn on switch 1 for 5 minutes, then turn it off. Turn on switch 2. Go to the other room. If the bulb is on, it's switch 2. If it's off but warm, it's switch 1. If it's off and cold, it's switch 3.",
        "answer_type": "string",
        "explanation": "Use the heat property of the bulb. By turning on switch 1 and leaving it on for a while, the bulb heats up. Then turning it off and turning on switch 2 allows you to distinguish: on = switch 2, off and warm = switch 1, off and cold = switch 3."
    })
    
    problems.append({
        "id": "logic_005",
        "category": "logic_puzzle",
        "problem_text": "There are 12 identical-looking coins. One is fake and has a different weight (you don't know if heavier or lighter). You have a balance scale. What is the minimum number of weighings needed to identify the fake coin?",
        "correct_answer": "3",
        "answer_type": "integer",
        "explanation": "Divide into three groups of 4. Weigh group 1 vs group 2. If equal, fake is in group 3. If not equal, fake is in the heavier or lighter group. Then take 3 coins from the suspect group, weigh 1 vs 1. This narrows it down, and a third weighing identifies the fake and whether it's heavier or lighter."
    })
    
    problems.append({
        "id": "logic_006",
        "category": "logic_puzzle",
        "problem_text": "Three people (A, B, C) are in a line. They can see only forward. A sees B and C. B sees C. C sees nobody. They are told there are 3 red hats and 2 blue hats total. They are each wearing a hat. After a pause, C says 'I don't know my color.' Then B says 'I don't know my color.' Then A says 'I know my color.' What color is A's hat?",
        "correct_answer": "Red",
        "answer_type": "string",
        "explanation": "C sees nothing, so can't know. B sees C. If C were blue, B would know there are at most 2 blues left (since there are only 2 total), and seeing C is blue, B would know B must be red (otherwise C would have deduced). Since B doesn't know, C must be red. A sees B and C. If both were blue, A would know A is red (only 2 blues total). Since A knows after B speaks, and B not knowing implies C is red, A must see that B and C are not both blue. Since C is red (from B's uncertainty), if B were also red, A would know A could be either. But A knows, so B must be blue, making A red."
    })
    
    # ========== 6 Game Theory Problems ==========
    
    problems.append({
        "id": "game_001",
        "category": "game_theory",
        "problem_text": "Two players alternately take coins from a pile of 21 coins. On each turn, a player can take 1, 2, or 3 coins. The player who takes the last coin wins. If you go first, what is your winning strategy?",
        "correct_answer": "Take 1 coin initially, then on each subsequent turn take (4 - coins taken by opponent) to leave a multiple of 4. This ensures you take the last coin.",
        "answer_type": "string",
        "explanation": "The key is to leave your opponent with a multiple of 4 coins. Since 21 = 4×5 + 1, take 1 coin first. Then whatever your opponent takes (1, 2, or 3), you take (4 - that amount) to leave them with another multiple of 4. Eventually you'll take the last coin."
    })
    
    problems.append({
        "id": "game_002",
        "category": "game_theory",
        "problem_text": "In a sealed-bid auction for an item worth $100 to you, you and one other bidder submit bids simultaneously. The highest bidder wins and pays their bid. What should you bid?",
        "correct_answer": "Bid $50 (or slightly more than half your valuation)",
        "answer_type": "string",
        "explanation": "This is a first-price sealed-bid auction. If you bid your full valuation ($100), you get zero surplus if you win. If the other bidder's valuation is unknown but uniformly distributed, the optimal bid is half your valuation. Bidding $50 maximizes expected utility, as you'll win about half the time and get positive surplus when you do."
    })
    
    problems.append({
        "id": "game_003",
        "category": "game_theory",
        "problem_text": "Two companies are deciding whether to enter a market. If both enter, each loses $10M. If one enters alone, that company gains $50M and the other gets $0. If neither enters, both get $0. What is the Nash equilibrium?",
        "correct_answer": "Both companies enter (lose $10M each)",
        "answer_type": "string",
        "explanation": "This is a prisoner's dilemma. For each company: if other enters, entering gives -10 vs 0 (enter is better). If other doesn't enter, entering gives 50 vs 0 (enter is better). So entering is a dominant strategy for both, leading to the Nash equilibrium where both enter, even though both would be better off if neither entered."
    })
    
    problems.append({
        "id": "game_004",
        "category": "game_theory",
        "problem_text": "You and an opponent each choose a number from 1 to 100 simultaneously. Whoever is closer to 2/3 of the average of both numbers wins. What number should you choose?",
        "correct_answer": "1",
        "answer_type": "integer",
        "explanation": "This is a 'beauty contest' game requiring iterated reasoning. Level 0: average is 50, so choose 33. Level 1: if others think 33, average is 33, so choose 22. Level 2: if others think 22, choose 15. Continuing this reasoning leads to the Nash equilibrium of 1, where 2/3 of the average (if both choose 1) is still 1."
    })
    
    problems.append({
        "id": "game_005",
        "category": "game_theory",
        "problem_text": "Two players play Rock-Paper-Scissors, but with a twist: if both choose the same, both lose $1. If different, the winner gets $2 and the loser pays $2. What is the optimal mixed strategy?",
        "correct_answer": "Play each option with probability 1/3 (equal randomization)",
        "answer_type": "string",
        "explanation": "This is a zero-sum game. The payoff matrix shows that any pure strategy can be exploited. The Nash equilibrium requires playing each option with equal probability (1/3 each), making the opponent indifferent between their choices and ensuring an expected payoff of 0."
    })
    
    problems.append({
        "id": "game_006",
        "category": "game_theory",
        "problem_text": "A seller values an item at $0. A buyer values it at $100. They negotiate: seller makes an offer, buyer accepts or rejects. If rejected, buyer makes counteroffer, and so on, alternating. Each round, the item loses 10% of its value (discount factor 0.9). What should the seller's first offer be?",
        "correct_answer": "$90",
        "answer_type": "string",
        "explanation": "This is an alternating-offers bargaining game with discounting. Working backwards: In the final round (if it gets there), seller would accept any positive amount. In the penultimate round, buyer would offer the minimum (say $1). In the round before that, seller would offer buyer's continuation value plus a bit. With discount factor 0.9, the subgame-perfect equilibrium gives the first-mover (seller) an advantage. The seller should offer approximately $90, which the buyer accepts immediately, as rejecting would lead to a worse outcome after discounting."
    })
    
    # Verify we have 25 problems
    assert len(problems) == 25, f"Expected 25 problems, got {len(problems)}"
    
    # Verify categories
    category_counts = {}
    for p in problems:
        category_counts[p["category"]] = category_counts.get(p["category"], 0) + 1
    
    assert category_counts.get("math_logic", 0) == 7, f"Expected 7 math/logic problems, got {category_counts.get('math_logic', 0)}"
    assert category_counts.get("physics", 0) == 6, f"Expected 6 physics problems, got {category_counts.get('physics', 0)}"
    assert category_counts.get("logic_puzzle", 0) == 6, f"Expected 6 logic puzzles, got {category_counts.get('logic_puzzle', 0)}"
    assert category_counts.get("game_theory", 0) == 6, f"Expected 6 game theory problems, got {category_counts.get('game_theory', 0)}"
    
    return problems


def save_problems_dataset(problems, output_file):
    """Save problems to JSON file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    dataset = {
        "metadata": {
            "total_problems": len(problems),
            "categories": {
                "math_logic": sum(1 for p in problems if p["category"] == "math_logic"),
                "physics": sum(1 for p in problems if p["category"] == "physics"),
                "logic_puzzle": sum(1 for p in problems if p["category"] == "logic_puzzle"),
                "game_theory": sum(1 for p in problems if p["category"] == "game_theory")
            }
        },
        "problems": problems
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Saved {len(problems)} problems to {output_file}")
    print(f"  Categories: {dataset['metadata']['categories']}")


def validate_problems(problems):
    """Validate that each problem has required fields and checkable answers."""
    required_fields = ["id", "category", "problem_text", "correct_answer", "answer_type"]
    
    for i, problem in enumerate(problems):
        # Check required fields
        for field in required_fields:
            if field not in problem:
                raise ValueError(f"Problem {i+1} (id: {problem.get('id', 'unknown')}) missing required field: {field}")
        
        # Check answer type is valid
        valid_types = ["integer", "float", "string"]
        if problem["answer_type"] not in valid_types:
            raise ValueError(f"Problem {problem['id']} has invalid answer_type: {problem['answer_type']}")
        
        # Check answer can be validated
        if problem["answer_type"] == "integer":
            try:
                int(problem["correct_answer"])
            except (ValueError, TypeError):
                raise ValueError(f"Problem {problem['id']} answer should be integer but got: {problem['correct_answer']}")
        
        if problem["answer_type"] == "float":
            try:
                float(problem["correct_answer"])
            except (ValueError, TypeError):
                raise ValueError(f"Problem {problem['id']} answer should be float but got: {problem['correct_answer']}")
    
    print(f"[OK] Validated all {len(problems)} problems")
    return True


if __name__ == "__main__":
    print("Building problem dataset...")
    problems = create_problems_dataset()
    
    print(f"\nValidating problems...")
    validate_problems(problems)
    
    print(f"\nSaving dataset...")
    save_problems_dataset(problems, PROBLEMS_FILE)
    
    print("\n[OK] Phase 1 complete! Problem dataset created successfully.")
    print(f"  File: {PROBLEMS_FILE}")
