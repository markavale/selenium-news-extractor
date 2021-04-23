from ..helpers import Compare, PubDateVariables, recursive_iterate

from bs4 import BeautifulSoup
from datetime import datetime
import datefinder, re, time, pytz

utc=pytz.UTC

class PublishDate:
    """
    Class to find Publish Date
        @params:
            html        -   news page source
    """

    def __init__(self, html: str):  
        """
        Initialize method
        """

        self.soup = BeautifulSoup(html, "html.parser")
        self.date = None

        #CLEAN DOM
        self.__clean_html()

        # SET UP DATA FOR DATE KEY COMPARISON
        self.pub_date_data = Compare(self.pub_date_variables.date_keys)
        
         # FIND ALL PROBABLE TAG FOR PUB DATE
        blocks = self.soup.find_all(map(lambda pub_date_variables : pub_date_variables, self.pub_date_variables.pub_date_tags))
        # print(blocks)
        probab_date = self.__iterate_tag(blocks)
        # print("---------------------------------")
        # print("Prob date",probab_date)
        if probab_date:            
            # FIND DATES IN STRING
            matches = datefinder.find_dates(str(probab_date)) # .replace(":", "")
            # GET MATCH IF LESS THAN DATE TODAY
            today = datetime.today()
            for match in matches:
                # print("Python global parser other match date", match)
                if match.year >= today.year -1 and match.year <= today.year: # Original | Prone to error
                    self.date = match
                    # print(match)
                    break
                else:
                    self.date = None
        else:
            self.date = None

        # # FIND ALL PROBABLE TAG FOR PUB DATE
        # for tag in self.pub_date_variables.pub_date_tags:
        #     blocks = self.soup.find_all(tag)
        #     # print()
        #     probab_date = self.__iterate_tag(blocks)

        #     if probab_date:
        #         # print("Probab_date true")
        #         # print(probab_date)
               
        #         # FIND DATES IN STRING
        #         matches = datefinder.find_dates(str(probab_date).replace(":", ""))
        #         # GET MATCH IF LESS THAN DATE TODAY
        #         today = datetime.today()
        #         for match in matches:
        #             # print("other match", match)
        #             if match.year >= today.year -1 and match.year <= today.year: # Original | Prone to error
        #                 self.date = match
        #                 print(match)
        #                 break
        #             else:
        #                 self.date = None
        #     else:
        #         pass

    def __iterate_tag(self, blocks):     
        """
        Iterates bs4 blocks to find probable author
        """
        # print(self.soup.find('time'))
        for block in blocks:
            # if block.name == "time":
            #     print(block.name)
            #     print(block.attrs.values())
            # print(block)
            # if block  == "time":
            #     print("match",block)
            # print(block)
            attr_values = block.attrs.values()   
            # print(attr_values)
            # print("prob date: ", attr_values)
            for attr_val in attr_values:
                # print("attrs_val", attr_val)
                # print("possible date: ",attr_val)
                if any([attr_val == "", not attr_val]):
                    continue

                if isinstance(attr_val, list):
                    final_list = recursive_iterate(attr_val)

                    for val in final_list:
                        result = self.pub_date_data.eval(val)

                        if result:
                            possible_date = block.text.strip().replace("\n", " ")
                            return possible_date

                    continue

                result = self.pub_date_data.eval(attr_val)

                if result:
                    possible_date = block.text.strip().replace("\n", " ")
                    return possible_date

    def __clean_html(self):
        """
        Clean up page source
        """
        self.pub_date_variables = PubDateVariables()

        # REMOVE UNRELATED TAGS
        for key in self.pub_date_variables.tags_for_decompose:
            for tag in self.soup.find_all(key):
                tag.decompose()
