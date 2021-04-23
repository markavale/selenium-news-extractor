import json, re
from pprint import pprint

class Obj:
        def __init__(self, first_name, last_name, middle_name):
            self.first_name = first_name
            self.last_name = last_name
            self.middle_name = middle_name

        def main(self):
            print(f"BEFORE: {self.last_name}, {self.first_name} {self.middle_name}")
            self.callback(
                new_first_name = "Mark Anthony",
                new_last_name  = "Vale"
                # new_middle_name key => not using here
            )

        def callback(self, **kwargs):
            self.first_name         = kwargs.get('new_first_name')
            self.last_name          = kwargs.get('new_last_name')

            # Set a default value if new_middle_name key is missing in parameters when self.callback is being call
            self.middle_name        = kwargs.get('new_middle_name', "Not Foo")

            print(f"AFTER: {self.last_name}, {self.first_name} {self.middle_name}")
    
def extract_date(url):
    date = re.findall(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url)
    if date == [] or date is None:
        return None
    else:
        return date[0]
    
    


if __name__ == "__main__":
    # obj = Obj(first_name="John", last_name="Doe", middle_name="Foo")
    # print(obj.main())

    # with open('test-data/mmi-data.json') as f:
    #     mmi_data = json.loads(f.read())
    # pprint(mmi_data[0]['_id'])
    url1= "https://www.washingtonpost.com/news/football-insider/wp/2016/09/02/odell-beckhams-fame-rests-on-one-stupid-little-ball-josh-norman-tells-author/32/3212/32/32/"
    date = extract_date(url1)
    print(len(date))