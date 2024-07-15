import re
class PancardPattern2:
    def __init__(self, coordinate_data: list, text_data_list: list, logger: object) -> None:
        self.coordinates = coordinate_data
        self.text_data_list = text_data_list
        print(self.text_data_list)
        self.logger = logger
    
    def get_name(self):
        try:
            # Search Keywords
            search_keyword = [r"\b\w*(GOVTOF INDE|fETAX DEPARTMEN|fETAX|GoyT  OF UNPIA|OF INDIA|GOVT. OF INDIA|GOVT.|INDIA|INCOME|TAX|DEPARTMENT|DEPARTNENT|INCOME TAX DEPARTNENT)\b"]

            # Skip keywords
            skip_keywords = [r"\b(sizer|feat|ana|uae|income|tax|department|departmen|indi|my|arg|fears|india|[0-9])\b",
                        r"\b(govt|goty|sree|feast|ofl|goyt|os|xe|ar|umdi|es|set|oe|oome|iid|fetax|incometaxdepartment|tincome|of|si|ali|[0-9])\b",
                        r"\b(pras|ta|ag|oreax|fart|mic|ncome|are|art|we|gove|tere|sittex|[0-9])\b"]

            # Break Loop Keywords
            break_loop_keywords = [r"\b(4d|i|are|permanent|ermanent|account|nun|number|ali)\b"]

            search_keyword_index = 0
            name = ""
            name_list = []
            coordinates = []
            name_coordinates = []
            width = 0

            # Find the name keyword index
            for index,text in enumerate(self.text_data_list):
                for pattern in search_keyword:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        search_keyword_index = index
                        break
                if search_keyword_index != 0:
                    break
            
            # Check if search keyword is not found
            if search_keyword_index == 0:
                self.logger.warning("| Search keyword not found in Pancard document")
                return {"names": "", "coordinates": []}

            # Loop through the text data list starting from the name keyword index
            for index,text in enumerate(self.text_data_list[search_keyword_index + 1:]):
                # Check for the break loop
                break_loop_match_found = False
                for pattern in break_loop_keywords:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    if re.search(compiled_pattern, text):
                        break_loop_match_found = True
                        break
                # Check if break loop is matched
                if break_loop_match_found:
                    break
                # Check if text not in skip keyword
                if not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in skip_keywords):
                    name += " "+ text
                
            # Check if name is not found
            if not name:
                self.logger.warning("| Name not found in Pancard document")
                return {"names": "", "coordinates": []}
            
            # Split the name and update the name list
            name_list = name.strip().split()

            # Loop through the list of coordinates
            for index,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if text in name_list:
                    name_coordinates.append([x1, y1, x2, y2])
            # Update the coordinates
            for i in name_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])
            return {
                "names": " ".join(name_list),
                "coordinates": coordinates
            }
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Names: {e}")
            return {"names": "", "coordinates": []}

    def get_father_name(self):
        try:
            # Search Date pattern keyword
            date_pattern = [r'(?:(?:0?[1-9]|[12][0-9]|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:19\d\d|20\d\d|\d{4}))|(?:(?:19\d\d|20\d\d|\d{4})[-/.](?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12][0-9]|3[01]))|(?:(?:0?[1-9]|1[0-2])[-/.](?:19\d\d|20\d\d|\d{4}))|(?:(?:19\d\d|20\d\d|\d{4})[-/]\d{3})']

            #date_pattern = [r'(?:(?:0?[1-9]|[12][0-9]|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:19\d\d|20\d\d))|(?:(?:19\d\d|20\d\d)[-/.](?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12][0-9]|3[01]))|(?:(?:0?[1-9]|1[0-2])[-/.](?:19\d\d|20\d\d))|(?:(?:19\d\d|20\d\d)[-/]\d{3})']
            #date_pattern = [r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}|\d{1}/\d{2}/\d{4}']
            # Search Date keyword
            search_keyword = [r"\b\w*(bonn|birth)\b"]
            # Break loop keywords
            break_loop_keywords = [r"\b(india|tax|department|are|permanent|ermanent|account|nun|number|ali)\b"]
            # Revese the text data list
            reversed_text_data_list = self.text_data_list[::-1]
            
            father_name_keyword_index = 0
            father_name = ""
            father_name_list = []
            father_name_coordinates = []
            coordinates = []
            width = 0

            # Find the father name keyword index
            for index,text in enumerate(reversed_text_data_list):
                for pattern in date_pattern:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        father_name_keyword_index = index
                        break
                if father_name_keyword_index != 0:
                    break
            
            # Check if father name keyword is not found
            if father_name_keyword_index == 0:
                # Check if father name keywowrd index is available in search keyword
                for index,text in enumerate(reversed_text_data_list):
                    for pattern in search_keyword:
                        if re.search(pattern, text, flags=re.IGNORECASE):
                            father_name_keyword_index = index
                            break
                    if father_name_keyword_index != 0:
                        break
            if father_name_keyword_index == 0:
                self.logger.warning("| Father's Name keyword not found in Pancard document")
                return {"names": "", "coordinates": []}
            
            # Loop through the reversed text data list starting from the father name keyword index
            for index,text in enumerate(reversed_text_data_list[father_name_keyword_index + 1:]):
                # Check for the break loop
                break_loop_match_found = False
                for pattern in break_loop_keywords:
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    if re.search(compiled_pattern, text):
                        break_loop_match_found = True
                        break
                # Check if break loop is matched
                if break_loop_match_found:
                    break
                # Check if text not in skip keyword
                if not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in date_pattern):
                    father_name += " "+ text

            # Check if father name is not found
            if not father_name:
                self.logger.warning("| Father's Name not found in Pancard document")
                return {"names": "", "coordinates": []}
            
            # Split the father name and update the father name list
            father_name_list = father_name.strip().split()

            # Loop through the list of coordinates
            for index,(x1, y1, x2, y2, text) in enumerate(self.coordinates):
                if text in father_name_list:
                    father_name_coordinates.append([x1, y1, x2, y2])
            # Update the coordinates
            for i in father_name_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])
            return {
                "names": " ".join(father_name_list),
                "coordinates": coordinates
            }
        except Exception as e:
            self.logger.error(f"| Error while extracting Father's Name: {e}")
            return {"names": "", "coordinates": []}