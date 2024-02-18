from itertools import combinations
from deuces import Card, Evaluator
import random
from copy import deepcopy
from deuces import Deck


class PokerGame:
    def __init__(self, num_players, hole_cards):
        """
        Initialize a PokerGame instance.

        Parameters:
        - num_players: The number of players in the game.
        - hole_cards: Initial hole cards for the player.
        """
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['h', 'd', 'c', 's']
        
        self.deck = [rank + suit for rank in ranks for suit in suits]
        self.num_players = num_players
        self.players_hands = {"player1": hole_cards}  # Player's known initial hole cards
        self.opponents_hands = {f"player{i}": [] for i in range(2, num_players + 1)}  # Initialize opponents' hands
        self.board = list()
        self.burned_cards = list()
        self.evaluator = Evaluator()

    def deal_hole_cards(self):
        """
        Deal random hole cards to the player.
        """
        self.players_hands["player1"] = random.sample(self.deck, 2)
        self.deck = [card for card in self.deck if card not in self.players_hands["player1"]]

    def deal_opponent_hands(self):
        """
        Deal random hole cards to each opponent.
        """
        
        for player_name in self.opponents_hands:
            self.opponents_hands[player_name] = random.sample(self.deck, 2)
            self.deck = [card for card in self.deck if card not in self.opponents_hands[player_name]]
        return list(self.opponents_hands.values())



    def update_board(self, *args):
        """
        Update the game board with new cards.

        Parameters:
        - args: Cards to be added to the board.
        """

        for card in args:
            if card in self.deck:
                self.board.append(card)
                self.deck.remove(card)
            else:
                print(f"Error: Card {card} is not in the deck.")

    def new_game(self, num_players, hole_cards):
        """
        Start a new poker game.

        Parameters:
        - num_players: The number of players in the new game.
        - hole_cards: Initial hole cards for the player in the new game.
        """
        self.num_players = num_players
        self.players_hands = {"player1": hole_cards}
        self.opponents_hands = {f"player{i}": [] for i in range(2, num_players + 1)}
        self.deck = Deck()
        self.board = list()
        self.burned_cards = list()

    def simulate_remaining_game(self, opponent_hands):
        win_count = 0

        for _ in range(10000):
            remaining_deck = deepcopy(self.deck)
            remaining_board = deepcopy(self.board)
            remaining_burned = deepcopy(self.burned_cards)

            # Simulate remaining community cards
            for _ in range(5 - len(self.board) - len(self.burned_cards)):
                remaining_board.append(remaining_deck.pop())

            # Convert cards to valid integer representations
            all_community_cards = [Card.new(card) for card in remaining_board + remaining_burned]

            player_hand = [Card.new(card) for card in self.players_hands["player1"]]
            player_score = self.evaluator.evaluate(player_hand, all_community_cards)

            opponent_hands = [hand for hand in opponent_hands]
            opponent_scores = [self.evaluator.evaluate([Card.new(card) for card in hand], all_community_cards) for hand in opponent_hands]

            if all(player_score > score for score in opponent_scores):
                win_count += 1

        win_probability = win_count / 10000  # Total number of simulations
        return win_probability



    def calculate_win_probabilities(self):
        """
        Calculate the estimated winning probability for the player.

        Returns:
        The estimated winning probability.
        """
        if len(self.board) == 0 and len(self.burned_cards) == 0:
            # No community cards dealt yet
            return self.simulate_remaining_game(self.deal_opponent_hands())
        elif len(self.board) < 5:
            # Flop, Turn, or River stage
            return self.simulate_remaining_game(list(self.deal_opponent_hands().values()))
        else:
            # Showdown stage (all community cards dealt)
            return self.simulate_remaining_game(list(self.deal_opponent_hands().values()))


    def calculate_hand_probability(self, hand_type):
        """
        Calculate the estimated probability of hitting a specific hand at any point in the game.

        Parameters:
        - hand_type: The hand type (e.g., "pair", "flush").

        Returns:
        The estimated probability of hitting the specific hand.
        """

        evaluator = self.evaluator

        if hand_type not in evaluator.HAND_EVAL:
            print(f"Error: Invalid hand type '{hand_type}'. Please enter a valid hand type.")
            return None

        hand_type_score = evaluator.HAND_EVAL[hand_type]

        win_count = 0

        for _ in range(10000):
            remaining_deck = deepcopy(self.deck)
            remaining_board = deepcopy(self.board)
            remaining_burned = deepcopy(self.burned_cards)

            # Simulate remaining community cards
            for _ in range(5 - len(self.board) - len(self.burned_cards)):
                remaining_board.append(remaining_deck.pop())

            all_community_cards = remaining_board + [card for card in remaining_burned]

            player_score = self.evaluator.evaluate(self.players_hands["player1"], all_community_cards)

            opponent_hands = self.deal_opponent_hands()
            opponent_scores = [self.evaluator.evaluate(hand, all_community_cards) for hand in opponent_hands]

            if any(score >= hand_type_score for score in opponent_scores):
                win_count += 1

        probability = win_count / 10000
        return probability

    def reveal_card(self, card):
        """
        Add a card to the burned_cards field, simulating the revelation of a card.

        Parameters:
        - card: The card to be revealed.
        """
        if card in self.deck:
            self.burned_cards.append(card)
            self.deck.remove(card)
        else:
            print(f"Error: Card {card} is not in the deck.")

    def add_to_opponent_hand(self, player_name, card):
        """
        Add a card to the specified opponent's hand.

        Parameters:
        - player_name: The name of the opponent (e.g., "player1", "player2").
        - card: The card to be added to the opponent's hand.
        """
        if player_name in self.opponents_hands:
            if card in self.deck:
                self.opponents_hands[player_name].append(card)
                self.deck.remove(card)
            else:
                print(f"Error: Card {card} is not in the deck.")
        else:
            print(f"Error: Opponent {player_name} does not exist.")

    def get_beating_hands(self):
        beating_hands = []

        # Get all possible two-card combinations from the remaining deck
        for combo in combinations(self.deck.cards, 2):
            opponent_hand = list(combo) + self.board
            opponent_score = self.evaluator.evaluate(opponent_hand, self.board)

            player_hand = self.players_hands[0] + self.board
            player_score = self.evaluator.evaluate(player_hand, self.board)

            if opponent_score > player_score:
                beating_hands.append(list(combo))

        return beating_hands

    def print_beating_hands(self):
        beating_hands = self.get_beating_hands()

        if beating_hands:
            print("Two-card hands that would beat your current hand:")
            for hand in beating_hands:
                Card.print_pretty_cards(hand)
        else:
            print("There are no two-card hands that would beat your current hand.")

    def show_hands(self):
        """
        Display the hand rank for the player's hand.
        """
        player_hand = self.players_hands["player1"] + self.board
        player_score = self.evaluator.evaluate(player_hand, self.board)
        player_class = self.evaluator.get_rank_class(player_score)

        print(f"Player hand rank = {player_score} ({self.evaluator.class_to_string(player_class)})")


