#!/usr/bin/env python3

from queries.similarity import find_similar_to, find_clue_variants, load_clues, load_answers
from xdfile.utils import get_args, open_output, find_files, log, debug, get_log, COLUMN_SEPARATOR, EOL, parse_tsv, progress, parse_pathname
from xdfile.html import html_header, html_footer, th, td, mkhref, html_select_options
from xdfile import corpus, clues

from collections import Counter
import random

def answers_from(clueset):
    return [ ca.answer for ca in clueset ]

def maybe_multstr(n):
    return (n > 1) and ("[x%d]" % n) or ""

def unboil(bc):
    return random.choice(boiled_clues[bc]).clue

def pubyear_table(pubyears):
    pubs = {}
    for pubid, year in pubyears:
        if pubid not in pubs:
            pubs[pubid] = Counter()
        try:
            pubs[pubid][int(year)] += 1
        except:
            pass

    minyear = min(min(years.keys()) for pubid, years in pubs.items() if years)
    maxyear = max(max(years.keys()) for pubid, years in pubs.items() if years)

    ret = '<table class="pubyears">'

    ret += th('pub', *[ str(y)[2:] for y in range(minyear, maxyear+1) ])

    for pubid, years in sorted(pubs.items()):
        # TODO: indicate how many puzzles in the corpus by background-color
        #  groups: >=350 puzzles, >=50, >=12, >=1
        ret += td(pubid, *[(years[y] or "") for y in range(minyear, maxyear+1)])

    ret += '</table>'
    return ret

def year_from_date(dt):
    return dt.split('-')[0]

def mkwww_cluepage(bc):
    bcs = boiled_clues[bc]

    clue_html = ''
    clue_html += '<div>Variants: ' + html_select_options([ ca.clue for ca in bcs ]) + '</div>'
    clue_html += '<hr/>'
    clue_html += '<div>Answers for this clue: ' + html_select_options([ ca.answer for ca in bcs ]) + '</div>'
    clue_html += '<hr/>'
    clue_html += pubyear_table((ca.pubid, year_from_date(ca.date)) for ca in bcs)
    
    return clue_html 

def main():
    global boiled_clues
    args = get_args('create clue index')
    outf = open_output()

    boiled_clues = load_clues()

    biggest_clues = "<li>%d total clues, which boil down to %d distinct clues" % (len(clues()), len(boiled_clues))

    bcs = [ (len(v), bc, answers_from(v)) for bc, v in boiled_clues.items() ]

    nreused = len([bc for n, bc, _ in bcs if n > 1])
    biggest_clues += "<li>%d (%d%%) of these clues are used in more than one puzzle" % (nreused, nreused*100/len(boiled_clues))

    cluepages_to_make = set()

    biggest_clues += '<h2>Most used clues</h2>'

    biggest_clues += '<table class="clues most-used-clues">'
    biggest_clues += th("clue", "# uses", "answers used with this clue")
    for n, bc, ans in sorted(bcs, reverse=True)[:100]:
        cluepages_to_make.add(bc)
        biggest_clues += td(mkhref(unboil(bc), bc), n, html_select_options(ans))

    biggest_clues += '</table>'

    most_ambig = "<h2>Most ambiguous clues</h2>"
    most_ambig += '(clues with the largest number of different answers)'
    most_ambig += '<table class="clues most-different-answers">'
    most_ambig += th("Clue", "answers")

    for n, bc, ans in sorted(bcs, reverse=True, key=lambda x: len(set(x[2])))[:100]:
        cluepages_to_make.add(bc)
        clue = mkhref(unboil(bc), bc)
        if 'quip' in bc or 'quote' in bc or 'theme' in bc or 'riddle' in bc:
            most_ambig += td(clue, html_select_options(ans), rowclass="theme")
        else:
            most_ambig += td(clue, html_select_options(ans))

    most_ambig += '</table>'

    for bc in cluepages_to_make:
        outf.write_html('clue/%s/index.html' % bc, mkwww_cluepage(bc), title=bc)

    outf.write_html('clue/index.html', biggest_clues + most_ambig, title="Clues")
        
main()
