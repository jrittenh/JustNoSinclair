# -*- encoding: utf-8 -*-
import re

import requests
from requests.exceptions import HTTPError
import retrying
from bs4 import BeautifulSoup


# this should grab just the domain portion (minus any www.) from the
# Google links
crappy_domain_regex = re.compile(r'^.*https?://(?:www\.)?(.+?)/.*$')


# some stations just seem to not have websites, but show up on these
# sites... compile them so we can filter them out
common_false_positives = [
    'logos.wikia.com',  # they keep logos for stations, even if the station doesn't have a site
    'stationindex.com',  # obvs, an index of all stations
    'businessinsider.com',  # they have an article detailing all Sinclair stations
    'en.wikipedia.org',  # I swear, these guys catalog EVERYTHING 😃
    'publicfiles.fcc.gov',  # turns out that the FCC keeps track of stations, whodathunkit
    'nocable.org',  #
    'wicd.sourceforge.net',  # weird edge-case where the station didn't have a domain, but something else shared an acronym
]


# for when search just can't figure it out...
manual_overrides = {
    'KBVU': None,
    'WOAI-TV': 'hoiabc.com',
    'WRDC': 'myrdctv.com',
}


def retry_test(exception):
    """
    Allows the retrying library to retry any HTTP errors.

    :param exception:
    :return:
    """
    return isinstance(exception, HTTPError)


@retrying.retry(retry_on_exception=retry_test)
def compile_stations_from_wikipedia():
    # grab the page from wikipedia
    wiki_page = requests.get('https://en.wikipedia.org/wiki/List_of_stations_owned_or_operated_by_Sinclair_Broadcast_Group')
    wiki_page.raise_for_status()

    # parse it and drill down to the table we care about (this should
    # continue to work okay as long as they don't restructure the page)
    soup = BeautifulSoup(wiki_page.text, 'html.parser')
    current_stations_table = soup.find(id="By_state_and_market").parent.find_next('table')

    # now, each table row should contain a station identifier in
    # either the first or second cell, let's grab those
    station_identifiers = []
    for row in current_stations_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 7:
            continue

        # choose which cell based on the total number in the tr
        # since "City of license / Market" uses a rowspan
        cell_we_want = cells[1] if len(cells) == 8 else cells[0]

        # okay, every station that isn't just a satellite of another
        # contains a link to a wikipage for it... look for that
        bold_tag = cell_we_want.find('b')
        if not bold_tag:
            continue
        link_tag = bold_tag.find('a')
        if link_tag:
            station_identifiers.append(link_tag.string)

    # get rid of any duplicates, sort it, then return
    station_identifiers = list(set(station_identifiers))
    station_identifiers.sort()
    return station_identifiers


@retrying.retry(retry_on_exception=retry_test, wait_exponential_multiplier=1000, wait_exponential_max=10000, wrap_exception=True)
def lookup_domain(station, include_extra=False):
    """
    Search for a domain... while making a lot of assumptions.

    Note: This incorporates an exponential backoff on failures,
    though I haven't seen any failures or rate limiting in testing.

    :param station:
    :param include_extra:
    :return:
    """

    print("Searching for: {}".format(station))

    # let's check the manual overrides first...
    if station in manual_overrides.keys():
        return manual_overrides[station]

    # make the search query
    query_string = 'https://www.google.com/search?q={}'.format(station)
    if include_extra:
        query_string += '%20TV%20Station'
    g_search = requests.get(query_string)
    g_search.raise_for_status()

    # parse the html
    soup = BeautifulSoup(g_search.text, 'html.parser')

    first_search_result = soup.find(id='search').find('a')
    match = re.match(crappy_domain_regex, first_search_result.get('href', ''))
    if match:
        # there were a few matching .edu domains that simply shared
        # an acronym, filter those out while seeing if we have a match
        if match.group(1) not in common_false_positives and not match.group(1).endswith('edu'):
            print("    {}".format(match.group(1)))
            return match.group(1)
        else:
            # sometimes adding "TV Station" to the query gives better
            # results... if we aren't already there, lets try that
            # before giving up
            if not include_extra:
                return lookup_domain(station, True)
            print("    Only false-positives found 😞")
            return
    else:
        print("    None Found, link href = {}".format(first_search_result.get('href', '')))
        return


if __name__ == "__main__":
    # get the list of stations from wikipedia then look each of them up
    domains = [lookup_domain(station) for station in compile_stations_from_wikipedia()]

    # people have already found some that this search doesn't find,
    # so load in the existing domains list before processing.
    with open('./sinclair_domains', 'r') as infile:
        for line in infile:
            print("Appending: {}".format(line.strip()))
            domains.append(line.strip())

    # get rid of any duplicates/Nones/etc then order them
    domains = list(set(domains))
    domains = [d for d in domains if d is not None and d != '']
    domains.sort()

    # and we're done, so let's write it to a file
    with open('./sinclair_domains_gen', 'w') as outfile:
        for domain in domains:
            outfile.write(domain + "\n")