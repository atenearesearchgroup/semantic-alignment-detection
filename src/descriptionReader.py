import re

description_file_path = "D:\\Thesis\\modelling-assistant\\tests\\actual-description\\"


def clean_text(text):
    if isinstance(text, str):
        text = text.encode("utf-8", "ignore").decode("utf-8")  # Remove badly encoded characters
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        return text
    return text


class DescriptionReader:
    def __init__(self, domain_name):
        self.actual_description = ""
        self.domain_name = domain_name

    def get_actual_description(self):
        with open(description_file_path + self.domain_name, 'r', encoding='utf-8') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)

        self.actual_description = local_vars.get('description', "")

        return clean_text(self.actual_description)
