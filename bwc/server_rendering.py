from bwc.objects import AreaFlag


def format_card(index, card):
    return f""" <span data-area_id="{card.area.id}" data-card_index="{index}" class='card-click' draggable='true' ondragstart='dragstart_handler(event)'\
onclick='do_submit(inspect({{}}, [\"{card.area.id}\", \"{index}\"]), \"auto inspect\");'>\
<span class=\"index\">[{index}]</span> <span class=\"card-title\">{card.name}</span></span>"""


def format_player(player_name):
    return f"<span class=\"playerName\">{player_name}</span>"


def format_score(score):
    return f"<span class=\"tag score {'negative-score' if score < 0 else 'non-negative-score'}\">({score} points)</span>"


def format_area_id(area):
    classes = "area"
    area_id = area.id

    if '.' in area_id:
        dot_loc = area_id.index('.')
        first = area_id[:dot_loc]
        second = area_id[dot_loc:]
        area_id = f'{format_player(first)}{second}'

    if AreaFlag.PLAY_AREA in area.flags:
        classes += " playArea"
    if AreaFlag.DRAW_AREA in area.flags:
        classes += " drawArea"
    if AreaFlag.HAND_AREA in area.flags:
        classes += " handArea"
    if AreaFlag.DISCARD_AREA in area.flags:
        classes += " discardArea"

    return f'<span data-area_id="{area.id}" class="{classes}">{area_id}</span>'


def format_area(engine, player, area):
    can_look, area_contents = engine.kernel.look_at(player, area)
    if can_look:
        output = f"{format_area_id(area)} "
        if AreaFlag.PLAY_AREA in area.flags:
            output += format_score(engine.kernel.score_area(area))
        else:
            output += "<span class=\"tag visible\">(visible)</span>"
        output += "\n"

        for i in range(len(area_contents)):
            card = area_contents[i]
            output += format_card(i + 1, card) + "\n"

        output = output[:-1]
    else:
        output = f"{format_area_id(area)} <span class=\"tag card-count\">({area_contents} cards)</span>"
    return f"<span ondrop='drop_handler(\"{area.id}\", event)' ondragover='dragover_handler(event)'>{output}</span>"
