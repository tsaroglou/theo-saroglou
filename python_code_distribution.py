class SecondTaxRateVoting(Page):
    form_model = 'player'
    form_fields = ['adjustment_values']

    def is_displayed(player):
        return player.consent and not player.remove

    def vars_for_template(player: Player):
        current_player = player
        player_group_type = current_player.group_type

        # Get the players from the opposite group and filter out players with None test_score2
        opposite_group_players = sorted(
            [p for p in player.group.get_players() if
             p.group_type != player_group_type and p.field_maybe_none('test_score2') is not None],
            key=lambda p: p.field_maybe_none('test_score2')
        )

        num_bars = len(opposite_group_players)

        # Create the predefined distribution for the interactive graph (using integers from 0 to 15)


        return {
            'num_bars': num_bars  # Send the number of sliders needed
        }

    def before_next_page(player: Player, timeout_happened):
        # Handle adjustments only if there's no timeout
        if not timeout_happened:
            try:
                # Convert the comma-separated string back into a list of floats
                adjustment_values = [float(value) for value in player.adjustment_values.split(',')]
            except ValueError:
                player.participant.vars['adjustment_error'] = True
                return

            # Check if the length of adjustment values matches the number of players
            opposite_group_players = [p for p in player.group.get_players() if p.group_type != player.group_type]
            if len(adjustment_values) != len(opposite_group_players):
                player.participant.vars['adjustment_error'] = True
            else:
                player.participant.vars['adjustment_error'] = False

        # Handle the timeout scenario
        if timeout_happened:
            # Increment the timeout count stored in participant.vars
            player.timeout_count += 1

            # If the participant times out 3 times, mark them for exclusion
            if player.timeout_count >= 3:
                player.remove = True  # Mark player for removal
