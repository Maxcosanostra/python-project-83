from bs4 import BeautifulSoup


def parse_html(content):
    soup = BeautifulSoup(content, 'html.parser')

    h1_tag = soup.find('h1')
    title_tag = soup.title
    description_tag = soup.find('meta', attrs={'name': 'description'})

    return {
        'h1': h1_tag.text[:255] if h1_tag else '',
        'title': title_tag.text[:255] if title_tag else '',
        'description': (description_tag['content'][:255]
                        if description_tag else ''),
    }
