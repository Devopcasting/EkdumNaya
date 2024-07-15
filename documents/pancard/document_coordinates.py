import pytesseract
import re
from PIL import Image
from qreader import QReader
from documents.pancard.pattern1 import PancardPattern1
from documents.pancard.pattern2 import PancardPattern2
from helper.text_coordinates import ImageTextCoordinates


class PancardDocumentInfo:
    def __init__(self, ocrr_workspace_doc_path: str, logger: object, redaction_level: int) -> None:
        self.ocrr_workspace_doc_path = ocrr_workspace_doc_path
        self.logger = logger
        self.coordinates = ImageTextCoordinates(self.ocrr_workspace_doc_path).generate_text_coordinates()
        # Tesseract configuration
        tesseract_config = r'--oem 3 --psm 11'
        self.text_data = pytesseract.image_to_string(self.ocrr_workspace_doc_path, lang="eng", config=tesseract_config)
        print(self.coordinates)
        # Pancard Pattern
        self.pancard_pattern_1 = [
            r"\b\w*(father['’]s|father|eather['’]s|fathar['’]s|fathers|ffatugr|ffatubr['’]s)\b",
            r"\b\w*(hratlifies|facer|pacers|hratlieies|gather)\b"
            ]   
        
    # Method to extract Pancard Number and its Coordinates
    def _extract_pancard_number(self) -> dict:
        result = {"Pancard Number": "", "Coordinates": []}
        try:
            # Extract Pancard Number and its Coordinates
            pancard_number = ""
            pancard_number_coordinates = []
            coordinates = []
            width = 0

            # Lambada function to check if any character in text is digit and alpha numeric
            is_digit_alpha_numeric = lambda x: any(char.isdigit() for char in x) and any(char.isalpha() for char in x)

            # Loop through all text coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                if len(text) in(7, 9, 10) and text.isupper() and is_digit_alpha_numeric(text):
                    pancard_number = text
                    pancard_number_coordinates.append([x1, y1, x2, y2])
            
            # Check if Pancard Number is not found
            if not pancard_number:
                self.logger.warning("| Pancard Number not found in Pancard document")
                return result
            
            # Update the result
            for i in pancard_number_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.80 * width), i[3]])
            result = {
                "Pancard Number": pancard_number,
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Number: {e}")
            return result
    
    # Method to extract Pancard DOB and its Coordinates
    def _extract_pancard_dob(self) -> dict:
        result = {"Pancard DOB": "", "Coordinates": []}
        try:
            # Extract Pancard DOB and its Coordinates
            dob = ""
            dob_coordinates = []
            coordinates = []
            width = 0

            dob_pattern = r'\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}|\d{4}-\d{4}|\d{4}/\d{4}|\d{2}/\d{2}/\d{2}|\d{1}/\d{2}/\d{4}'

            # Loop through all text coordinates
            for x1, y1, x2, y2, text in self.coordinates:
                # Check if text matches the DOB pattern
                if re.search(dob_pattern, text, flags=re.IGNORECASE):
                    dob += " "+ text
                    dob_coordinates.append([x1, y1, x2, y2])
            
            # Check if DOB is not found
            if not dob:
                self.logger.warning("| DOB not found in Pancard document")
                return result
            
            # Update the result
            for i in dob_coordinates:
                width = i[2] - i[0]
                coordinates.append([i[0], i[1], i[0] + int(0.70 * width), i[3]])
            result = {
                "Pancard DOB": dob.strip(),
                "Coordinates": coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard DOB: {e}")
            return result

    # Method to extract Pancard User Name
    def _extract_pancard_user_name(self) -> dict:
        result = {"Pancard User Name": "", "Coordinates": []}
        try:
            # Get the text from data list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]
            
            # Identify the Pancard Pattern
            pancard_pattern_1_found = False
            for text in text_data_list:
                for pattern in self.pancard_pattern_1:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        pancard_pattern_1_found = True
                        break
                if pancard_pattern_1_found:
                    break
            
            # Check if Pancard Pattern 1 is found
            if pancard_pattern_1_found:
                # Call the PancardPattern1 class
                pancard_pattern_1_obj = PancardPattern1(self.coordinates, text_data_list, self.logger)
                pancard_pattern_result = pancard_pattern_1_obj.get_name()
            else:
                # Call the PancardPattern2 class
                pancard_pattern_2_obj = PancardPattern2(self.coordinates, text_data_list, self.logger)
                pancard_pattern_result = pancard_pattern_2_obj.get_name()
            
            # Check if coordinates are not found
            if len(pancard_pattern_result["coordinates"]) == 0:
                self.logger.warning("| Pancard User Name not found in Pancard document")
                return result
            
            # Update the result
            result = {
                "Pancard User Name": pancard_pattern_result["names"],
                "Coordinates": pancard_pattern_result["coordinates"]
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard User Name: {e}")
            return result
    
    # Method to extract Father's name
    def _extract_father_name(self) -> dict:
        result = {"Pancard Father's Name": "", "Coordinates": []}
        try:
            # Get the text from data list
            text_data_list = [text.strip() for text in self.text_data.split("\n") if len(text) != 0]

            # Identify the Pancard Pattern
            pancard_pattern_1_found = False
            for text in text_data_list:
                for pattern in self.pancard_pattern_1:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        pancard_pattern_1_found = True
                        break
                if pancard_pattern_1_found:
                    break
            # Check if Pancard Pattern 1 is found
            if pancard_pattern_1_found:
                # Call the PancardPattern1 class
                pancard_pattern_1_obj = PancardPattern1(self.coordinates, text_data_list, self.logger)
                pancard_pattern_result = pancard_pattern_1_obj.get_father_name()
            else:
                # Call the PancardPattern2 class
                pancard_pattern_2_obj = PancardPattern2(self.coordinates, text_data_list, self.logger)
                pancard_pattern_result = pancard_pattern_2_obj.get_father_name()
            
            # Update the result
            result = {
                "Pancard Father's Name": pancard_pattern_result["names"],
                "Coordinates": pancard_pattern_result["coordinates"]
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard Father's Name: {e}")
            return result
    
    # Method to detect QR Codes in the document
    def _extract_qrcodes(self):
        result = {"Pancard QRCodes": "", "Coordinates": []}
        try:
            # Extract QR Codes coordinates from Pancard Document

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
                self.logger.error("| QR Codes not found in Pancard document")
                return result
            
            # Get the 50% of QR Codes
            for qr in qrcodes:
                x1, y1, x2, y2 = qr['bbox_xyxy']
                qrcodes_coordinates.append([int(round(x1)), int(round(y1)), int(round(x2)), (int(round(y1)) + int(round(y2))) // 2])

            # Update result
            result = {
                "Pancard QRCodes": f"Found {len(qrcodes_coordinates)} QR Code",
                "Coordinates": qrcodes_coordinates
            }
            return result
        except Exception as e:
            self.logger.error(f"| Error while extracting Pancard QRCodes: {e}")
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
            # Collect: Pancard Number
            pancard_number = self._extract_pancard_number()
            if len(pancard_number["Coordinates"]) == 0:
                self.logger.error("| Pancard Number not found in Pancard document")
                return {"message": "Pancard Number not found in Pancard document", "status": "REJECTED"}
            document_info_list.append(pancard_number)

            # Collect: Pancard DOB
            pancard_dob = self._extract_pancard_dob()
            if len(pancard_dob["Coordinates"]) == 0:
                self.logger.error("| DOB not found in Pancard document")
                return {"message": "DOB not found in Pancard document", "status": "REJECTED"}
            document_info_list.append(pancard_dob)

            # Collect: Pancard User Name
            pancard_user_name = self._extract_pancard_user_name()
            if len(pancard_user_name["Coordinates"]) == 0:
                self.logger.error("| Pancard User Name not found in Pancard document")
                return {"message": "Pancard User Name not found in Pancard document", "status": "REJECTED"}
            document_info_list.append(pancard_user_name)

            # Collect: Pancard Father's Name
            pancard_father_name = self._extract_father_name()
            if len(pancard_father_name["Coordinates"]) == 0:
                self.logger.error("| Pancard Father's Name not found in Pancard document")
                return {"message": "Pancard Father's Name not found in Pancard document", "status": "REJECTED"}
            document_info_list.append(pancard_father_name)
            
            # Collect: QR-Codes
            qrcodes = self._extract_qrcodes()
            if len(qrcodes["Coordinates"]) == 0:
                self.logger.error("| QR Codes not found in Pancard document")
            else:
                document_info_list.append(qrcodes)

            print(document_info_list)
            # Remove duplicate coordinates
            unique_document_info_list = self._remove_duplicate_coordinates(document_info_list)
            return {"message": "Successfully Processed Pancard Documment", "status": "REDACTED", "data": unique_document_info_list }
        except Exception as e:
            self.logger.error(f"| Error while collecting Pancard document information: {e}")
            return {"message": "Error in collecting Pancard Document Information", "status": "REJECTED"}