# importing libraries
import entrezpy.esearch.esearcher
import entrezpy.efetch.efetcher
import os
import sys
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# XML download code
# search articles based on terms and filters
# reference - https://stackoverflow.com/questions/51390968/python-ssl-certificate-verify-error
# import ssl
#
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     # Legacy Python that doesn't verify HTTPS certificates by default
#     pass
# else:
#     # Handle target environment that doesn't support HTTPS verification
#     ssl._create_default_https_context = _create_unverified_https_context




def xml_extraction_query(start_date, end_date):
    """
    :param start_date:
    :param end_date:
    :return:
    """
    search = entrezpy.esearch.esearcher.Esearcher("entrezpy",
                                                  "srevolution23@gmail.com",
                                                  apikey="959aa974127d557c0a823891fc0aaa990f08")
    search_analyzer = search.inquire({'db': 'pmc',
                                      'term': 'open access[filter]',
                                      'rettype': 'count',
                                      'datetype': 'pdat',
                                      'mindate': start_date,
                                      'maxdate': end_date})

    start_date = "".join(start_date.split("/"))
    end_data = "".join(end_date.split("/"))
    query_dict = {'db': 'pmc',
                  'term': 'open access[filter]',
                  'rettype': 'count',
                  'datetype': 'pdat',
                  'mindate': start_date,
                  'maxdate': end_data}

    print(f'Search resulted in {search_analyzer.result.count} PMIDs')
    return search_analyzer, query_dict


def xml_download(search_analyzer, query_dict, start_pmid, end_pmid, pmids):
    """
    :param search_analyzer:
    :param query_dict:
    :param start_pmid:
    :param end_pmid:
    :param pmids:

    :return:
    """
    # retrieve article information
    output_folder = '../data/xml'
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    with open(f'{output_folder}/' + "pmc_" + query_dict['mindate'] + "_" + query_dict['maxdate'] + "_" + str(end_pmid) +
              '.xml', 'w') as sys.stdout:
        try:
            fetcher = entrezpy.efetch.efetcher.Efetcher("entrezpy",
                                                        "srevolution23@gmail.com",
                                                        apikey="959aa974127d557c0a823891fc0aaa990f08")
            fetcher.inquire({'db': 'pmc', 'retmode': 'xml', 'id': pmids[start_pmid: end_pmid], 'usehistory': True})
        except ValueError:
            pass
        sys.stdout.flush()



