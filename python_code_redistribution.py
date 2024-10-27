class InteractiveGraph(Page):
    form_model = 'player'
    form_fields = ['tax_vote']

    def is_displayed(player):
        return player.consent and not player.remove

    def vars_for_template(player):
        current_player = player
        player_group_type = current_player.group_type
        player.percentage_ranking_100 = 100 - current_player.percentage_ranking * 100

        # Get players from the opposite group and filter out players with None in score2
        players = sorted(
            [p for p in player.group.get_players() if p.group_type != player_group_type and p.field_maybe_none('score2') is not None],
            key=lambda p: p.score2
        )

        # Now you are dealing with players who have a valid score2
        scores2 = [p.score2 for p in players]  # Raw scores to be used for bar heights and display
        id_in_group_list = [p.id_in_group for p in players]

        # Set player colors based on ranking
        for player in players:
            if player.percentage_ranking < 0.20:
                player.color = 'red_human.png'
            elif player.percentage_ranking < 0.40:
                player.color = 'yellow_human.png'
            elif player.percentage_ranking < 0.60:
                player.color = 'green_human.png'
            elif player.percentage_ranking < 0.80:
                player.color = 'orange_human.png'
            else:
                player.color = 'blue_human.png'

        player_colors = [f"/static/Test_Luck_Merit/Images/{p.color}" for p in players]

        # Calculate bar heights based on score2 (proportional to raw score)
        bar_heights = [score * 20 + 5 for score in scores2]  # Heights calculated based on score2
        rankings = [f"{(1 - p.percentage_ranking) * 100:.2f}%" for p in players]
        money_earned = [f"€{(score / 15) * 2.5:.2f}" for score in scores2]

        # Pass scores2 instead of percentage scores
        scores_and_colors = zip(scores2, player_colors, bar_heights, rankings, money_earned, id_in_group_list)

        return {
            'scores_and_colors': list(scores_and_colors),  # Convert zip to list
            'percentage_ranking_100': current_player.percentage_ranking_100,
            'participant_color': current_player.field_maybe_none('color') or 'default_icon.png',
            'specific_participant_id_in_group': current_player.id_in_group,
            'bin_index': player.get_rank_bin(),
            'all_histogram': [],  # Provide a default value for all_histogram
            'bins_labels': [str(i) for i in range(len(players))]  # Use indices as dummy labels
        }
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            # Increment the timeout count stored in participant.vars
            player.remove = True  # Mark player for removal

