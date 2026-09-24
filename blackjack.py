# Get properties and lists of possible cards, their suits, and their point values
from deck_of_cards import cards
import random
import time
import locale

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


def intro():
    print("Welcome to Blackjack! Ready to play?")
    if input("Press enter to continue...") == "":
        setup()
    else:
        print("Invalid input. Please try again.")
        intro()


def setup():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand, first_hand_final_value
    bank = 10.00
    bank_formatted = locale.currency(bank, grouping=True)
    bet = 0
    deck = list(cards.keys())
    player_cards = []
    dealer_cards = []
    player_hand_value = sum(cards[card] for card in player_cards)
    dealer_hand_value = sum(cards[card] for card in dealer_cards)

    first_split_hand = []
    second_split_hand = []
    first_hand_final_value = None

    start_and_deal()


def start_and_deal():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand, first_hand_final_value
    # Shuffle the deck
    print("Shuffling the deck...")
    random.shuffle(deck)
    time.sleep(2)

    # Ask how much the player wants to bet
    # Place bet and subtract bet from cash value
    update_bank_and_bet()
    if bank <= 0:
        print("You don't have any money left to play. Game over.")
        exit()

    bet = float(input("How much do you want to bet this round? \n$"))

    while bet > bank:
        print("You don't have enough money to place that bet. Try again.")
        bet = float(input("How much do you want to bet this round? \n$"))
    else:
        pass

    print("Placing bet...")
    bank -= bet
    time.sleep(1)
    update_bank_and_bet()
    time.sleep(1.5)

    # Deal initial cards
    print("\nDealing cards...")
    for _ in range(2):
        player_cards.append(deck.pop())
        dealer_cards.append(deck.pop())

    # update hand values
    update_hand_values()

    time.sleep(2)

    print(f"\nYour cards:", player_cards)
    print("Hand value:", player_hand_value)
    time.sleep(1)
    print("\nDealer's face-up card: ", dealer_cards[0])
    dealer_blackjack_check()
    insurance()

    time.sleep(1)

    player_turn()


def player_turn():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand, first_hand_final_value
    # Check for blackjack (21 points)
    if len(player_cards) == 2 and player_hand_value == 21:
        bank += bet * 2.5
        print("\nBlackjack! You win!")
        update_bank_and_bet()
        if first_split_hand != []:
            first_hand_final_value = 0
            second_hand_in_split()
        else:
            ask_play_again()

    # Ask the player what they want to do: 'hit', 'stay', or 'double' (if they have two of the same card)
    if len(player_cards) == 2 and cards[player_cards[0]] == cards[player_cards[1]]:
        action = input(
            "\nWhat do you want to do? Options: [(H)it|(S)tay|(D)ouble|(Sp)lit]: "
        ).lower()
    else:
        action = input("\nWhat do you want to do? Options: [(H)it|(S)tay|(D)ouble]: ").lower()

    # If 'hit', give the player another card and add it to their point value
    # If the point value is over 21, they bust, and it's game over. If not, ask 'hit' or 'stay' again.
    if action == "hit" or action == "h":
        player_cards.append(deck.pop())
        print(f"\nYour new card:", player_cards[-1])
        update_hand_values()
        print("Hand value:", player_hand_value)

        time.sleep(1)

        if player_busts():
            print("\nYou bust!")
            if first_split_hand == []:
                print("Round over.")
                ask_play_again()
            else:
               first_hand_final_value = 0
               second_hand_in_split()
        else:
            player_turn()

    # If 'stay', dealer takes their turn.
    elif action == "stay" or action == "s":
        if first_split_hand != []:
            first_hand_final_value = player_hand_value
            second_hand_in_split()
        else:
            dealer_turn()

    # If 'double', split player's hand into two separate hands, each hand with one of the original dealt cards. Add a new card to each hand and update point values.
    # When 'double' is active, ask 'hit', 'stay', or 'double' (if they have two of the same card on either hand)
    elif action == "double" or action == "d":
        if len(player_cards) == 2 and bank >= bet:
            bank -= bet
            bet *= 2
            print("\nDoubling down...")
            time.sleep(1)
            update_bank_and_bet()
            player_cards.append(deck.pop())
            print(f"\nYour new card:", player_cards[-1])
            update_hand_values()
            print("Hand value:", player_hand_value)

            time.sleep(1)

            if player_busts():
                print("\nYou bust!")
                if first_split_hand == []:
                    print("Round over.")
                    ask_play_again()
                else:
                    second_hand_in_split()

        else:
            print(
                "You can't double down. You either don't have enough money or you don't have two cards."
            )
            player_turn()

    elif action == "split" or action == "sp":
        split()

    else:
        print("Invalid action entered. Try again.")
        player_turn()


def split():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand
    if (
        len(player_cards) == 2
        and cards[player_cards[0]] == cards[player_cards[1]]
        and bank >= bet
    ):
        bank -= bet
        print("\nSplitting your hand...")
        time.sleep(1)
        update_bank_and_bet()
        first_split_hand = [player_cards[0], deck.pop()]
        second_split_hand = [player_cards[1], deck.pop()]
        print(f"\nYour first hand:", first_split_hand)
        print(f"Your second hand:", second_split_hand)

        # Play first hand
        player_cards = first_split_hand
        update_hand_values()
        print("\nFor the first hand:")
        print("Hand value:", player_hand_value)
        player_turn()

    else:
        print(
            "You can't split. You either don't have two of the same card or you don't have enough money."
        )
        player_turn()


def second_hand_in_split():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand, first_hand_final_value
    print("\nMoving on to your second hand...")
    player_cards = second_split_hand
    first_split_hand = []
    update_hand_values()
    print(f"\nYour second hand:", player_cards)
    print("Hand value:", player_hand_value)
    time.sleep(1)
    player_turn()


