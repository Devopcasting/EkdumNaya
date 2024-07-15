import re
class PancardPattern1:
    def __init__(self, coordinate_data: list, text_data_list: list, logger: object) -> None:
        self.coordinates = coordinate_data
        self.text_data_list = text_data_list
        self.logger = logger
        # Skip Keywords
        self.skip_keywords = [
            r"\b\w*(name|uiname|mame|nun|alatar|fname|hehe|itiame)\b",
            r"\b\w*(father['’]s|father|eather['’]s|fathar['’]s|fathers|ffatugr|ffatubr['’]s)\b",
            r"\b\w*(hratlifies|facer|pacers|hratlieies|name|gather)\b",
            r"(=)"]
            
    
    def get_name(self) -> dict:
        try:
            # Search Keywords
            name_keyword = [r"\b\w*(name|uiname|mame|nun|fname|hehe|itiame)\b"]

            # Break Loop Keywords
            break_loop_keywords = [
                r"\b\w*(father['’]s|father|eather['’]s|fathar['’]s|fathers|ffatugr|ffatubr['’]s)\b",
                r"\b\w*(hratlifies|facer|pacers|hratlieies|gather|eaters)\b"]

            name_keyword_index = 0
            name = ""
            name_list = []
            coordinates = []
            name_coordinates = []
            width = 0

            # Find the name keyword index
            for index,text in enumerate(self.text_data_list):
                for pattern in name_keyword:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        name_keyword_index = index
                        break
                if name_keyword_index:
                    break
            
            # Check if name keyword is not found
            if name_keyword_index == 0:
                self.logger.warning("| Name keyword not found in Pancard document")
                return {"names": "", "coordinates": []}
            
            # Loop through the text data list starting from the name keyword index
            for index,text in enumerate(self.text_data_list[name_keyword_index + 1:]):
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
                # Check if text does'nt match the skip keywords
                if not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in self.skip_keywords):
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
            # Search Keywords
            father_name_keywords = [
                r"\b\w*(father['’]s|father|eather['’]s|fathar['’]s|fathers|ffatugr|ffatubr['’]s)\b",
                r"\b\w*(hratlifies|facer|pacers|hratlieies|gather|eaters)\b"]
            
            # Break Loop Keywords
            break_loop_keywords = [r"\b(date|da|rte|saan|of|birth)\b"]

            father_name_keyword_index = 0
            father_name = ""
            father_name_list = []
            father_name_coordinates = []
            coordinates = []
            width = 0

            # Find the father name keyword index
            for index,text in enumerate(self.text_data_list):
                for pattern in father_name_keywords:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        father_name_keyword_index = index
                        break
                if father_name_keyword_index:
                    break
            
            # Check if father name keyword is not found
            if father_name_keyword_index == 0:
                self.logger.warning("| Father's Name keyword not found in Pancard document")
                return {"names": "", "coordinates": []}
            
            # Loop through the text data list starting from the father name keyword index
            for index,text in enumerate(self.text_data_list[father_name_keyword_index + 1:]):
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
                # Check if text does'nt match the skip keywords
                if not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in self.skip_keywords) and not text.isdigit():
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
            self.logger.error(f"| Error while extracting Pancard Father's Name: {e}")
            return {"names": "", "coordinates": []}