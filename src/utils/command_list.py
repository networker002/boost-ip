from bs4 import BeautifulSoup

def get_command_list_text() -> list:
    with open("src/shared/fr/list.html", 'r') as f:
        ctx = f.read()

    bs = BeautifulSoup(ctx, "lxml")
    text_ctx = bs.find("ol").text.split()

    return text_ctx