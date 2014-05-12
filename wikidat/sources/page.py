# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 22:14:09 2014

@author: jfelipe
"""
import time
from data_item import DataItem


class Page(DataItem):
    """
    Models Page elements in Wikipedia database dumps
    """

    def __init__(self, data_dict={}, lang=None):
        """
        Constructor method for Page objects. Must forward params to
        parent class DataItem (mandatory inheritance)

        Parameters
        ----------
        data_dict: dictionary of raw data to be processed
        lang: identifier of Wikipedia language edition from which this
        element comes from (e.g. frwiki, eswiki, dewiki...)

        self.data_dict
        ---------
        * id: Unique numeric identifier for this page
        * ns: Namespace code for this page (0 is main)
        * title: Page title (unicode string)
        * restrictions: List of applicable restrictions to this page
        """
        super(Page, self).__init__(data_dict=data_dict, lang=lang)

    def process(self, pages_iter):
        """
        Class method that processes an iterator of Page objects and yields
        unicode tuples to be appended to an extended insert for DB storage
        """
        # Build component for extended insert with info about this Page
        for page in pages_iter:
            new_page_insert = "".join(["(", page.data_dict['id'], ",",
                                       page.data_dict['ns'], ",'",
                                       page.data_dict['title'].
                                       replace("\\", "\\\\").
                                       replace("'", "\\'").
                                       replace('"', '\\"'), "',"])
            if 'restrictions' in page.data_dict:
                new_page_insert = "".join([new_page_insert,
                                           "'", page.data_dict['restrictions'],
                                           "')"])
            else:
                new_page_insert = "".join([new_page_insert, "'')"])

            yield new_page_insert

    def store_db(self, pages_iter, con=None, size_cache=200):
        """
        Class method, processor to insert Page info in DB

        Arguments:
        ----------
        pages_iter = iterator over Page elements to be stored in DB
        """
        page_insert_rows = 0
        total_pages = 0

        print "Starting data loading at %s." % (
            time.strftime("%Y-%m-%d %H:%M:%S %Z",
                          time.localtime()))

        for new_page_insert in pages_iter:
            # Build extended insert for Page objects
            if page_insert_rows == 0:
                page_insert = "".join(["INSERT INTO page ",
                                       "VALUES", new_page_insert])
                page_insert_rows += 1

            elif page_insert_rows <= size_cache:
                page_insert = "".join([page_insert, ",",
                                       new_page_insert])
                # Update rows counter
                page_insert_rows += 1
            else:
                con.send_query(page_insert)

                page_insert = "".join(["INSERT INTO page ",
                                       "VALUES", new_page_insert])
                # Update rows counter
                page_insert_rows = 1

            total_pages += 1
            #if total_pages % 1000 == 0:
                #print "%s pages processed %s." % (total_pages,
                        #time.strftime("%Y-%m-%d %H:%M:%S %Z",
                                      #time.localtime()) )

        # Send last extended insert for page
        con.send_query(page_insert)
        print "END: %s pages processed %s." % (
            total_pages, time.strftime("%Y-%m-%d %H:%M:%S %Z",
                                       time.localtime()))