# game = PokerGame(4, ['As', '7d'])
# print(game.calculate_win_probabilities())

if __name__ == "__main__":
    num_players = int(input("Enter the number of players (2-15): "))
    hole_cards = input("Enter your hole cards (e.g., Ah 7d): ").split()

    game = PokerGame(num_players, hole_cards)

    while True:
        command = input("Enter command (newgame, flop, turn, river, calculatewin, calculatehit, revealed, addtoplayer, outs, showhands, help, exit): ").split()

        try:
            if command:
                if command[0] == "newgame":
                    if len(command) >= 2:
                        num_players = int(command[1])
                        hole_cards = input("Enter your hole cards (e.g., Ah 7d): ").split()
                        game.new_game(num_players, hole_cards)
                    else:
                        print("Error: Missing num_players argument for 'newgame' command.")
                elif command[0] in {"flop", "turn", "river"}:
                    if len(command) >= 4:
                        game.update_board(command[1], command[2], command[3])
                    else:
                        print(f"Error: Missing card arguments for '{command[0]}' command.")
                elif command[0] == "calculatewin":
                    win_prob = game.calculate_win_probabilities()
                    print(f"Estimated Winning Probability: {win_prob:.2%}")
                elif command[0] == "calculatehit":
                    hand_type = input("Enter hand type (pair, two_pair, three_of_a_kind, straight, flush, full_house, four_of_a_kind, straight_flush, royal_flush): ")
                    hand_prob = game.calculate_hand_probability(hand_type)
                    if hand_prob is not None:
                        print(f"Estimated Probability of Hitting {hand_type.capitalize()}: {hand_prob:.2%}")
                elif command[0] == "revealed":
                    if len(command) >= 2:
                        revealed_card = command[1]
                        game.reveal_card(revealed_card)
                    else:
                        print("Error: Missing card argument for 'revealed' command.")
                elif command[0] == "addtoplayer":
                    if len(command) >= 3:
                        player_name = command[1]
                        added_card = command[2]
                        game.add_to_opponent_hand(player_name, added_card)
                    else:
                        print("Error: Missing player_name or card argument for 'addtoplayer' command.")
                elif command[0] == "outs":
                    game.print_beating_hands()
                elif command[0] == "showhands":
                    game.show_hands()
                elif command[0] == "help":
                    header = "Available Commands"
                    print(f"{'=' * ((40 - len(header)) // 2)}{header}{'=' * ((40 - len(header)) // 2)}")
                    print("newgame <num_players>: Start a new poker game with the specified number of players.")
                    print("flop <card1> <card2> <card3>: Simulate the flop by adding three cards to the board.")
                    print("turn <card>: Simulate the turn by adding one card to the board.")
                    print("river <card>: Simulate the river by adding one card to the board.")
                    print("calculatewin: Calculate the estimated winning probability for the player.")
                    print("calculatehit: Calculate the estimated probability of hitting a specific hand.")
                    print("revealed <card>: Simulate the revelation of a card by adding it to the burned cards.")
                    print("addtoplayer <player_name> <card>: Add a card to the specified opponent's hand.")
                    print("outs: Print two-card hands that would beat the current hand.")
                    print("showhands: Display the hand rank for the player's hand.")
                    print("help: Display this help message.")
                    print("exit: Exit the program.")
                    print("=" * 40)

                elif command[0] == "exit":
                    break
                else:
                    print("Invalid command. Try again.")
            else:
                print("Please enter a command.")
        except Exception as e:
            print(f"Error: {e}")
