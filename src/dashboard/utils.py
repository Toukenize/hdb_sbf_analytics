def format_as_pc(s):
    return f'{s:.2%}'


def format_as_thousand_dollars(s):
    return f'$ {s}k'


def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_max = s == s.max()
    return ['background-color: #F63366; color: white; font-weight: bold'
            if v else '' for v in is_max]


def align_center(_s):
    return 'text-align: center'
