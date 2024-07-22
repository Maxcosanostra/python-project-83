from bs4 import BeautifulSoup


def parse_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    h1 = soup.find('h1').text if soup.find('h1') else None
    title = soup.title.string if soup.title else None
    description = None
    if soup.find('meta', attrs={'name': 'description'}):
        description = soup.find(
            'meta', attrs={'name': 'description'}
        )['content']
    return {
        'h1': h1,
        'title': title,
        'description': description,
    }
