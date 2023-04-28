# importing required libraries
import pandas as pd
import numpy as np
import os
import lxml
import csv
from bs4 import BeautifulSoup as bs
import re
import PubMed_API_XML_Retrieval
import entrezpy.esearch.esearcher
import entrezpy.efetch.efetcher
import math
import json
import os
import sys
import time


def extract_tags(xml_papers) -> list:
    result = []
    art_title, pmc_id, doi, acklge, acknowledgement, funding, fn_statement = "NA", "NA", "NA", "NA", "NA", "NA", "NA"
    for paper in xml_papers:

        # getting pmc article title
        if len(paper.find_all('article-title')) > 0:
            art_title = paper.find_all('article-title')[0].text
        else:
            art_title = paper.find_all('journal-title')[0].text
        # print(art_title)

        # getting pmc & doi
        meta = paper.find_all("article-meta")
        art_ids = meta[0].find_all("article-id")

        for ids in art_ids:
            id_ = ids.attrs

            if id_['pub-id-type'] == 'pmc':
                pmc_id = ids.text
                # print(ids.text)

            if id_['pub-id-type'] == 'doi':
                doi = ids.text
                # print(doi)
            else:
                doi = 'na'

        # Funding Information from acknowledgement <ack> tag
        ack_tag = paper.find_all("ack")  # attrs
        if len(ack_tag) == 0:
            acklge = 'NA'
        else:
            for tag in ack_tag:
                if tag.find_next().name == 'p':
                    acklge = tag.find_next("p").text
                    break
                else:
                    acklge = 'NA'

        title = paper.find_all("title")
        if len(title) == 0:
            acknowledgement = 'NA'
            funding = 'NA'
        else:
            # Funding Information from <title> tag
            for t in title:
                pattern = t.text.lower()
                matched = re.match("funding:? ?[A-Z a-z]*", pattern)
                is_matched = bool(matched)
                if is_matched:
                    funding = t.find_next("p").text
                    break
                else:
                    funding = 'NA'

            # Acknowledgement Information from <title> tag
            for t in title:
                pattern = t.text.lower()
                matched = re.match("acknowledge?ments?:?", pattern)
                is_matched = bool(matched)
                if is_matched:
                    acknowledgement = t.find_next("p").text
                    break
                else:
                    acknowledgement = 'NA'

        # Funding Information from the footnotes section
        fn = paper.find("fn-group")  # attrs
        if fn is None:
            fn_statement = "NA"
        else:
            temp = fn.find("fn", {"fn-type": "supported-by"})
            if temp is None:
                fn_statement = "NA"
            else:
                fn_statement = temp.text

        result.append([art_title, pmc_id, doi, acklge, acknowledgement, funding, fn_statement])
    funding_dataframe = pd.DataFrame(result)
    funding_dataframe.columns = ['Article_Title', 'PMC_ID', 'DOI', 'ACK', 'ACKNOWLEDGEMENT', 'FUNDING', 'FOOTNOTES']
    funding_dataframe = funding_dataframe.set_index(['Article_Title'])
    return funding_dataframe


def save_file(out_filename: str, dataframe) -> csv:
    """
    It writes list output as 'csv' file in the current directory

    out_filename:   the name that will be give of the output file
    input_item:   processed data in list.
    """

    if os.path.isfile(out_filename):
        os.remove(out_filename)
        print("File has been deleted")
    else:
        print("File does not exist")
    dataframe.to_csv(out_filename)


if __name__ == '__main__':
    # xml file manual download
    mode = input("Enter mode: ")
    print(mode)
    if mode == 'pilot':
        xml_path = "../data/xml_manual"
        xml_files = os.listdir(xml_path)
        xml_files = [ele for ele in xml_files if ele.split("_")[0] == "pmc"]
        for ele in xml_files:
            with open(os.path.join(xml_path, ele), encoding='utf-8') as input_file:
                contents = input_file.read()

                # embedding the XML with beautiful soup module

                soup = bs(contents, 'xml')

                # extracts of the article units
                xml_papers = soup.find_all("article")
                annotated_dataframe = extract_tags(xml_papers)

                # name the processed output file
                out_filename = "../data/ack_data_pilot/ack_data_" + ele.split("_")[-1].split(".")[0] + ".csv"

                # save the processed file into csv
                save_file(out_filename, annotated_dataframe)
    if mode == 'main':

        # downloading the xml files
        start_date = '2022/01/01'
        end_date = '2022/02/01'
        search_analyzer, query_dict = PubMed_API_XML_Retrieval.xml_extraction_query(start_date, end_date)

        pmids = search_analyzer.result.uids
        retmax = 100  # maximum PMIDs per request
        xml_file_counter = 0
        for i in range(math.ceil(len(pmids) / retmax)):

            PubMed_API_XML_Retrieval.xml_download(search_analyzer, query_dict, i * retmax, i * retmax + retmax, pmids)
            time.sleep(5)
            xml_file_counter += 1
            # resetting the standard input output operation
            sys.stdout = sys.__stdout__
            # extracting funding statements from xml files
            xml_path = "../data/xml"
            xml_files = os.listdir(xml_path)
            xml_files = [ele for ele in xml_files if ele.split("_")[0] == "pmc"]
            with open(os.path.join(xml_path, xml_files[0]), encoding ='utf-8') as input_file:
                contents = input_file.read()

                # embedding the XML with beautiful soup module

                soup = bs(contents, 'xml')

                # extracts of the article units
                xml_papers = soup.find_all("article")
                annotated_dataframe = extract_tags(xml_papers)

                # name the processed output file
                out_filename = "../data/ack_data/ack_data" + xml_files[0].split("_")[-1] + ".csv"

                # save the processed file into csv
                save_file(out_filename, annotated_dataframe)
            os.remove(os.path.join(xml_path, xml_files[0]))