def dealer_turn():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand
    # DEALER'S TURN:
    # Turn the face-down dealer's card over and update total dealer's point value.
    # If dealer's point value is less than 17, deal another card and add it to the point value.
    # If dealer's point value is equal to 17 but less than 22, check dealer's point value against player's. Highest point value wins the game.
    # If dealer's point value is higher than 21, dealer busts and player wins.

    print("Turning over dealer's face-down card...")
    time.sleep(1)
    print(f"\nAnd the card is...", end=" ")
    print(f"a {dealer_cards[-1]},")
    print("Dealer's hand value:", dealer_hand_value)

    while dealer_hand_value < 17:
        time.sleep(1.5)
        dealer_cards.append(deck.pop())
        update_hand_values()
        print(f"\nDealt new card:", dealer_cards[-1])
        print("Dealer's hand value:", dealer_hand_value)
    else:
        settle()


def player_busts():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand
    time.sleep(1.5)
    if player_hand_value > 21:
        return True
    else:
        return False

def dealer_blackjack_check():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand
    if dealer_hand_value == 21 and player_hand_value != 21:
        print("\nDealer has Blackjack! You automatically lose.")
        update_bank_and_bet()
        ask_play_again()
    elif dealer_hand_value == 21 and player_hand_value == 21:
        print("\nDealer has Blackjack and you have Blackjack! It's a push.")
        update_bank_and_bet()
        ask_play_again()
    else:
        pass


def settle():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand
    time.sleep(1.5)

 # --- SETTLE SECOND HAND (or the only hand if no split occurred) ---
    winner(player_hand_value)

    # --- SETTLE FIRST HAND (only if a split actually happened) ---
    if first_hand_final_value is not None:
        print("\nSettling first split hand...")
        winner(first_hand_final_value)

    update_bank_and_bet()
    ask_play_again()

def winner(hand_value):
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand
    time.sleep(0.5)

    if hand_value == 0:
        print("\nYou bust on this hand!")
        return

    if not player_busts() and dealer_hand_value > 21:
        bank += bet * 2
        print("\nDealer busts! You win!")


    elif (
        not player_busts()
        and dealer_hand_value < 22
        and dealer_hand_value > hand_value
    ):
        print("\nDealer wins. Better luck next time.")


    # If player wins, add bet x2 to player's bank
    elif dealer_hand_value < 22 and dealer_hand_value < hand_value:
        bank += bet * 2
        print("\nYou win!")


    elif dealer_hand_value == hand_value:
        bank += bet
        print("\nIt's a push! You and the dealer tied.")


def update_hand_values():
    global player_hand_value, dealer_hand_value
    player_hand_value = sum(cards[card] for card in player_cards)
    dealer_hand_value = sum(cards[card] for card in dealer_cards)

    # If the player has any number of Aces and their hand value is over 21, subtract 10 from their hand value to account for the Ace being worth 1 instead of 11.
    for card in player_cards:
        if card.startswith("Ace") and player_hand_value > 21:
            player_hand_value -= 10

    # Do the same thing for the dealer's hand value.
    for card in dealer_cards:
        if card.startswith("Ace") and dealer_hand_value > 21:
            dealer_hand_value -= 10


def update_bank_and_bet():
    global bank_formatted
    bank_formatted = locale.currency(bank, grouping=True)
    time.sleep(0.5)
    print("\nYour current balance is: " + str(bank_formatted))


def insurance():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand
    if dealer_cards[0].startswith("Ace"):
        print(
            "\nThe dealer's face-up card is an Ace. You can take insurance of about half your bet ($"
            + str(bet / 2)
            + ")."
        )
        time.sleep(1)
        answer = input("Do you want to take insurance? [Y|N]: ").lower()

        if answer == "yes" or answer == "y":
            insurance_bet = bet / 2
            if bank >= insurance_bet:
                bank -= insurance_bet
                print("\nTaking insurance...")
                time.sleep(1)
                update_bank_and_bet()
                print("\nChecking if dealer has Blackjack...")
                time.sleep(1)
                if dealer_hand_value == 21:
                    print(
                        "\nDealer has Blackjack! You win the insurance bet, but lose your original bet."
                    )
                    bank += insurance_bet * 3
                    update_bank_and_bet()
                    ask_play_again()
                else:
                    print(
                        "\nDealer does not have Blackjack. You lose the insurance bet. Let's continue."
                    )
                    update_bank_and_bet()
                    player_turn()
            else:
                print("You don't have enough money to take insurance.")
                player_turn()
        elif answer == "no" or answer == "n":
            if dealer_hand_value == 21:
                print("\nDealer has Blackjack! You lose.")
                update_bank_and_bet()
                ask_play_again()
            else:
                print("\nDealer does not have Blackjack. Let's continue playing.")
                player_turn()
        else:
            print("Invalid answer. Please try again.")
            insurance()

    else:
        pass


def ask_play_again():
    global bank, bank_formatted, bet, deck, player_cards, dealer_cards, player_hand_value, dealer_hand_value, first_split_hand, second_split_hand
    time.sleep(1.5)
    answer = input("Want to play again? [Y|N]: ").lower()

    if answer == "yes" or answer == "y":
        player_cards = []
        dealer_cards = []
        first_split_hand = []
        second_split_hand = []
        deck = list(cards.keys())
        start_and_deal()
    elif answer == "no" or answer == "n":
        print("Thanks for playing!")
        print("Your final balance is: " + str(bank_formatted))
        exit()
    else:
        print("Invalid answer. Please try again.")
        ask_play_again()

intro()
