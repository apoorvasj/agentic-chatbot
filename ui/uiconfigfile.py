from configparser import ConfigParser
import os

class Config:
    def __init__(self, config_file="uiconfig.ini"):
        config_path = os.path.join(os.path.dirname(__file__), config_file)

        self.config= ConfigParser()

        #read the config file
        self.config.read(config_path)
    
    def get_llm_options(self):
        return self.config["DEFAULT"].get("LLM_OPTIONS").split(",")
    
    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE")
    
    def get_pdf_path(self):
        return self.config["DEFAULT"].get("TEMP_PDF_PATH")
    
if __name__=='__main__':
    cfg= Config()
    print(cfg.get_page_title())
    print(cfg.get_llm_options())