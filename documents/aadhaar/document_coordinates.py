import pytesseract
import re
from PIL import Image
from qreader import QReader
from helper.text_coordinates import ImageTextCoordinates
from helper.places import places_list

class AadhaarDocumentInfo:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object, redaction_level: int) -> None:
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
        self.redaction_level = redaction_level

        self.coordinates = ImageTextCoordinates(self.ocrr_workspace_doc_path).generate_text_coordinates()
        self.lang_coordinates =ImageTextCoordinates(self.ocrr_workspace_doc_path, lang="regionalplus").generate_text_coordinates()
        # Tesseract configuration
        tesseract_config = r'--oem 3 --psm 11'
        tesseract_config_lang = r'--oem 3 --psm 11 -l hin+eng'
        self.text_data = pytesseract.image_to_string(self.ocrr_workspace_doc_path, lang="eng", config=tesseract_config)
        self.text_lang_data = pytesseract.image_to_string(self.ocrr_workspace_doc_path, lang="hin+eng", config=tesseract_config_lang)
        print(self.coordinates)
        # List of Places
        self.places = places_list

    # Method to extract Aadhaar Number and its Coordinates
    def _extract_aadhaar_number(self) -> dict:
        result = {"Aadhaar Number": "", "Coordinates": []}
        try:
            # Extract Aadhaar Number and its Coordinates
            aadhaar_number = ""
            aadhaar_number_coordinates = []
            coordinates = []
            width = 0

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text is of length 4 or 14 and is digit
                if (len(text) == 4 or len(text) == 14) and text.isdigit():
                    aadhaar_number += " "+ text
                    aadhaar_number_coordinates.append([x1, y1, x2, y2])
            
            # Check if Aadhaar Number is not found
            if not aadhaar_number:
                # Loop throgh the lang coordinates
                for x1, y1, x2, y2, text in self.lang_coordinates:
                    # Check if text is of length 4 or 14 and is digit
                    if (len(text) == 4 or len(text) == 14) and text.isdigit():
                        aadhaar_number += " "+ text
                        aadhaar_number_coordinates.append([x1, y1, x2, y2])
                if not aadhaar_number:
                    self.logger.error(f"| Unable to extract Aadhaar Number")
                    return result
            
            # Update the result
            for i in aadhaar_number_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])

            result = {
                "Aadhaar Number": aadhaar_number,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Number: {e}")
            return result

    # Method to extract Aadhaar Name and its Coordinates
    def _extract_aadhaar_name(self) -> dict:
        result = {"Aadhaar Name": "", "Coordinates": []}
        try:
            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_lang_data.split("\n") if len(text) != 0]

            # Reverse the filtered text data list
            reversed_text_data_list = text_data_list[::-1]
            print(f"REVERSED : {reversed_text_data_list}")

            # Search Gender Keywords
            gender_keyword = [r"\b(?:male|female|fmale|fale|femalp|femere|FEMALI|femala|mate|femate|#femste|fomale|fertale|malo|femsle|fade|ferme|famate)\b"]
            gender_keyword_index = 0

            # Skip keywords
            skip_keywords = [r"\b(dob|date|birth|address|india|dentification|tar|unique|authority|or|ae|oftndia|CGavernment)\b",
                             r"\b(tolindia|ser|binh|indie|ob|008|dow|coe|a|et|gove|oo|ss|poe|patos|तन|een|ex|oe|nx|पिल|nun|iie|yala|maes|pace|RRYOOB|भारत|सरकार|का)\b",
                             r"\b(ons|nt|x|reer|an|pee|ie|i|aoc|ee|OY|TIT|STINT|RAS|salad|कफ|फपफन|आपस|लक|फ|प्यक|aa)\b",
                             r"\b(leadi|Men|ros|Ft|ndia|gvernme|जन्म|fafa|s|Doe|Squemaioniaaare|aod|न|99|PaaS|nia|ea|ca|net|Src|rerp|ane|lace|tine)\b",
                             r"\b(aay|ra|tal|५०|52|69|82|race|aeeETa|nae|aS|menrrsens|ale|OVErAMe|itor|wera|birth|ly|teats|ange|peat)\b",
                             r"(=|का)",
                             r"\|",
                             r"&",
                             r"\)"]

            # Break loop keyword
            break_loop_keyword = [r"\b(address|india|dentification|unique|authority|or|ae)\b"]
            
            # Loop through the reversed text data list
            for index, text in enumerate(reversed_text_data_list):
                # Loop through the gender patterns
                for pattern in gender_keyword:
                    # Compile the pattern
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        gender_keyword_index = index
                        break
            
            # Check if gender keyword is found
            if not gender_keyword_index:
                self.logger.error("| Gender keyword index not found in Aadhaar document")
                return result
            
            name = ""
            name_list = []
            name_coordinates = []
            coordinates = []
            width = 0
            
            # Loop through the reversed text data list starting from gender keyword index
            for index, text in enumerate(reversed_text_data_list[gender_keyword_index + 1:]):
                # Check for break loop keyword
                # for keyword in break_loop_keyword:
                #     break_loop_keyword_found = False
                #     if re.match(keyword, text, flags=re.IGNORECASE):
                #         break_loop_keyword_found = True
                #         print(f"BREAK: {text}")
                #         break
                # if break_loop_keyword_found:
                #     break
                
                # Check not any skip keywords are matched
                if not any(re.search(keyword, text, flags=re.IGNORECASE) for keyword in skip_keywords):
                    name += " " + text
                
            # Check if name is not found
            if not name:
                self.logger.error("| Aadhaar Name not found in Aadhaar document")
                return result
            
            # Split the name into a list
            name_list = name.strip().split()

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.lang_coordinates:
                # Check if text is in name list
                if text in name_list:
                    name_coordinates.append([x1, y1, x2, y2])
            
            # Update the result
            for i in name_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.50 * width), i[3]])
            
            result = {
                "Aadhaar Name": name,
                "Coordinates": coordinates
            }
            print(result)
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Name: {e}")
            return result
    
    # Method to extract Aadhaar DOB and its Coordinates
    def _extract_aadhaar_dob(self) -> dict:
        result = {"Aadhaar DOB": "", "Coordinates": []}
        try:
            # Extract Aadhaar DOB and its Coordinates
            dob = ""
            dob_list = ""
            dob_coordinates = []
            coordinates = []
            width = 0

            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]

            # DOB Pattern: DD/MM/YYY, DD-MM-YYY
            #dob_pattern = r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2}|\d{4})\b'
            dob_pattern = r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b'
            #dob_pattern = r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}|\d{1}/\d{2}/\d{4}|\d{4}'
            #dob_pattern = r'\b\d{2}/\d{2}/\d{4}|\b\d{2}/\d{5}|\b\d{2}-\d{2}-\d{4}|\b\d{4}/\d{4}|\b\d{2}/\d{2}/\d{2}|\b\d{1}/\d{2}/\d{4}|\b[Oo]?\d{1}/\d{5}|\b\d{4}\b'
            
            # DOB Search keyword
            dob_search_keyword = r"\b\w*(dob|doe|rryoob|birth|bieth|binh|dor|dow|dod)\b"

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the DOB pattern
                if re.match(dob_pattern, text, flags=re.IGNORECASE):
                    dob += " "+ text
                    dob_coordinates.append([x1, y1, x2, y2])
            
            # Check if DOB is not found
            if not dob:
                # Loop through the text data
                for text in text_data_list:
                    # Check if text matches the DOB search keyword
                    if re.search(dob_search_keyword, text, flags=re.IGNORECASE):
                        dob += " "+ text
                        break
                
                # Split the dob
                dob_list = dob.split()
                # Remove '/' from dob list
                dob_list = [x for x in dob_list if x != '/']

                # Loop through the coordinates
                for x1, y1, x2, y2, text in self.coordinates:
                    # Check if text is in dob_list and not in coordinates
                    if text in dob_list and [x1, y1, x2, y2] not in dob_coordinates:
                        dob_coordinates.append([x1, y1, x2, y2])

            # Update the result
            for i in dob_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.80 * width), i[3]])
            result = {
                "Aadhaar DOB": dob,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar DOB: {e}")
            return result
    
    # Method to extarct Aadhaar Gender and its Coordinates
    def _extract_aadhaar_gender(self) -> dict:
        result = {"Aadhaar Gender": "", "Coordinates": []}
        try:
            # Extract Gender and its Coordinates
            gender = ""
            gender_list = []
            coordinates = []

            gender_pattern = [
                r"\b(?:male|female|fmale|femalp|fale|femere|FEMALI|femala|mate|femate|#femste|fomale|fertale|malo|femsle|fade|ferme|famate)\b"
            ]

            # Get the text data in a list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]

            # Loop through the text data
            for text in text_data_list:
                # Loop through the gender patterns
                for pattern in gender_pattern:
                    # Compile the pattern
                    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)
                    # Search for pattern in the text block
                    if re.search(compiled_pattern, text):
                        gender = text
                        break
            
            # Check if Gender is not found
            if not gender:
                self.logger.error("| Gender not found in Aadhaar document")
                return result
            
            # Split the gender text
            gender_list = gender.split()
            # Remove '/' from gender list
            gender_list = [x for x in gender_list if x != '/']

            # Get the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                if text in gender_list:
                    if [x1, y1, x2, y2] not in coordinates:
                        coordinates.append([x1, y1, x2, y2])

            # Update the result
            result = {
                "Aadhaar Gender": gender,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Gender: {e}")
            return result

    # Method to extract Aadhaar Address and its Coordinates
    def _extract_aadhaar_address(self) -> dict:
        result = {"Aadhaar Address": "", "Coordinates": []}
        try:
            address = ""
            coordinates = []

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Loop throgh list of places
                for place in self.places:
                    # Check if the text matches the place
                    if re.search(place, text, flags=re.IGNORECASE):
                        address += " " + text
                        coordinates.append([x1, y1, x2, y2])

            # Check if Address is not found
            if not address:
                self.logger.warning("| Address not found in Aadhaar document")
                return result
            
            # Update the result
            result = {
                "Aadhaar Address": address,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Address: {e}")
            return result
    
    # Method to extract Aadhaar Pincode and its Coordinates
    def _extract_aadhaar_pincode(self) -> dict:
        result = {"Aadhaar Pincode": "", "Coordinates": []}
        try:
            pincode = ""
            pincode_coordinates = []
            coordinates = []
            width = 0

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text length is 6 and text is a number
                if len(text) in (6,7) and text[:6].isdigit():
                    pincode += " "+ text
                    pincode_coordinates.append([x1, y1, x2, y2])

            # Check if Pincode is not found
            if not pincode:
                self.logger.error("| Pincode not found in Aadhaar document")
                return result
            
            # Update the result
            for i in pincode_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.30 * width), i[3]])

            result = {
                "Aadhaar Pincode": pincode,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Pincode: {e}")
            return result
    
    # Method to extract Aadhaar Mobile number and its Coordinates
    def _extract_aadhaar_mobile(self) -> dict:
        result = {"Aadhaar Mobile": "", "Coordinates": []}
        try:
            mobile = ""
            mobile_coordinates = []
            coordinates = []
            width = 0

            # Loop through the coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text length is 10 or 11
                if len(text) in (10,11) and text[:10].isdigit():
                    mobile = text
                    mobile_coordinates.append([x1, y1, x2, y2])
                
            # Check if Mobile is not found
            if not mobile:
                self.logger.warning("| Mobile number not found in Aadhaar document")
                return result
            
            # Update result
            for i in mobile_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.54 * width), i[3]])

            result = {
                "Aadhaar Mobile": mobile,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar Mobile: {e}")
            return result
    
    # Method to extract Aadhaar QR-Codes and its Coordinates
    def _extract_aadhaar_qr_codes(self) -> list:
        result = {"Aadhaar QRCodes": "", "Coordinates": []}
        try:
            # Initialize QRCode Reader
            qrreader = QReader()
    
            # Initialize list to store QRCode coordinates
            qrcodes_coordinates = []

            # Load the image
            image = Image.open(self.ocrr_workspace_doc_path)

            # Detect and Decode QR Codes
            qrcodes = qrreader.detect(image)

            # Check if qrcodes not found
            if not qrcodes:
                self.logger.error("| QR Codes not found in Aadhaar document")
                return result
            
            # Get the 50% of QR Codes
            for qr in qrcodes:
                x1, y1, x2, y2 = qr['bbox_xyxy']
                qrcodes_coordinates.append([int(round(x1)), int(round(y1)), int(round(x2)), (int(round(y1)) + int(round(y2))) // 2])

            # Update result
            result = {
                "Aadhaar QRCodes": f"Found {len(qrcodes_coordinates)} QR Code",
                "Coordinates": qrcodes_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Aadhaar QRCodes: {e}")
            return result

    # Method remove duplicate list of coordinates
    def _remove_duplicate_coordinates(self, coordinates: list) -> list:
        new_data = []
        for item in coordinates:
            seen = set()
            unique_coords = []
            for coord in item['Coordinates']:
                coord_tuple = tuple(coord)
                if coord_tuple not in seen:
                    unique_coords.append(coord)
                    seen.add(coord_tuple)
            item['Coordinates'] = unique_coords
            new_data.append(item)
        return new_data
    
    # Method to collect document information 
    def collect_document_info(self) -> list:
        document_info_list = []
        try:
            # Collect: Aadhaar Number
            aadhaar_number = self._extract_aadhaar_number()
            if len(aadhaar_number['Coordinates']) == 0:
                self.logger.error("| Aadhaar Number not found in Aadhaar document")
                return {"message": "Aadhaar Number not found in Aadhaar document", "status": "REJECTED"}
            document_info_list.append(aadhaar_number)

            # Collect: Aadhaar Name
            aadhaar_name = self._extract_aadhaar_name()
            if len(aadhaar_name['Coordinates']) == 0:
                self.logger.error("| Aadhaar Name not found in Aadhaar document")
                return {"message": "Aadhaar Name not found in Aadhaar document", "status": "REJECTED"}
            document_info_list.append(aadhaar_name)

            # Collect: Aadhaar Dates
            aadhaar_dates = self._extract_aadhaar_dob()
            if len(aadhaar_dates['Coordinates']) == 0:
                self.logger.error("| Aadhaar Dates not found in Aadhaar document")
                return {"message": "Aadhaar Dates not found in Aadhaar document", "status": "REJECTED"}
            document_info_list.append(aadhaar_dates)

            # Collect: Aadhaar Gender
            aadhaar_gender = self._extract_aadhaar_gender()
            if len(aadhaar_gender['Coordinates']) == 0:
                self.logger.error("| Aadhaar Gender not found in Aadhaar document")
                return {"message": "Aadhaar Gender not found in Aadhaar document", "status": "REJECTED"}
            document_info_list.append(aadhaar_gender)

            # Collect: Aadhaar Address
            aadhaar_address = self._extract_aadhaar_address()
            if len(aadhaar_address['Coordinates']) == 0:
                self.logger.warning("| Aadhaar Address not found in Aadhaar document")
            else:
                document_info_list.append(aadhaar_address)

            # Collect: Aadhaar Pincode
            aadhaar_pincode = self._extract_aadhaar_pincode()
            if len(aadhaar_pincode['Coordinates']) == 0:
                self.logger.warning("| Aadhaar Pincode not found in Aadhaar document")
            else:
                document_info_list.append(aadhaar_pincode)
            
            # Collect: Aadhaar Mobile
            aadhaar_mobile = self._extract_aadhaar_mobile()
            if len(aadhaar_mobile['Coordinates']) == 0:
                self.logger.warning("| Aadhaar Mobile not found in Aadhaar document")
            else:
                document_info_list.append(aadhaar_mobile)
            
            # Collect: Aadhaar QRCodes
            aadhaar_qrcodes = self._extract_aadhaar_qr_codes()
            if len(aadhaar_qrcodes['Coordinates']) == 0:
                self.logger.warning("| Aadhaar QRCodes not found in Aadhaar document")
            else:
                document_info_list.append(aadhaar_qrcodes)

            print(document_info_list)
            # Remove duplicate coordinates
            unique_document_info_list = self._remove_duplicate_coordinates(document_info_list)
            return {"message": "Successfully Processed Aadhaar Documment", "status": "REDACTED", "data": unique_document_info_list }
        except Exception as e:
            self.logger.error(f"| Error while collecting Aadhaar document information: {e}")
            return {"message": "Error in collecting Aadhaar Document Information", "status": "REJECTED"}